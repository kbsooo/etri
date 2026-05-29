#!/usr/bin/env python3
"""E141: audit whether E140 failed on real combo tails or transfer vetoes.

E140 reported all combined variants failing all-set tail neutrality. Inspection
showed that raw05/all-sign worst-tail deltas are often numerical zero
(`1.11e-16`). This audit separates three possibilities:

1. exact-tail gate artifact;
2. true inverse-top tail failure;
3. transfer/E72/post-E101 veto failure after tail tolerance.

No new prediction is created and no public labels are fitted.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, load_sub  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e96_public_miss_budget_tail_scenarios as e96mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


SCAN_IN = OUT / "e140_tailworld_primitive_decoder_probe_scan.csv"
MICRO_IN = OUT / "e140_tailworld_primitive_decoder_probe_micro.csv"
SUMMARY_OUT = OUT / "e141_tail_tolerance_transfer_audit_summary.csv"
FRONTIER_OUT = OUT / "e141_tail_tolerance_transfer_audit_frontier.csv"
REPORT_OUT = OUT / "e141_tail_tolerance_transfer_audit_report.md"

TOLS = [0.0, 1.0e-15, 1.0e-12, 1.0e-9, 1.0e-6, 1.0e-5]


def tail_cols(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns if c.startswith("set_") and c.endswith("_worst_minus_base")]


def set_cols(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns if c.startswith("set_") and c.endswith("_minus_base") and "worst" not in c]


def e95_plausible_exposure_threshold() -> float:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    _loss, _weight, wrong_is_zero, wrong_is_one = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    _density_masks, density = e130.build_density_masks(sample, refs)
    adverse = np.maximum(
        e96mod.adverse_delta_for_e72_direction(refs["e95"], refs["mixmin"], wrong_is_zero, wrong_is_one),
        0.0,
    )
    return e130.weighted_l1(adverse, density["plausible"].reshape(-1))


def summarize_tolerances(scan: pd.DataFrame, threshold: float) -> pd.DataFrame:
    tails = tail_cols(scan)
    sets = set_cols(scan)
    rows: list[dict[str, Any]] = []
    all_sets_beat = scan[sets].lt(0.0).all(axis=1)
    base_core = (
        scan["all_margin_vs_mixmin"].fillna(False).astype(bool)
        & scan["all_beats_base"].fillna(False).astype(bool)
        & all_sets_beat
        & scan["hidden_core_minus_base"].lt(0.0)
        & scan["world_support_minus_base"].le(0.0)
        & scan["raw_energy_q_p90_minus_base"].le(0.0)
    )
    for tol in TOLS:
        tail_pass = scan[tails].le(tol).all(axis=1)
        relaxed = base_core & tail_pass
        e72_pass = scan["e72_adverse_exposure_e101_plausible"].le(threshold + 1.0e-12)
        post101_pass = scan["post101_mean_vs_e95_e101_sensor"].lt(0.0) & scan[
            "post101_p95_vs_e95_e101_sensor"
        ].le(0.0)
        actionable = relaxed & scan["gate_strict_actionable"].fillna(False).astype(bool)
        rows.append(
            {
                "tol": tol,
                "tail_pass": int(tail_pass.sum()),
                "base_core_pass": int(base_core.sum()),
                "relaxed_structural_pass": int(relaxed.sum()),
                "relaxed_and_e72_pass": int((relaxed & e72_pass).sum()),
                "relaxed_and_post101_pass": int((relaxed & post101_pass).sum()),
                "relaxed_and_strict_veto": int((relaxed & scan["gate_strict_veto"].fillna(False)).sum()),
                "relaxed_and_actionable": int(actionable.sum()),
                "best_relaxed_all_minus_e95": float(scan.loc[relaxed, "all_minus_base"].min())
                if relaxed.any()
                else np.nan,
                "best_relaxed_post101_mean": float(scan.loc[relaxed, "post101_mean_vs_e95_e101_sensor"].min())
                if relaxed.any()
                else np.nan,
                "best_relaxed_post101_p95": float(scan.loc[relaxed, "post101_p95_vs_e95_e101_sensor"].min())
                if relaxed.any()
                else np.nan,
                "min_relaxed_e72_plausible_exposure": float(
                    scan.loc[relaxed, "e72_adverse_exposure_e101_plausible"].min()
                )
                if relaxed.any()
                else np.nan,
                "e72_threshold": float(threshold),
                "min_relaxed_e72_gap": float(
                    scan.loc[relaxed, "e72_adverse_exposure_e101_plausible"].min() - threshold
                )
                if relaxed.any()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def frontier_rows(scan: pd.DataFrame, threshold: float) -> pd.DataFrame:
    tails = tail_cols(scan)
    sets = set_cols(scan)
    frame = scan.copy()
    frame["tail_pass_tol1e12"] = frame[tails].le(1.0e-12).all(axis=1)
    frame["all_sets_mean_beat"] = frame[sets].lt(0.0).all(axis=1)
    frame["relaxed_structural_tol1e12"] = (
        frame["all_margin_vs_mixmin"].fillna(False).astype(bool)
        & frame["all_beats_base"].fillna(False).astype(bool)
        & frame["all_sets_mean_beat"]
        & frame["tail_pass_tol1e12"]
        & frame["hidden_core_minus_base"].lt(0.0)
        & frame["world_support_minus_base"].le(0.0)
        & frame["raw_energy_q_p90_minus_base"].le(0.0)
    )
    frame["e72_plausible_gap_vs_e95"] = frame["e72_adverse_exposure_e101_plausible"] - threshold
    frame["post101_p95_positive"] = frame["post101_p95_vs_e95_e101_sensor"].clip(lower=0.0)
    frame["frontier_score"] = (
        -frame["all_minus_base"].clip(upper=0.0)
        - 10.0 * frame["e72_plausible_gap_vs_e95"].clip(lower=0.0)
        - 10.0 * frame["post101_p95_positive"]
        - 2.0 * frame["tail_equal_law_resid_ratio"].clip(lower=0.0)
    )
    keep_cols = [
        "pool",
        "top_k",
        "shape",
        "scale",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        *sets,
        *tails,
        "tail_pass_tol1e12",
        "relaxed_structural_tol1e12",
        "e72_adverse_exposure_e101_plausible",
        "e72_plausible_gap_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "gate_cos95_resid025",
        "gate_active_q2s3_not_more_than_e101",
        "gate_e72_not_more_than_e95",
        "gate_material_vs_e95",
        "gate_strict_veto",
        "gate_strict_actionable",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "frontier_score",
        "tag",
    ]
    return frame.sort_values(
        ["relaxed_structural_tol1e12", "e72_plausible_gap_vs_e95", "post101_p95_positive", "all_minus_base"],
        ascending=[False, True, True, True],
    )[keep_cols].head(80)


def micro_axis_summary(micro: pd.DataFrame) -> pd.DataFrame:
    tails = tail_cols(micro)
    rows: list[dict[str, Any]] = []
    for scope, group in [("all", micro), *list(micro.groupby("target", sort=True))]:
        rec: dict[str, Any] = {"scope": str(scope), "rows": int(len(group))}
        for col in tails:
            name = col.replace("set_", "").replace("_worst_minus_base", "")
            rec[f"{name}_tail_pass_exact"] = int(group[col].le(0.0).sum())
            rec[f"{name}_tail_pass_tol1e12"] = int(group[col].le(1.0e-12).sum())
            rec[f"{name}_tail_max"] = float(group[col].max())
        rec["all_tail_pass_tol1e12"] = int(group[tails].le(1.0e-12).all(axis=1).sum())
        rec["local_reward"] = int(group["primitive_local_reward"].sum()) if "primitive_local_reward" in group else 0
        rec["tail_world_local"] = int(group["primitive_tail_world_local"].sum()) if "primitive_tail_world_local" in group else 0
        rows.append(rec)
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, frontier: pd.DataFrame, micro_summary: pd.DataFrame) -> None:
    best = frontier.head(1).iloc[0] if len(frontier) else None
    lines = [
        "# E141 Tail Tolerance / Transfer Audit",
        "",
        "## Question",
        "",
        "E140 said all combined rows failed all-set tail neutrality. E141 asks whether that is a real tail-axis failure or an exact-zero gate artifact, then checks what remains blocked after a small tolerance.",
        "",
        "## Tolerance Summary",
        "",
        e138.md_table(summary, ".12f"),
        "",
        "## Micro Tail-Axis Summary",
        "",
        e138.md_table(micro_summary, ".12f"),
        "",
        "## Frontier Rows After Tail Tolerance",
        "",
        e138.md_table(frontier.head(30), ".12f"),
        "",
        "## Interpretation",
        "",
    ]
    if best is not None:
        lines.extend(
            [
                f"- At tolerance `1e-12`, relaxed structural rows open, but strict-veto/actionable rows remain `0`.",
                f"- The best E72-plausible gap after relaxed structure is `{float(summary.loc[summary['tol'].eq(1.0e-12), 'min_relaxed_e72_gap'].iloc[0]):.12f}`.",
                f"- Best frontier row: `{best['tag']}` with all-minus-E95 `{float(best['all_minus_base']):.12f}`, E72 gap `{float(best['e72_plausible_gap_vs_e95']):.12f}`, post-E101 p95 `{float(best['post101_p95_vs_e95_e101_sensor']):.12f}`.",
            ]
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "No submission. The exact tail gate was too brittle, but relaxing it does not create a candidate. The surviving blocker is transfer-tail budget: E72-plausible exposure remains above the E95 threshold and post-E101 p95 remains positive before material actionability appears.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan = pd.read_csv(SCAN_IN)
    micro = pd.read_csv(MICRO_IN)
    threshold = e95_plausible_exposure_threshold()
    summary = summarize_tolerances(scan, threshold)
    frontier = frontier_rows(scan, threshold)
    micro_summary = micro_axis_summary(micro)
    summary.to_csv(SUMMARY_OUT, index=False)
    frontier.to_csv(FRONTIER_OUT, index=False)
    write_report(summary, frontier, micro_summary)
    row = summary[summary["tol"].eq(1.0e-12)].iloc[0]
    print(
        {
            "e95_e72_threshold": float(threshold),
            "tail_pass_tol1e12": int(row["tail_pass"]),
            "relaxed_structural_tol1e12": int(row["relaxed_structural_pass"]),
            "relaxed_and_e72_pass": int(row["relaxed_and_e72_pass"]),
            "relaxed_and_post101_pass": int(row["relaxed_and_post101_pass"]),
            "relaxed_and_actionable": int(row["relaxed_and_actionable"]),
            "min_relaxed_e72_gap": float(row["min_relaxed_e72_gap"]),
            "best_relaxed_all_minus_e95": float(row["best_relaxed_all_minus_e95"]),
            "best_relaxed_post101_p95": float(row["best_relaxed_post101_p95"]),
        }
    )


if __name__ == "__main__":
    main()
