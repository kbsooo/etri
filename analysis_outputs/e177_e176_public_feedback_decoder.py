#!/usr/bin/env python3
"""E177: pre-public feedback decoder for E176.

E176 is the risk-adjusted sibling of E174: it keeps the partial-reopen body but
dampens only the reopened Q2 cells. This script fixes how to interpret a future
E176 public LB before that score is known.

No submission is created.
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
E176_FILE = "submission_e176_abl_q2_to0p75_91e49725.csv"
E174_FILE = "submission_e174_ro_fc_top75_to1p0_95638e73.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

BANDS_OUT = OUT / "e177_e176_public_feedback_decoder_bands.csv"
PAIRWISE_OUT = OUT / "e177_e176_public_feedback_decoder_pairwise.csv"
TOP_CELLS_OUT = OUT / "e177_e176_public_feedback_decoder_top_cells.csv"
GROUP_ATTR_OUT = OUT / "e177_e176_public_feedback_decoder_group_attribution.csv"
PRIOR_MOMENTS_OUT = OUT / "e177_e176_public_feedback_decoder_prior_moments.csv"
TARGET_CONTRAST_OUT = OUT / "e177_e176_public_feedback_decoder_target_contrast.csv"
REPORT_OUT = OUT / "e177_e176_public_feedback_decoder_report.md"
OBSERVED_OUT = OUT / "e177_e176_observed_score_decision.csv"

EPS = 1.0e-12


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "q2_underopen_breakthrough",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update": "E176 wins beyond normal post-E95 scale. The broad body, visible-tail repair, partial reopening, and Q2 under-opening are all public-real.",
        "next_action": "Promote E176 as the broad anchor. Next experiment should decompose S3/S2/S1-heavy reopening, not increase Q2.",
        "candidate_to_test": "conditional:e176_non_q2_reopen_decomposition",
        "forbidden_action": "Do not submit E174 merely because it has a slightly stronger focus prior edge; the observed win says the Q2 risk cut mattered.",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": E95_EDGE_VS_MIXMIN,
        "world_update": "E176 wins by at least the E95-over-mixmin edge. Q/S-asymmetric partial reopening is public-readable.",
        "next_action": "Use E176 as the expected-score anchor and treat E174 as a max-edge contrast only.",
        "candidate_to_test": "conditional:e176_component_responsibility_audit",
        "forbidden_action": "Do not reopen Q2 back to E174 without an independent reason.",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": E95_EDGE_VS_MIXMIN,
        "delta_hi_inclusive": -3.0e-6,
        "world_update": "E176 is public-positive but still hidden-hard-label-resolution scale. Q2 damping is plausible but not fully resolved.",
        "next_action": "Promote cautiously. Compare E176 against E174 only if a second public slot is explicitly a Q2-amplitude test.",
        "candidate_to_test": "conditional:e174_vs_e176_q2_amplitude_sensor",
        "forbidden_action": "Do not infer a broad 0.54 path from a micro-win; the edge can still be one-cell driven.",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update": "E176 does not separate from E95. The partial-reopen family is underresolved or its body gain cancels residual Q/S tail risk.",
        "next_action": "Keep E95 practical. If testing the same family again, use E172 only as the safer contrast or E174 only as the deliberate Q2 full-reopen contrast.",
        "candidate_to_test": "conditional:e172_or_e174_by_question",
        "forbidden_action": "Do not tune Q2 keep factors from a tie.",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": E101_DELTA_VS_E95,
        "world_update": "E176 loses to E95 but no worse than E101. Q2 damping was not enough to make the broad partial-reopen family public-positive.",
        "next_action": "Use E172 as the cleaner same-family contrast only if the next question is broad-tail repair; otherwise shift to E154/conservative branch.",
        "candidate_to_test": "conditional:E172_or_E154_by_question",
        "forbidden_action": "Do not make another E176 sibling by moving the Q2 keep factor.",
    },
    {
        "outcome": "e101_worse_mixmin_safe",
        "delta_lo_exclusive": E101_DELTA_VS_E95,
        "delta_hi_inclusive": MIXMIN_DELTA_VS_E95,
        "world_update": "E176 is worse than E101 but still mixmin-safe. Even the damped Q2 partial reopen likely remains public-misaligned.",
        "next_action": "Demote the E174/E176 partial-reopen branch. Prefer E154 if another expected-score file is needed.",
        "candidate_to_test": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
        "forbidden_action": "Do not submit E174 next unless the sole goal is proving full Q2 reopening, not score improvement.",
    },
    {
        "outcome": "branch_loss",
        "delta_lo_exclusive": MIXMIN_DELTA_VS_E95,
        "delta_hi_inclusive": 5.0e-5,
        "world_update": "E176 gives back the E95-over-mixmin gain. The same-family broad partial-reopen lane is not expected-score safe.",
        "next_action": "Close E176/E174/E172/E169 as expected-score followups and rebuild the bad-axis model.",
        "candidate_to_test": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
        "forbidden_action": "Do not submit E169 or E166 unless explicitly spending a falsification slot.",
    },
    {
        "outcome": "hard_fail",
        "delta_lo_exclusive": 5.0e-5,
        "delta_hi_inclusive": np.inf,
        "world_update": "E176 is strongly incompatible with public labels. Q2 damping did not address the dominant negative axis.",
        "next_action": "Close the same-family broad reopen expected-score lane and search for a new non-collinear latent.",
        "candidate_to_test": "",
        "forbidden_action": "Do not create threshold, keep-factor, or target-drop siblings.",
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
        "e176_q2_underopen": load_prob(E176_FILE, sample),
        "e174_full_q2": load_prob(E174_FILE, sample),
        "e172_tail_repair": load_prob(E172_FILE, sample),
        "e169_unrolled": load_prob(E169_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e101": load_prob(E101_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
    }
    pairs = [
        ("e176_q2_underopen", "e95"),
        ("e176_q2_underopen", "e174_full_q2"),
        ("e174_full_q2", "e176_q2_underopen"),
        ("e176_q2_underopen", "e172_tail_repair"),
        ("e176_q2_underopen", "e169_unrolled"),
        ("e176_q2_underopen", "e154"),
        ("e176_q2_underopen", "e101"),
        ("e176_q2_underopen", "mixmin"),
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
        "e174_full_q2_vs_e95": load_prob(E174_FILE, sample),
        "e176_q2_underopen_vs_e95": load_prob(E176_FILE, sample),
    }
    cells = e171.build_cells()
    rows: list[dict[str, Any]] = []
    for candidate, pred in preds.items():
        rec: dict[str, Any] = {"candidate": candidate}
        for prior in e172.PRIORS:
            rec.update(e172.prior_moments(cells, pred, e95, prior))
        rows.append(rec)
    out = pd.DataFrame(rows)
    base_e172 = out[out["candidate"].eq("e172_tail_repair_vs_e95")].iloc[0]
    base_e174 = out[out["candidate"].eq("e174_full_q2_vs_e95")].iloc[0]
    for col in out.columns:
        if col.startswith(("mean_delta_", "p95_delta_norm_", "worse_than_e101_norm_")):
            out[f"delta_{col}_vs_e172"] = out[col] - float(base_e172[col])
            out[f"delta_{col}_vs_e174"] = out[col] - float(base_e174[col])
    return out


def target_contrast(sample: pd.DataFrame, priors: dict[str, np.ndarray]) -> pd.DataFrame:
    p176 = load_prob(E176_FILE, sample)
    p174 = load_prob(E174_FILE, sample)
    p172 = load_prob(E172_FILE, sample)
    p95 = load_prob(E95_FILE, sample)
    details = [
        e173.cell_detail("e176_vs_e174_q2_damping", p176, p174, priors),
        e173.cell_detail("e174_vs_e172_full_reopen", p174, p172, priors),
        e173.cell_detail("e176_vs_e172_q2_underopen_reopen", p176, p172, priors),
        e173.cell_detail("e176_vs_e95_full_move", p176, p95, priors),
    ]
    rows: list[pd.DataFrame] = []
    for detail in details:
        if detail.empty:
            continue
        one = (
            detail.groupby(["pair", "target"], dropna=False)
            .agg(
                n_cells=("target", "size"),
                n_rows=("sub_idx", "nunique"),
                expected_delta_focus_mean=("expected_delta_focus_mean", "sum"),
                swing_sum=("swing", "sum"),
                top1_swing=("swing", "max"),
                support_prob_swing_weighted=(
                    "support_prob_focus_mean",
                    lambda s: float(np.average(s, weights=detail.loc[s.index, "swing"]))
                    if float(detail.loc[s.index, "swing"].sum()) > 0
                    else np.nan,
                ),
                e72_active_rate=("e72_active", lambda s: float(s.fillna(False).astype(bool).mean())),
                mean_safe_density=("all_safe_density", "mean"),
            )
            .reset_index()
        )
        rows.append(one)
    return pd.concat(rows, ignore_index=True).sort_values(["pair", "expected_delta_focus_mean"])


def write_report(
    bands: pd.DataFrame,
    pairwise: pd.DataFrame,
    top_cells: pd.DataFrame,
    groups: pd.DataFrame,
    prior_moments: pd.DataFrame,
    target_effect: pd.DataFrame,
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
        "delta_mean_delta_focus_mean_vs_e174",
        "delta_p95_delta_norm_visible_mean_vs_e174",
        "delta_worse_than_e101_norm_visible_mean_vs_e174",
        "delta_mean_delta_focus_mean_vs_e172",
    ]
    group_focus = groups[
        groups["pair"].isin(
            [
                "e176_vs_e95",
                "e176_vs_e174",
                "e176_vs_e172",
                "e174_vs_e172",
            ]
        )
        & groups["group_kind"].isin(["target", "target_group", "context_type", "e72_active", "target_context"])
    ].sort_values(["pair", "group_kind", "expected_delta_focus_mean"])
    top_vs_e95 = top_cells[top_cells["pair"].eq("e176_q2_underopen_vs_e95")].sort_values("swing", ascending=False)
    top_vs_e174 = top_cells[top_cells["pair"].eq("e176_q2_underopen_vs_e174_full_q2")].sort_values(
        "swing", ascending=False
    )
    observed_text = "_No observed E176 public score supplied._"
    if observed is not None:
        observed_text = md_table(pd.DataFrame([observed.to_dict()]), None, n=1)

    report = f"""# E177 E176 Public Feedback Decoder

## Question

If `submission_e176_abl_q2_to0p75_91e49725.csv` is submitted, how should its
public LB update the current broad-branch world model without post-hoc Q2
keep-factor tuning?

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

## Prior-Moment Q2 Damping Tradeoff

{md_table(prior_moments, moment_cols)}

## Pairwise Hard-Label Readability

{md_table(pairwise, pair_cols)}

## Target Contrast

{md_table(target_effect, [
    "pair",
    "target",
    "n_cells",
    "n_rows",
    "expected_delta_focus_mean",
    "swing_sum",
    "top1_swing",
    "support_prob_swing_weighted",
    "e72_active_rate",
    "mean_safe_density",
], n=80)}

## E176 Group Attribution

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
], n=120)}

## Top E176-vs-E95 Hard-Label Cells

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

## Top E176-vs-E174 Q2-Damping Cells

{md_table(top_vs_e174, [
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

E177 creates no submission. It locks the interpretation of
`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`.

- A win below E95 validates Q/S-asymmetric partial reopening.
- A tie or small loss keeps E95 practical and makes E172/E174 only contrast
  sensors, not automatic next submissions.
- A worse-than-E101 result demotes the damped partial-reopen family.
- If E176 loses but E174 later wins, the full Q2 reopening was public-real; if
  both lose, the whole partial-reopen family is public-misaligned.
"""
    REPORT_OUT.write_text(report)


def run(score: float | None = None) -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    bands = build_bands()
    pairwise, top_cells = pairwise_metrics(sample, priors)
    p95 = load_prob(E95_FILE, sample)
    p176 = load_prob(E176_FILE, sample)
    p174 = load_prob(E174_FILE, sample)
    p172 = load_prob(E172_FILE, sample)
    groups = e173.build_group_attribution(
        [
            e173.cell_detail("e176_vs_e95", p176, p95, priors),
            e173.cell_detail("e176_vs_e174", p176, p174, priors),
            e173.cell_detail("e176_vs_e172", p176, p172, priors),
            e173.cell_detail("e174_vs_e172", p174, p172, priors),
        ]
    )
    prior_moments = prior_moment_table(sample)
    target_effect = target_contrast(sample, priors)

    observed = classify_score(score, bands) if score is not None else None
    bands.to_csv(BANDS_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    groups.to_csv(GROUP_ATTR_OUT, index=False)
    prior_moments.to_csv(PRIOR_MOMENTS_OUT, index=False)
    target_effect.to_csv(TARGET_CONTRAST_OUT, index=False)
    if observed is not None:
        pd.DataFrame([observed.to_dict()]).to_csv(OBSERVED_OUT, index=False)
    write_report(bands, pairwise, top_cells, groups, prior_moments, target_effect, observed)
    print(BANDS_OUT)
    print(PAIRWISE_OUT)
    print(TOP_CELLS_OUT)
    print(GROUP_ATTR_OUT)
    print(PRIOR_MOMENTS_OUT)
    print(TARGET_CONTRAST_OUT)
    print(REPORT_OUT)
    if observed is not None:
        print(OBSERVED_OUT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Optional observed public LB for E176.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(score=args.score)


if __name__ == "__main__":
    main()
