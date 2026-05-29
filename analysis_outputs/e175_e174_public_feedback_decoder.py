#!/usr/bin/env python3
"""E175: pre-public feedback decoder for E174.

E174 reopens a ranked subset of E172 rollback cells. This script fixes the
public-score interpretation before feedback: it separates a true partial
reopening win from hidden-label underresolution or Q2/S3 over-reopening.

It creates no new submission.
"""

from __future__ import annotations

import argparse
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
import e171_e169_critical_cell_prior_audit as e171  # noqa: E402
import e172_e169_critical_tail_rollback_probe as e172  # noqa: E402
import e173_e172_public_feedback_decoder as e173  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E95_EDGE_VS_MIXMIN = E95_PUBLIC - MIXMIN_PUBLIC
E101_DELTA_VS_E95 = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA_VS_E95 = MIXMIN_PUBLIC - E95_PUBLIC

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E174_FILE = "submission_e174_ro_fc_top75_to1p0_95638e73.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

BANDS_OUT = OUT / "e175_e174_public_feedback_decoder_bands.csv"
PAIRWISE_OUT = OUT / "e175_e174_public_feedback_decoder_pairwise.csv"
TOP_CELLS_OUT = OUT / "e175_e174_public_feedback_decoder_top_cells.csv"
GROUP_ATTR_OUT = OUT / "e175_e174_public_feedback_decoder_group_attribution.csv"
PRIOR_MOMENTS_OUT = OUT / "e175_e174_public_feedback_decoder_prior_moments.csv"
REPORT_OUT = OUT / "e175_e174_public_feedback_decoder_report.md"
OBSERVED_OUT = OUT / "e175_e174_observed_score_decision.csv"

EPS = 1.0e-12


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "partial_reopen_breakthrough",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update": "E174 wins beyond ordinary post-E95 scale. The broad body, visible-tail repair, and partial reopening are all public-real.",
        "next_action": "Promote E174 as a new broad anchor; decompose the top-75 reopened cells by target/context before any larger reopening.",
        "candidate_to_test": "conditional:e174_reopen_decomposition",
        "forbidden_action": "Do not jump to raw E169 or raw E166. The observation validates controlled reopening, not the unrolled body.",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": E95_EDGE_VS_MIXMIN,
        "world_update": "E174 wins by at least the E95-over-mixmin edge. E172 was overconservative at public-readable scale.",
        "next_action": "Use E174 as the broad expected-score anchor. Next experiment should localize whether S3, Q2, or S2 carried the reopening gain.",
        "candidate_to_test": "conditional:e174_target_context_ablation",
        "forbidden_action": "Do not submit E172 just to be safer unless the goal is private-risk contrast rather than expected public score.",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": E95_EDGE_VS_MIXMIN,
        "delta_hi_inclusive": -3.0e-6,
        "world_update": "E174 is public-positive but still frontier-resolution scale. Partial reopening is alive, but hidden-label resolution remains the bottleneck.",
        "next_action": "Promote cautiously. Prefer a responsibility audit over same-family keep-factor tuning.",
        "candidate_to_test": "conditional:e174_responsibility_audit",
        "forbidden_action": "Do not claim the broad lane is solved; a few high-swing labels can still explain the win.",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update": "E174 does not separate from E95. Either partial reopening is hidden-label underresolved, or its recovered body signal cancels its Q2/S3 risk.",
        "next_action": "Keep E95 practical. If spending another broad slot, E172 is the cleaner contrast because it tests whether reopening was the error.",
        "candidate_to_test": "analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv",
        "forbidden_action": "Do not tune top-N or keep factors from a tie.",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": E101_DELTA_VS_E95,
        "world_update": "E174 loses to E95 but no worse than E101. The most likely failure is over-reopening or unresolved hidden hard labels, not necessarily broad-body rejection.",
        "next_action": "Use E172 as the only same-family contrast if the next question remains broad tail repair. Otherwise shift to E154/conservative branch.",
        "candidate_to_test": "conditional:E172_or_E154_by_question",
        "forbidden_action": "Do not submit E169; it has more of the same reopened tail and worse visible-risk geometry.",
    },
    {
        "outcome": "e101_worse_mixmin_safe",
        "delta_lo_exclusive": E101_DELTA_VS_E95,
        "delta_hi_inclusive": MIXMIN_DELTA_VS_E95,
        "world_update": "E174 is worse than E101 but still mixmin-safe. The partial reopening likely spent too much Q2/S3 or q2_bad margin.",
        "next_action": "Demote E174. E172 is information-only unless we explicitly need to test whether full damping saves the broad body; otherwise prefer E154.",
        "candidate_to_test": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
        "forbidden_action": "Do not rescue with top-50/top-100 reopening siblings.",
    },
    {
        "outcome": "branch_loss",
        "delta_lo_exclusive": MIXMIN_DELTA_VS_E95,
        "delta_hi_inclusive": 5.0e-5,
        "world_update": "E174 gives back the E95-over-mixmin gain. Controlled reopening is not enough; the broad body or safety axis is public-misaligned.",
        "next_action": "Close E174 same-family reopening and make E172 only a low-risk contrast, not an automatic next file.",
        "candidate_to_test": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
        "forbidden_action": "Do not submit E169/E166 unless deliberately accepting a high-risk falsification slot.",
    },
    {
        "outcome": "hard_fail",
        "delta_lo_exclusive": 5.0e-5,
        "delta_hi_inclusive": np.inf,
        "world_update": "E174 is strongly incompatible with public labels. The broad-reopen family missed a major negative axis.",
        "next_action": "Close E174/E172/E169 same-family broad expected-score followups and rebuild the bad-axis geometry.",
        "candidate_to_test": "",
        "forbidden_action": "Do not submit threshold, keep-factor, or density siblings.",
    },
]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)


def lb_bound(delta: float) -> float:
    return E95_PUBLIC + float(delta)


def build_bands() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for band in BANDS:
        lo = float(band["delta_lo_exclusive"])
        hi = float(band["delta_hi_inclusive"])
        rows.append(
            {
                "outcome": band["outcome"],
                "delta_vs_e95_lo_exclusive": lo,
                "delta_vs_e95_hi_inclusive": hi,
                "public_lb_lo_exclusive": lb_bound(lo) if np.isfinite(lo) else -np.inf,
                "public_lb_hi_inclusive": lb_bound(hi) if np.isfinite(hi) else np.inf,
                "beats_e95": hi < 0,
                "beats_e101": (lb_bound(hi) < E101_PUBLIC) if np.isfinite(hi) else False,
                "beats_mixmin": (lb_bound(hi) < MIXMIN_PUBLIC) if np.isfinite(hi) else False,
                "world_update": band["world_update"],
                "next_action": band["next_action"],
                "candidate_to_test": band["candidate_to_test"],
                "forbidden_action": band["forbidden_action"],
            }
        )
    return pd.DataFrame(rows)


def classify_score(score: float, bands: pd.DataFrame) -> pd.Series:
    delta = float(score) - E95_PUBLIC
    hit = bands[
        bands["delta_vs_e95_lo_exclusive"].lt(delta)
        & bands["delta_vs_e95_hi_inclusive"].ge(delta)
    ]
    if len(hit) != 1:
        raise RuntimeError(f"score {score} maps to {len(hit)} bands")
    row = hit.iloc[0].copy()
    row["observed_public_lb"] = float(score)
    row["observed_delta_vs_e95"] = delta
    row["observed_delta_vs_e101"] = float(score) - E101_PUBLIC
    row["observed_delta_vs_mixmin"] = float(score) - MIXMIN_PUBLIC
    return row


def pairwise_metrics(sample: pd.DataFrame, priors: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    probs = {
        "e95": load_prob(E95_FILE, sample),
        "e174_partial_reopen": load_prob(E174_FILE, sample),
        "e172_tail_repair": load_prob(E172_FILE, sample),
        "e169_unrolled": load_prob(E169_FILE, sample),
        "e166_raw": load_prob(E166_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e101": load_prob(E101_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
    }
    pairs = [
        ("e174_partial_reopen", "e95"),
        ("e172_tail_repair", "e95"),
        ("e174_partial_reopen", "e172_tail_repair"),
        ("e174_partial_reopen", "e169_unrolled"),
        ("e174_partial_reopen", "e166_raw"),
        ("e174_partial_reopen", "e154"),
        ("e174_partial_reopen", "e101"),
        ("e174_partial_reopen", "mixmin"),
    ]
    rows: list[dict[str, Any]] = []
    top_rows: list[pd.DataFrame] = []
    for new, base in pairs:
        rec, top = e162.pair_metrics(new, base, probs[new], probs[base], priors)
        rows.append(rec)
        if not top.empty:
            top["pair"] = f"{new}_vs_{base}"
            top_rows.append(top)
    pairwise = pd.DataFrame(rows)
    tops = pd.concat(top_rows, ignore_index=True) if top_rows else pd.DataFrame()
    return pairwise, tops


def prior_moment_table(sample: pd.DataFrame) -> pd.DataFrame:
    e95 = load_prob(E95_FILE, sample)
    preds = {
        "e169_unrolled_vs_e95": load_prob(E169_FILE, sample),
        "e172_tail_repair_vs_e95": load_prob(E172_FILE, sample),
        "e174_partial_reopen_vs_e95": load_prob(E174_FILE, sample),
    }
    cells = e171.build_cells()
    rows: list[dict[str, Any]] = []
    for candidate, pred in preds.items():
        rec: dict[str, Any] = {"candidate": candidate}
        for prior in e172.PRIORS:
            rec.update(e172.prior_moments(cells, pred, e95, prior))
        rows.append(rec)
    out = pd.DataFrame(rows)
    base_e169 = out[out["candidate"].eq("e169_unrolled_vs_e95")].iloc[0]
    base_e172 = out[out["candidate"].eq("e172_tail_repair_vs_e95")].iloc[0]
    for col in out.columns:
        if col.startswith(("mean_delta_", "p95_delta_norm_", "worse_than_e101_norm_")):
            out[f"delta_{col}_vs_e169"] = out[col] - float(base_e169[col])
            out[f"delta_{col}_vs_e172"] = out[col] - float(base_e172[col])
    return out


def write_report(
    bands: pd.DataFrame,
    pairwise: pd.DataFrame,
    top_cells: pd.DataFrame,
    groups: pd.DataFrame,
    prior_moments: pd.DataFrame,
    observed: pd.Series | None,
) -> None:
    pair_cols = [
        "new",
        "base",
        "moved_cells",
        "moved_rows",
        "targets_moved",
        "expected_delta_focus_mean",
        "cells_to_flip_expected_focus_mean",
        "top1_swing",
        "top5_swing",
        "cells_for_2e6_guard",
        "cells_for_e95_edge",
        "support_prob_swing_weighted_focus_mean",
    ]
    moment_cols = [
        "candidate",
        "mean_delta_focus_mean",
        "mean_delta_visible_mean",
        "p95_delta_norm_visible_mean",
        "worse_than_e101_norm_visible_mean",
        "mean_delta_subject",
        "mean_delta_flank_mean",
        "delta_mean_delta_focus_mean_vs_e172",
        "delta_mean_delta_visible_mean_vs_e172",
        "delta_p95_delta_norm_visible_mean_vs_e172",
        "delta_worse_than_e101_norm_visible_mean_vs_e172",
    ]
    group_focus = groups[
        groups["pair"].isin(["e174_vs_e95", "e174_vs_e172", "e174_vs_e169"])
        & groups["group_kind"].isin(["target", "target_group", "context_type", "e72_active", "target_context"])
    ].sort_values(["pair", "group_kind", "expected_delta_focus_mean"])
    top_vs_e95 = top_cells[top_cells["pair"].eq("e174_partial_reopen_vs_e95")].sort_values("swing", ascending=False)
    top_vs_e172 = top_cells[top_cells["pair"].eq("e174_partial_reopen_vs_e172_tail_repair")].sort_values(
        "swing", ascending=False
    )
    observed_text = "_No observed E174 public score supplied._"
    if observed is not None:
        observed_text = md_table(pd.DataFrame([observed.to_dict()]), None, n=1)

    report = f"""# E175 E174 Public Feedback Decoder

## Question

If `submission_e174_ro_fc_top75_to1p0_95638e73.csv` is submitted, how should
its public LB update the broad-branch world model without post-hoc keep-factor
tuning?

Current anchors:

- E95 public LB: `{E95_PUBLIC:.10f}`
- E101 public LB: `{E101_PUBLIC:.10f}`
- mixmin public LB: `{MIXMIN_PUBLIC:.10f}`
- E95 edge over mixmin: `{E95_EDGE_VS_MIXMIN:.10f}`

## Decoder Bands

{md_table(bands, [
    "outcome",
    "public_lb_lo_exclusive",
    "public_lb_hi_inclusive",
    "beats_e95",
    "beats_e101",
    "beats_mixmin",
    "next_action",
    "candidate_to_test",
])}

## Prior-Moment Reopening Tradeoff

{md_table(prior_moments, moment_cols)}

## Pairwise Hard-Label Readability

{md_table(pairwise, pair_cols)}

## E174 Group Attribution

{md_table(group_focus, [
    "pair",
    "group_kind",
    "group",
    "n_cells",
    "n_rows",
    "expected_delta_focus_mean",
    "abs_expected_share",
    "support_prob_swing_weighted",
    "mean_safe_density",
    "e72_active_rate",
    "context_high_rate",
], n=100)}

## Top E174-vs-E95 Hard-Label Cells

{md_table(top_vs_e95, [
    "pair",
    "sub_idx",
    "target",
    "swing",
    "support_label",
    "p_y1_focus_mean",
    "p_y1_subject",
    "p_y1_nearest_hard085",
], n=25)}

## Top E174-vs-E172 Reopened Cells

{md_table(top_vs_e172, [
    "pair",
    "sub_idx",
    "target",
    "swing",
    "support_label",
    "p_y1_focus_mean",
    "p_y1_subject",
    "p_y1_nearest_hard085",
], n=25)}

## Observed Score Decision

{observed_text}

## Decision

E175 creates no submission. The pre-feedback highest-upside broad expected-score
file is `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`.

- A win below E95 validates partial rollback reopening as public-real.
- A tie or small loss keeps E95 practical and makes E172 the only clean
  same-family contrast.
- A worse-than-E101 result demotes E174 and blocks top-N reopening siblings.
- A worse-than-mixmin result closes E174/E172/E169 same-family broad expected
  score followups unless a new public-independent bad axis explains the miss.
"""
    REPORT_OUT.write_text(report)


def run(score: float | None = None) -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    bands = build_bands()
    pairwise, top_cells = pairwise_metrics(sample, priors)
    p95 = load_prob(E95_FILE, sample)
    p174 = load_prob(E174_FILE, sample)
    p172 = load_prob(E172_FILE, sample)
    p169 = load_prob(E169_FILE, sample)
    groups = e173.build_group_attribution(
        [
            e173.cell_detail("e174_vs_e95", p174, p95, priors),
            e173.cell_detail("e174_vs_e172", p174, p172, priors),
            e173.cell_detail("e174_vs_e169", p174, p169, priors),
        ]
    )
    prior_moments = prior_moment_table(sample)

    observed = classify_score(score, bands) if score is not None else None
    bands.to_csv(BANDS_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    groups.to_csv(GROUP_ATTR_OUT, index=False)
    prior_moments.to_csv(PRIOR_MOMENTS_OUT, index=False)
    if observed is not None:
        pd.DataFrame([observed.to_dict()]).to_csv(OBSERVED_OUT, index=False)
    write_report(bands, pairwise, top_cells, groups, prior_moments, observed)
    print(BANDS_OUT)
    print(PAIRWISE_OUT)
    print(TOP_CELLS_OUT)
    print(GROUP_ATTR_OUT)
    print(PRIOR_MOMENTS_OUT)
    print(REPORT_OUT)
    if observed is not None:
        print(OBSERVED_OUT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Optional observed public LB for E174.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(score=args.score)


if __name__ == "__main__":
    main()
