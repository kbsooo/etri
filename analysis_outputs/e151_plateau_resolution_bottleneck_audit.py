#!/usr/bin/env python3
"""E151: compress the current 0.576 plateau into falsifiable bottleneck evidence.

This is not a model and it does not create a submission. It joins the already
observed public anchors and the E129-E150 stress chain to test a narrower
claim:

    The current plateau is not mainly caused by missing a better old CSV or by
    ordinary model capacity. It arises because local-upside directions and
    public-tail-safe directions only intersect on a tiny E142/E143/E144 branch,
    whose effect size is below the resolution of existing selectors.

The output is a decision report: what survives, what is weakened, and what the
next smallest kill experiment should be.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
A2C8_PUBLIC = 0.5774393210

SUMMARY_OUT = OUT / "e151_plateau_resolution_bottleneck_summary.csv"
FAMILY_OUT = OUT / "e151_plateau_resolution_family_evidence.csv"
CATEGORY_OUT = OUT / "e151_plateau_resolution_category_status.csv"
REPORT_OUT = OUT / "e151_plateau_resolution_bottleneck_report.md"


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def val(frame: pd.DataFrame, col: str, where: pd.Series | None = None, default: float = np.nan) -> float:
    rows = frame if where is None else frame[where]
    if rows.empty or col not in rows.columns:
        return default
    return float(rows.iloc[0][col])


def count_val(frame: pd.DataFrame, col: str, where: pd.Series | None = None) -> int:
    rows = frame if where is None else frame[where]
    if rows.empty or col not in rows.columns:
        return 0
    return int(rows.iloc[0][col])


def sum_col(frame: pd.DataFrame, col: str) -> int:
    if col not in frame.columns or frame.empty:
        return 0
    raw = frame[col]
    if raw.dtype == bool:
        return int(raw.sum())
    series = (
        raw.astype(str)
        .str.strip()
        .str.lower()
        .replace({"true": "1", "false": "0", "yes": "1", "no": "0"})
    )
    series = pd.to_numeric(series, errors="coerce").fillna(0)
    return int(series.sum())


def best_min(frame: pd.DataFrame, col: str) -> float:
    if col not in frame.columns or frame.empty:
        return np.nan
    return float(pd.to_numeric(frame[col], errors="coerce").min())


def best_max(frame: pd.DataFrame, col: str) -> float:
    if col not in frame.columns or frame.empty:
        return np.nan
    return float(pd.to_numeric(frame[col], errors="coerce").max())


def public_edges() -> pd.DataFrame:
    rows = [
        {
            "edge": "mixmin_gain_vs_a2c8",
            "delta_logloss": MIXMIN_PUBLIC - A2C8_PUBLIC,
            "abs_scale": abs(MIXMIN_PUBLIC - A2C8_PUBLIC),
            "read": "large anchor-loss/binary-world jump; not the current plateau scale",
        },
        {
            "edge": "e95_gain_vs_mixmin",
            "delta_logloss": E95_PUBLIC - MIXMIN_PUBLIC,
            "abs_scale": abs(E95_PUBLIC - MIXMIN_PUBLIC),
            "read": "current frontier edge; hardtail localization is real but tiny",
        },
        {
            "edge": "e101_loss_vs_e95",
            "delta_logloss": E101_PUBLIC - E95_PUBLIC,
            "abs_scale": abs(E101_PUBLIC - E95_PUBLIC),
            "read": "resolved negative sensor; one small S3-scale boundary can erase most expected gain",
        },
        {
            "edge": "e72_loss_vs_mixmin",
            "delta_logloss": E72_PUBLIC - MIXMIN_PUBLIC,
            "abs_scale": abs(E72_PUBLIC - MIXMIN_PUBLIC),
            "read": "failed broad movement scale; large enough for public to clearly reject",
        },
    ]
    return pd.DataFrame(rows)


def selector_resolution_rows(edges: pd.DataFrame) -> list[dict[str, Any]]:
    e98_scores = read_csv("e98_e95_updated_selector_model_scores.csv")
    best_proxy = e98_scores.sort_values("p90_abs_error").iloc[0]
    p90 = float(best_proxy["p90_abs_error"])
    mae = float(best_proxy["mae"])

    e120 = read_csv("e120_post_e101_public_observation_summary.csv").iloc[0]
    actual_minus_local_mean = float(e120["actual_minus_local_mean"])
    actual_minus_local_p95 = float(e120["actual_minus_local_p95"])
    local_e101_mean = float(e120["local_e101_mean_vs_e95"])
    local_e101_p95 = float(e120["local_e101_p95_vs_e95"])

    e144 = read_csv("e144_e143_active_boundary_refine_frontier.csv")
    selected = e144[e144["tag"].astype(str).str.contains("d7b4b331")].iloc[0]
    control = e144[e144["tag"].astype(str).eq("e144_control_e143")].iloc[0]
    e144_local_vs_e95 = float(selected["all_minus_base"])
    e143_local_vs_e95 = float(control["all_minus_base"])
    e144_vs_e143_local = e144_local_vs_e95 - e143_local_vs_e95
    e144_post101_p95 = float(selected["post101_p95_vs_e95_e101_sensor"])

    e149 = read_csv("e149_e144_anchor_geometry_summary.csv")
    e144_geom = e149[e149["name"].eq("e144")].iloc[0]

    e95_edge = float(edges[edges["edge"].eq("e95_gain_vs_mixmin")]["abs_scale"].iloc[0])
    e101_edge = float(edges[edges["edge"].eq("e101_loss_vs_e95")]["abs_scale"].iloc[0])
    e144_edge = abs(e144_local_vs_e95)
    e144_tiebreak = abs(e144_vs_e143_local)

    return [
        {
            "evidence": "best_known_lb_selector_p90_error",
            "value": p90,
            "reference": "e98_e95_updated_selector_model_scores.csv",
            "ratio_vs_e95_edge": p90 / e95_edge,
            "ratio_vs_e101_edge": p90 / e101_edge,
            "ratio_vs_e144_local_edge": p90 / e144_edge,
            "interpretation": "movement-fingerprint selectors are far too coarse for frontier-scale ranking",
        },
        {
            "evidence": "best_known_lb_selector_mae",
            "value": mae,
            "reference": "e98_e95_updated_selector_model_scores.csv",
            "ratio_vs_e95_edge": mae / e95_edge,
            "ratio_vs_e101_edge": mae / e101_edge,
            "ratio_vs_e144_local_edge": mae / e144_edge,
            "interpretation": "even average proxy error exceeds the live edge by more than an order of magnitude",
        },
        {
            "evidence": "e101_actual_minus_local_mean",
            "value": actual_minus_local_mean,
            "reference": "e120_post_e101_public_observation_summary.csv",
            "ratio_vs_e95_edge": actual_minus_local_mean / e95_edge,
            "ratio_vs_e101_edge": actual_minus_local_mean / e101_edge,
            "ratio_vs_e144_local_edge": actual_minus_local_mean / e144_edge,
            "interpretation": "local stress was optimistic by more than the entire E95 gain over mixmin",
        },
        {
            "evidence": "e101_actual_minus_local_p95",
            "value": actual_minus_local_p95,
            "reference": "e120_post_e101_public_observation_summary.csv",
            "ratio_vs_e95_edge": actual_minus_local_p95 / e95_edge,
            "ratio_vs_e101_edge": actual_minus_local_p95 / e101_edge,
            "ratio_vs_e144_local_edge": actual_minus_local_p95 / e144_edge,
            "interpretation": "the public tail beat the local p95 optimism; p95 alone was not conservative enough",
        },
        {
            "evidence": "e101_local_mean_vs_actual_direction",
            "value": local_e101_mean,
            "reference": "e120_post_e101_public_observation_summary.csv",
            "ratio_vs_e95_edge": abs(local_e101_mean) / e95_edge,
            "ratio_vs_e101_edge": abs(local_e101_mean) / e101_edge,
            "ratio_vs_e144_local_edge": abs(local_e101_mean) / e144_edge,
            "interpretation": "local mean predicted a win while public gave a loss",
        },
        {
            "evidence": "e144_vs_e95_local_edge",
            "value": e144_local_vs_e95,
            "reference": "e144_e143_active_boundary_refine_frontier.csv",
            "ratio_vs_e95_edge": abs(e144_local_vs_e95) / e95_edge,
            "ratio_vs_e101_edge": abs(e144_local_vs_e95) / e101_edge,
            "ratio_vs_e144_local_edge": 1.0,
            "interpretation": "E144 is a readable hypothesis sensor but not a 0.54-scale movement",
        },
        {
            "evidence": "e144_vs_e143_local_tiebreak",
            "value": e144_vs_e143_local,
            "reference": "e144_e143_active_boundary_refine_frontier.csv",
            "ratio_vs_e95_edge": e144_tiebreak / e95_edge,
            "ratio_vs_e101_edge": e144_tiebreak / e101_edge,
            "ratio_vs_e144_local_edge": e144_tiebreak / e144_edge,
            "interpretation": "the E144-over-E143 local edge is far below selector/public resolution",
        },
        {
            "evidence": "e144_post101_p95_vs_e95",
            "value": e144_post101_p95,
            "reference": "e144_e143_active_boundary_refine_frontier.csv",
            "ratio_vs_e95_edge": abs(e144_post101_p95) / e95_edge,
            "ratio_vs_e101_edge": abs(e144_post101_p95) / e101_edge,
            "ratio_vs_e144_local_edge": abs(e144_post101_p95) / e144_edge,
            "interpretation": "E144 survives the E101-tail stress, but only at micro-tail scale",
        },
        {
            "evidence": "e144_cosine_with_e143",
            "value": float(e144_geom["cos_e143_branch_axis"]),
            "reference": "e149_e144_anchor_geometry_summary.csv",
            "ratio_vs_e95_edge": np.nan,
            "ratio_vs_e101_edge": np.nan,
            "ratio_vs_e144_local_edge": np.nan,
            "interpretation": "E144 is branch-pruned geometry, not independent representation",
        },
    ]


def family_evidence() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    e129 = read_csv("e129_transfer_shrinkage_pareto_universe_gate_summary.csv")
    rows.append(
        {
            "family": "old_submission_universe",
            "question": "Did we just fail to pick an existing better CSV?",
            "best_local_edge": np.nan,
            "best_tail_p95": np.nan,
            "strict_or_submit_count": count_val(e129, "count", e129["gate"].eq("gate_strict_novel_actionable")),
            "failure_mode": "strict_novel_actionable=0",
            "belief_update": "candidate selection among old files is not the main missing lever",
        }
    )

    for name, file, question in [
        (
            "density_synthesis",
            "e130_tail_density_synthesis_probe_summary.csv",
            "Can transfer-shrinkage density plus old donors co-locate local reward and safety?",
        ),
        (
            "atom_combo_density",
            "e131_tail_density_atom_combo_probe_summary.csv",
            "Can atom combinations repair density-only donor mismatch?",
        ),
        (
            "veto_nullspace_gradient",
            "e132_veto_nullspace_gradient_probe_summary.csv",
            "Can E95-local gradients move in the safety nullspace directly?",
        ),
        (
            "blocktarget_state_gradient",
            "e137_blocktarget_state_movement_probe_summary.csv",
            "Does visible block-target state make gradient moves safe?",
        ),
        (
            "blocktarget_vetonull_overlap",
            "e138_blocktarget_vetonull_overlap_probe_summary.csv",
            "Does overlapping state with veto-null masks co-locate safety and strict structure?",
        ),
        (
            "set_consensus_decoder",
            "e139_blocktarget_set_consensus_decoder_probe_summary.csv",
            "Does set-consensus decoding make a safe target representation?",
        ),
    ]:
        df = read_csv(file)
        rows.append(
            {
                "family": name,
                "question": question,
                "best_local_edge": best_min(df, "best_all_minus_e95"),
                "best_tail_p95": best_min(df, "best_sensor_p95_vs_e95"),
                "strict_or_submit_count": sum_col(df, "submit_gate"),
                "failure_mode": "submit_gate=0; local reward and public-tail safety do not meet under the family gates",
                "belief_update": "use as representation diagnostic, not as submission source",
            }
        )

    e140 = read_csv("e141_tail_tolerance_transfer_audit_summary.csv")
    tol = e140[e140["tol"].astype(float).eq(1e-12)]
    rows.append(
        {
            "family": "tailworld_primitive_decoder_before_clip",
            "question": "Was E140 only blocked by numeric exactness?",
            "best_local_edge": val(tol, "best_relaxed_all_minus_e95"),
            "best_tail_p95": val(tol, "best_relaxed_post101_p95"),
            "strict_or_submit_count": count_val(tol, "relaxed_and_actionable"),
            "failure_mode": "relaxed structure exists but e72 budget/post101 p95 fail",
            "belief_update": "the blocker is transfer-tail budget, not exact-tail arithmetic",
        }
    )

    for name, file, submit_col, question, belief in [
        (
            "transfer_budget_clip_e142",
            "e142_transfer_budget_clipped_decoder_probe_summary.csv",
            "submit_relaxed",
            "Can budget-neutral clipping make E140 public-safe?",
            "first live residual branch opens, but still fails active/Q2S3 strictness",
        ),
        (
            "active_q2s3_repair_e143",
            "e143_e142_active_q2s3_veto_repair_summary.csv",
            "strict_submit",
            "Can pruning E101-warned active Q2/S3 cells make the branch strict?",
            "strict branch opens, but public value is frontier-scale small",
        ),
        (
            "fine_boundary_e144",
            "e144_e143_active_boundary_refine_summary.csv",
            "e144_submit",
            "Is the E143 full rollback boundary too coarse?",
            "E144 is the current sensor, but only a tiny same-branch refinement",
        ),
    ]:
        df = read_csv(file)
        rows.append(
            {
                "family": name,
                "question": question,
                "best_local_edge": best_min(df, "best_all_minus_e95"),
                "best_tail_p95": best_min(df, "best_post101_p95" if "best_post101_p95" in df.columns else "best_strict_post101_p95"),
                "strict_or_submit_count": sum_col(df, submit_col),
                "failure_mode": "survives as live sensor" if name == "fine_boundary_e144" else "not final until public feedback",
                "belief_update": belief,
            }
        )

    return pd.DataFrame(rows)


def category_status(summary: pd.DataFrame, family: pd.DataFrame) -> pd.DataFrame:
    p90_ratio = float(summary[summary["evidence"].eq("best_known_lb_selector_p90_error")]["ratio_vs_e95_edge"].iloc[0])
    e101_optimism_ratio = float(summary[summary["evidence"].eq("e101_actual_minus_local_mean")]["ratio_vs_e95_edge"].iloc[0])
    old_strict = int(family[family["family"].eq("old_submission_universe")]["strict_or_submit_count"].iloc[0])
    e144_count = int(family[family["family"].eq("fine_boundary_e144")]["strict_or_submit_count"].iloc[0])
    e144_cos = float(summary[summary["evidence"].eq("e144_cosine_with_e143")]["value"].iloc[0])

    rows = [
        {
            "category": "A_data_signal_shortage",
            "status": "evidence_weak_partial",
            "evidence": "E142-E144 and blocktarget states still produce local/post101 signal; the issue is safe decoding, not absence of all signal.",
            "kill_condition": "If independent representation creates no local/post101 signal after E144, upgrade toward data-signal shortage.",
        },
        {
            "category": "B_validation_mismatch",
            "status": "evidence_strong",
            "evidence": f"best known-LB selector p90 is {p90_ratio:.2f}x the E95 edge; E101 local optimism is {e101_optimism_ratio:.2f}x the E95 edge.",
            "kill_condition": "A new validation object must rank E95/E101/E144 correctly with error below 5e-6.",
        },
        {
            "category": "C_public_subset_mismatch",
            "status": "evidence_strong_but_underidentified",
            "evidence": "E101 public feedback invalidated broad-plausible local transfer while preserving part of mixmin gain; E144 requires score+attribution+geometry.",
            "kill_condition": "E144 clean win with attribution dominated by inherited body would reduce subset-mismatch emphasis.",
        },
        {
            "category": "D_target_prior_calibration_tail",
            "status": "evidence_strong",
            "evidence": "E95 hardtail survives, E101 one-cell-scale S3 boundary misses, and E144 is mostly Q3/S3/S2/Q1/S4 tail calibration.",
            "kill_condition": "A broad all-target move beats E95 without hardtail pruning.",
        },
        {
            "category": "E_representation_decoder_problem",
            "status": "evidence_strong",
            "evidence": "E137/E138 show state/safety visibility, but submit gates stay zero until E142-E144 hand-built decoder branch.",
            "kill_condition": "A representation-to-probability decoder passes strict, budget, post101 p95, and independent geometry without manual clipping.",
        },
        {
            "category": "F_candidate_selection_problem",
            "status": "mostly_rejected_for_existing_files",
            "evidence": f"E129 strict novel actionable count is {old_strict}; E144 branch count is {e144_count} but cos(E144,E143)={e144_cos:.6f}.",
            "kill_condition": "A forgotten old candidate passes E129 plus E120/E149-style stress without being same-family.",
        },
    ]
    return pd.DataFrame(rows)


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            x = rec[col]
            if pd.isna(x):
                vals.append("")
            elif isinstance(x, (float, np.floating)):
                vals.append(format(float(x), floatfmt))
            else:
                vals.append(str(x))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(edges: pd.DataFrame, summary: pd.DataFrame, family: pd.DataFrame, categories: pd.DataFrame) -> None:
    top_summary = summary[
        summary["evidence"].isin(
            [
                "best_known_lb_selector_p90_error",
                "e101_actual_minus_local_mean",
                "e144_vs_e95_local_edge",
                "e144_vs_e143_local_tiebreak",
                "e144_cosine_with_e143",
            ]
        )
    ].copy()
    family_view = family[
        [
            "family",
            "best_local_edge",
            "best_tail_p95",
            "strict_or_submit_count",
            "failure_mode",
            "belief_update",
        ]
    ].copy()

    text = f"""# E151 Plateau Resolution Bottleneck Audit

## Question

Is the `0.5762913298` plateau mainly an ordinary candidate-selection/modeling
problem, or is it a resolution/decoder bottleneck where public-tail-safe
directions and local-upside directions only intersect on a tiny branch?

## Strangest Observed Point

The current public frontier is separated from mixmin by only
`{abs(E95_PUBLIC - MIXMIN_PUBLIC):.10f}`, while the best known-LB selector p90
error is `{float(summary[summary['evidence'].eq('best_known_lb_selector_p90_error')]['value'].iloc[0]):.10f}`.
That is `{float(summary[summary['evidence'].eq('best_known_lb_selector_p90_error')]['ratio_vs_e95_edge'].iloc[0]):.2f}x`
the frontier edge. At the same time, E144's improvement over E143 locally is
only `{abs(float(summary[summary['evidence'].eq('e144_vs_e143_local_tiebreak')]['value'].iloc[0])):.10f}`.

## Current Strongest World Model

`E95 is a real S-heavy hardtail/calibration law. The next residual structure is
visible, but current validation/proxy selectors cannot resolve frontier-scale
edges, and most decoders turn visible state into either local reward or
public-tail safety, not both. E142/E143/E144 are the only current intersection,
and E144 is a branch-pruned sensor rather than a broad new representation.`

## What This World Predicts

- Old-file universe search should keep returning no novel strict successor.
- Local-gradient/state-aware probes can show impressive mean/local reward but
  fail strict/actionable gates or p95/tail budget.
- Any public-improving successor before a new representation decoder should be
  E95-relative, small, and heavily constrained by E72/E101 tail geometry.
- E144 public feedback will be informative, but even a win is a branch validation,
  not a 0.54-scale breakthrough.

## Smallest Experiment That Can Kill It

Two options can kill this model:

1. Public: submit `submission_e144_activeboundary_d7b4b331.csv` and interpret
   with `analysis_outputs/e150_e144_postfeedback_interpreter.py --score <LB>`.
2. Local: produce a new representation-to-probability decoder that passes
   strict structure, E72 budget, post-E101 p95, and independent geometry with a
   local edge comfortably above `1e-5` without being E142/E143/E144-collinear.

## Public Edge Scales

{md_table(edges, ".10f")}

## Resolution Evidence

{md_table(top_summary, ".10f")}

## Family Evidence

{md_table(family_view, ".10f")}

## Bottleneck Category Status

{md_table(categories, ".9f")}

## Experiment Result

E151 does not create a submission. It falsifies the easy explanation that the
plateau is mainly a missed old candidate or a generic model-capacity problem.
The stronger explanation is a decoder/resolution bottleneck: the signal is
visible enough to form E142-E144, but public-safe probability movement is only
certified on a very narrow, E143-collinear branch.

## Belief Update

- Strengthen: validation mismatch, public subset/tail calibration, and
  representation-decoder bottleneck.
- Weaken: old-candidate selection failure and same-family Q2/S3 amplitude
  tweaking.
- Keep alive: E144 as the next public sensor.

## Next Highest-Information Action

Submit `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv` if a
single public slot is available. If waiting, the next local experiment should
not be a blend/top-count sweep. It should build an independent decoder target:
predict the transfer-budget-neutral residual representation, then prove it can
move probabilities with strict/actionable gates and non-collinearity to E143.

## Submission Candidate

- File: `analysis_outputs/submission_e144_activeboundary_d7b4b331.csv`
- Intent: test whether E95 can accept a branch-pruned, transfer-budget-neutral
  residual movement after active/Q2S3 pruning.
- Expected public reaction: a clean or micro win strengthens the residual branch;
  a tie keeps E95 as practical frontier; a fine loss is conditional and does not
  automatically justify E143; branch loss/hard fail closes same-family rescue.
- Failure interpretation: public hidden S3/Q3/body tail is more adverse than the
  visible priors, or the whole E142/E143/E144 branch is public-sensor overfit.
"""
    REPORT_OUT.write_text(text, encoding="utf-8")


def main() -> None:
    edges = public_edges()
    summary = pd.DataFrame(selector_resolution_rows(edges))
    family = family_evidence()
    categories = category_status(summary, family)

    summary.to_csv(SUMMARY_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)
    categories.to_csv(CATEGORY_OUT, index=False)
    write_report(edges, summary, family, categories)

    print(
        {
            "summary": str(SUMMARY_OUT),
            "family": str(FAMILY_OUT),
            "categories": str(CATEGORY_OUT),
            "report": str(REPORT_OUT),
            "rows": {
                "summary": len(summary),
                "family": len(family),
                "categories": len(categories),
            },
        }
    )
    print(categories[["category", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
