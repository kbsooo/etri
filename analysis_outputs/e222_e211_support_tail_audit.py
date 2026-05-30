#!/usr/bin/env python3
"""E222: hard-tail audit for live Q3/S4 JEPA candidates after the E216 miss.

E216 taught a new failure criterion: a JEPA movement can pass local OOF,
subject-half, geometry, bad-axis, and focus-expected checks, yet still be
public-adverse when its moved cells have weak hard-label support. This audit
uses E216 as a negative control and asks whether the still-live E211 Q3/S4
submission candidates have the same support/tail smell.

No submission is created here. The output is a risk audit for candidate order.
"""

from __future__ import annotations

from dataclasses import dataclass
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


N_PUBLIC_CELLS = 250 * len(TARGETS)
PUBLIC_READABLE_GUARD = 2.0e-6
E95_EDGE_OVER_MIXMIN = 0.0000153107
E95_PUBLIC = 0.5762913298
E216_PUBLIC = 0.5772865088
OBS_E216_MISS = E216_PUBLIC - E95_PUBLIC
EPS = 1.0e-12

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"

SUMMARY_OUT = OUT / "e222_e211_support_tail_audit_summary.csv"
TARGET_OUT = OUT / "e222_e211_support_tail_audit_targets.csv"
TOP_CELLS_OUT = OUT / "e222_e211_support_tail_audit_top_cells.csv"
REPORT_OUT = OUT / "e222_e211_support_tail_audit_report.md"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    file_name: str
    anchor_file: str
    family: str
    status: str
    note: str


CANDIDATES = [
    Candidate(
        "e211_e154_closer",
        "submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv",
        E154_FILE,
        "e211_q3s4",
        "live_primary",
        "Highest E212 structured-survival score; E154 anchor plus Q3 raw and S4 closer gate.",
    ),
    Candidate(
        "e211_e95_toward",
        "submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv",
        E95_FILE,
        "e211_q3s4",
        "live_clean_sensor",
        "Clean current-frontier JEPA sensor; E95 anchor plus Q3 raw and S4 toward gate.",
    ),
    Candidate(
        "e211_e95_closer",
        "submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv",
        E95_FILE,
        "e211_q3s4",
        "live_clean_sensor",
        "E95 anchor plus Q3 raw and S4 closer gate.",
    ),
    Candidate(
        "e209_e95_raw_control",
        "submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv",
        E95_FILE,
        "e209_q3s4_raw",
        "control",
        "Raw E209 Q3/S4 materialization on E95 at low scale.",
    ),
    Candidate(
        "e210_e95_dependency_gate",
        "submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv",
        E95_FILE,
        "e210_q3s4_dependency",
        "control",
        "Dependency-gated Q3/S4 control: stronger focus expectation but weaker local body/geometry.",
    ),
    Candidate(
        "e216_e154_s2_negative",
        "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        E154_FILE,
        "e216_s2_maskfam",
        "negative_public_control",
        "Submitted E216 S2 masked-family JEPA file; public miss is known.",
    ),
    Candidate(
        "e216_e95_s2_negative",
        "submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv",
        E95_FILE,
        "e216_s2_maskfam",
        "negative_unsubmitted_control",
        "E95-anchor sibling of the failed E216 S2 movement.",
    ),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def safe_weighted_mean(x: np.ndarray, w: np.ndarray) -> float:
    den = float(np.sum(w))
    if den <= EPS:
        return float("nan")
    return float(np.average(x, weights=w))


def top_sum(x: np.ndarray, k: int) -> float:
    arr = np.sort(np.asarray(x, dtype=np.float64).reshape(-1))[::-1]
    if len(arr) == 0:
        return 0.0
    return float(arr[:k].sum())


def summarize_cells(cells: pd.DataFrame, prefix: dict[str, Any]) -> dict[str, Any]:
    rec: dict[str, Any] = dict(prefix)
    if cells.empty:
        rec.update(
            {
                "moved_cells": 0,
                "moved_rows": 0,
                "targets_moved": "",
                "expected_focus": 0.0,
                "support_delta": 0.0,
                "adverse_delta": 0.0,
                "total_swing": 0.0,
                "top1_swing": 0.0,
                "top5_swing": 0.0,
                "top10_swing": 0.0,
                "top25_swing": 0.0,
                "top1_over_abs_expected": np.nan,
                "top5_over_abs_expected": np.nan,
                "top1_swing_share": np.nan,
                "top5_swing_share": np.nan,
                "support_prob_focus_mean": np.nan,
                "support_prob_focus_swing_weighted": np.nan,
                "adverse_over_e216_miss": np.nan,
                "cells_for_2e6_guard": -1,
                "cells_for_e95_edge": -1,
                "cells_to_flip_expected_focus": -1,
                "support_tail_gate": False,
            }
        )
        return rec

    swing = cells["swing"].to_numpy(dtype=np.float64)
    total_swing = float(swing.sum())
    expected_focus = float(cells["expected_focus"].sum())
    abs_expected = abs(expected_focus)
    rec.update(
        {
            "moved_cells": int(len(cells)),
            "moved_rows": int(cells["row_idx"].nunique()),
            "targets_moved": ",".join(TARGETS[j] for j in sorted(cells["target_idx"].unique())),
            "expected_focus": expected_focus,
            "expected_global": float(cells["expected_global"].sum()),
            "expected_subject": float(cells["expected_subject"].sum()),
            "expected_nearest_hard085": float(cells["expected_nearest_hard085"].sum()),
            "hard_delta_focus": float(cells["hard_delta_focus"].sum()),
            "support_delta": float(cells["support_delta"].sum()),
            "adverse_delta": float(cells["adverse_delta"].sum()),
            "total_swing": total_swing,
            "top1_swing": top_sum(swing, 1),
            "top5_swing": top_sum(swing, 5),
            "top10_swing": top_sum(swing, 10),
            "top25_swing": top_sum(swing, 25),
            "support_prob_focus_mean": float(cells["support_prob_focus"].mean()),
            "support_prob_focus_swing_weighted": safe_weighted_mean(
                cells["support_prob_focus"].to_numpy(dtype=np.float64), swing
            ),
            "mean_abs_prob_delta": float(cells["abs_prob_delta"].mean()),
            "mean_abs_logit_delta": float(cells["abs_logit_delta"].mean()),
            "max_abs_logit_delta": float(cells["abs_logit_delta"].max()),
            "adverse_over_e216_miss": float(cells["adverse_delta"].sum() / OBS_E216_MISS),
            "cells_for_2e6_guard": e162.min_cells_for_threshold(swing, PUBLIC_READABLE_GUARD),
            "cells_for_e95_edge": e162.min_cells_for_threshold(swing, E95_EDGE_OVER_MIXMIN),
            "cells_to_flip_expected_focus": e162.min_cells_for_threshold(swing, abs_expected),
        }
    )
    rec["top1_over_abs_expected"] = float(rec["top1_swing"] / max(abs_expected, 1.0e-15))
    rec["top5_over_abs_expected"] = float(rec["top5_swing"] / max(abs_expected, 1.0e-15))
    rec["top1_swing_share"] = float(rec["top1_swing"] / max(total_swing, 1.0e-15))
    rec["top5_swing_share"] = float(rec["top5_swing"] / max(total_swing, 1.0e-15))
    rec["support_tail_gate"] = bool(
        expected_focus < 0.0
        and rec["support_prob_focus_swing_weighted"] >= 0.50
        and rec["top1_over_abs_expected"] <= 0.50
        and rec["cells_for_2e6_guard"] >= 1
    )
    return rec


def cell_table(
    spec: Candidate,
    pair_kind: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    base_name: str,
    priors: dict[str, np.ndarray],
    sample: pd.DataFrame,
) -> pd.DataFrame:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    if len(row_idx) == 0:
        return pd.DataFrame()

    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / N_PUBLIC_CELLS
    dy0_s = dy0 / N_PUBLIC_CELLS
    support_label = np.where(dy1_s < dy0_s, 1, 0)
    support_delta = np.minimum(dy1_s, dy0_s)
    adverse_delta = np.maximum(dy1_s, dy0_s)
    swing = np.abs(dy1_s - dy0_s)
    py_focus = priors["focus_mean"][row_idx, target_idx]
    py_global = priors["global"][row_idx, target_idx]
    py_subject = priors["subject"][row_idx, target_idx]
    py_nearest = priors["nearest_hard085"][row_idx, target_idx]
    support_prob_focus = np.where(support_label == 1, py_focus, 1.0 - py_focus)

    out = pd.DataFrame(
        {
            "candidate_id": spec.candidate_id,
            "family": spec.family,
            "status": spec.status,
            "pair_kind": pair_kind,
            "candidate_file": spec.file_name,
            "base_file": base_name,
            "row_idx": row_idx,
            "target_idx": target_idx,
            "target": [TARGETS[j] for j in target_idx],
            "subject_id": sample.loc[row_idx, "subject_id"].astype(str).to_numpy(),
            "sleep_date": sample.loc[row_idx, "sleep_date"].astype(str).to_numpy(),
            "lifelog_date": sample.loc[row_idx, "lifelog_date"].astype(str).to_numpy(),
            "p_base": p_base[row_idx, target_idx],
            "p_new": p_new[row_idx, target_idx],
            "prob_delta": p_new[row_idx, target_idx] - p_base[row_idx, target_idx],
            "abs_prob_delta": np.abs(p_new[row_idx, target_idx] - p_base[row_idx, target_idx]),
            "logit_delta": logit(p_new[row_idx, target_idx]) - logit(p_base[row_idx, target_idx]),
            "abs_logit_delta": np.abs(logit(p_new[row_idx, target_idx]) - logit(p_base[row_idx, target_idx])),
            "loss_delta_y1": dy1_s,
            "loss_delta_y0": dy0_s,
            "support_label": support_label,
            "support_delta": support_delta,
            "adverse_delta": adverse_delta,
            "swing": swing,
            "py_focus": py_focus,
            "py_global": py_global,
            "py_subject": py_subject,
            "py_nearest_hard085": py_nearest,
            "expected_focus": py_focus * dy1_s + (1.0 - py_focus) * dy0_s,
            "expected_global": py_global * dy1_s + (1.0 - py_global) * dy0_s,
            "expected_subject": py_subject * dy1_s + (1.0 - py_subject) * dy0_s,
            "expected_nearest_hard085": py_nearest * dy1_s + (1.0 - py_nearest) * dy0_s,
            "hard_delta_focus": np.where(py_focus >= 0.5, dy1_s, dy0_s),
            "support_prob_focus": support_prob_focus,
        }
    )
    return out


def pair_audit(
    spec: Candidate,
    pair_kind: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    base_name: str,
    priors: dict[str, np.ndarray],
    sample: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    cells = cell_table(spec, pair_kind, p_new, p_base, base_name, priors, sample)
    summary = summarize_cells(
        cells,
        {
            "candidate_id": spec.candidate_id,
            "family": spec.family,
            "status": spec.status,
            "pair_kind": pair_kind,
            "candidate_file": spec.file_name,
            "base_file": base_name,
            "note": spec.note,
        },
    )
    target_rows: list[dict[str, Any]] = []
    if not cells.empty:
        for target, part in cells.groupby("target", sort=False):
            target_rows.append(
                summarize_cells(
                    part,
                    {
                        "candidate_id": spec.candidate_id,
                        "family": spec.family,
                        "status": spec.status,
                        "pair_kind": pair_kind,
                        "candidate_file": spec.file_name,
                        "base_file": base_name,
                        "target": target,
                    },
                )
            )
    target_df = pd.DataFrame(target_rows)
    top = cells.sort_values("swing", ascending=False).head(25).copy()
    return summary, target_df, top


def add_ranking(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    out = summary.copy()
    support = out["support_prob_focus_swing_weighted"].fillna(0.0)
    top = out["top1_over_abs_expected"].replace([np.inf, -np.inf], np.nan).fillna(9.0)
    expected = out["expected_focus"].fillna(0.0)
    adverse_ratio = out["adverse_over_e216_miss"].replace([np.inf, -np.inf], np.nan).fillna(9.0)
    out["e222_tail_survival_score"] = (
        -expected * 1000.0
        + (support - 0.45) * 0.20
        - np.maximum(top - 0.35, 0.0) * 0.02
        - np.maximum(adverse_ratio - 4.0, 0.0) * 0.0005
    )
    out["e222_decision"] = np.where(
        out["support_tail_gate"].astype(bool),
        "tail_supported",
        np.where(
            (expected < 0.0) & (support < 0.50),
            "expected_good_but_low_support",
            np.where(expected < 0.0, "expected_good_tail_unclear", "expected_bad_or_neutral"),
        ),
    )
    return out


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, top_cells: pd.DataFrame) -> None:
    live_anchor = summary[
        summary["pair_kind"].eq("graft_vs_anchor") & summary["status"].str.contains("live", regex=False)
    ].sort_values("e222_tail_survival_score", ascending=False)
    live_actual = summary[
        summary["pair_kind"].eq("actual_vs_e95") & summary["status"].str.contains("live", regex=False)
    ].sort_values("e222_tail_survival_score", ascending=False)
    controls = summary[summary["status"].str.contains("negative", regex=False)].sort_values(
        ["pair_kind", "candidate_id"]
    )
    target_live = target_df[
        target_df["pair_kind"].eq("graft_vs_anchor") & target_df["status"].str.contains("live", regex=False)
    ].sort_values(["candidate_id", "expected_focus"])

    cols = [
        "candidate_id",
        "pair_kind",
        "base_file",
        "moved_cells",
        "targets_moved",
        "expected_focus",
        "adverse_delta",
        "adverse_over_e216_miss",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "cells_to_flip_expected_focus",
        "support_tail_gate",
        "e222_decision",
        "e222_tail_survival_score",
    ]
    target_cols = [
        "candidate_id",
        "pair_kind",
        "target",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "support_tail_gate",
    ]
    top_cols = [
        "candidate_id",
        "pair_kind",
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
        "# E222 E211 Support/Tail Audit",
        "",
        "## Question",
        "",
        "After E216 failed publicly, does the live E211 Q3/S4 JEPA movement show the same low-support hard-label tail pattern?",
        "",
        "## Live Graft vs Anchor",
        "",
        md_table(live_anchor, cols, n=20),
        "",
        "## Live Actual vs E95",
        "",
        md_table(live_actual, cols, n=20),
        "",
        "## Negative Controls",
        "",
        md_table(controls, cols, n=20),
        "",
        "## Target Breakdown For Live Grafts",
        "",
        md_table(target_live, target_cols, n=30),
        "",
        "## Top Swing Cells",
        "",
        md_table(top_cells.sort_values("swing", ascending=False), top_cols, n=20),
        "",
        "## Decision",
        "",
    ]
    if live_anchor.empty:
        lines.append("- No live E211 candidates were audited.")
    else:
        best = live_anchor.iloc[0]
        low_support = live_anchor[live_anchor["e222_decision"].eq("expected_good_but_low_support")]
        lines.append(
            f"- Best live graft by E222 tail score: `{best['candidate_id']}` with expected focus `{best['expected_focus']:.9f}`, support probability `{best['support_prob_focus_swing_weighted']:.6f}`, and decision `{best['e222_decision']}`."
        )
        if not low_support.empty:
            lines.append(
                "- E211 is not automatically cleared by the E216 lesson: the live Q3/S4 grafts still have sub-0.5 swing-weighted support under focus priors, so public feedback should be read as a tail-support sensor rather than a safe improvement claim."
            )
        else:
            lines.append(
                "- Unlike E216, the live E211 grafts pass the explicit support-tail gate under this audit."
            )
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = load_prob(E95_FILE, sample)
    cache: dict[str, np.ndarray] = {E95_FILE: e95}
    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    top_parts: list[pd.DataFrame] = []

    for spec in CANDIDATES:
        if spec.file_name not in cache:
            cache[spec.file_name] = load_prob(spec.file_name, sample)
        if spec.anchor_file not in cache:
            cache[spec.anchor_file] = load_prob(spec.anchor_file, sample)
        cand = cache[spec.file_name]
        anchor = cache[spec.anchor_file]

        for pair_kind, base_name, base in [
            ("graft_vs_anchor", spec.anchor_file, anchor),
            ("actual_vs_e95", E95_FILE, e95),
        ]:
            rec, tgt, top = pair_audit(spec, pair_kind, cand, base, base_name, priors, sample)
            summary_rows.append(rec)
            if not tgt.empty:
                target_parts.append(tgt)
            if not top.empty:
                top_parts.append(top)

    summary = add_ranking(pd.DataFrame(summary_rows))
    target_df = add_ranking(pd.concat(target_parts, ignore_index=True)) if target_parts else pd.DataFrame()
    top_cells = pd.concat(top_parts, ignore_index=True) if top_parts else pd.DataFrame()
    summary = summary.sort_values(["pair_kind", "e222_tail_survival_score"], ascending=[True, False]).reset_index(drop=True)
    if not target_df.empty:
        target_df = target_df.sort_values(["pair_kind", "candidate_id", "target"]).reset_index(drop=True)
    if not top_cells.empty:
        top_cells = top_cells.sort_values("swing", ascending=False).reset_index(drop=True)

    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    write_report(summary, target_df, top_cells)

    print("[E222 summary]")
    cols = [
        "candidate_id",
        "pair_kind",
        "moved_cells",
        "targets_moved",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "e222_decision",
        "e222_tail_survival_score",
    ]
    print(summary[cols].round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
