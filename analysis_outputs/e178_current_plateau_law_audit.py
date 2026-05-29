#!/usr/bin/env python3
"""E178: current post-E95 plateau law audit.

The new E101 public observation is not a new score to chase; it is a constraint
on the hidden public world. This audit compresses the current E95/E101/E166-
E176 evidence into one falsifiable statement:

    The 0.57629 plateau is no longer explained by lack of signal alone. A broad
    hidden body exists, but the remaining public-readable edge is dominated by
    a few hard-label cells and Q/S tail calibration, below the resolution of the
    selectors that ranked earlier candidates.

No model is trained and no submission is created.
"""

from __future__ import annotations

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
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
A2C8_PUBLIC = 0.5774393210

E95_FILE = "submission_e95_hardtail_541e3973.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E174_FILE = "submission_e174_ro_fc_top75_to1p0_95638e73.csv"
E176_FILE = "submission_e176_abl_q2_to0p75_91e49725.csv"

E176_PAIRWISE = OUT / "e177_e176_public_feedback_decoder_pairwise.csv"
E176_PRIOR_MOMENTS = OUT / "e177_e176_public_feedback_decoder_prior_moments.csv"
E98_SELECTOR = OUT / "e98_e95_updated_selector_model_scores.csv"

METRICS_OUT = OUT / "e178_current_plateau_law_candidate_metrics.csv"
EVIDENCE_OUT = OUT / "e178_current_plateau_law_evidence.csv"
CATEGORY_OUT = OUT / "e178_current_plateau_law_category_status.csv"
REPORT_OUT = OUT / "e178_current_plateau_law_report.md"

EPS = 1.0e-12


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return np.clip(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def target_move_shares(p_new: np.ndarray, p_base: np.ndarray) -> dict[str, float]:
    move = np.abs(logit(p_new) - logit(p_base))
    total = float(move.sum())
    if total <= EPS:
        return {
            "q_share": 0.0,
            "s_share": 0.0,
            "q2s3_share": 0.0,
            "s3_share": 0.0,
            "max_target_share": 0.0,
            "max_target": "",
        }
    shares = {target: float(move[:, i].sum() / total) for i, target in enumerate(TARGETS)}
    q_share = sum(shares[t] for t in ["Q1", "Q2", "Q3"])
    s_share = sum(shares[t] for t in ["S1", "S2", "S3", "S4"])
    max_target = max(shares, key=shares.get)
    return {
        "q_share": float(q_share),
        "s_share": float(s_share),
        "q2s3_share": float(shares["Q2"] + shares["S3"]),
        "s3_share": float(shares["S3"]),
        "max_target_share": float(shares[max_target]),
        "max_target": max_target,
    }


def geometry_metrics(
    pred: np.ndarray,
    e95: np.ndarray,
    bad_names: list[str],
    bad_basis: np.ndarray,
    refs: dict[str, np.ndarray],
) -> dict[str, Any]:
    move = (logit(pred) - logit(e95)).reshape(-1)
    norm = float(np.linalg.norm(move))
    bad_energy, bad_resid = e165.span_energy(move, bad_basis)
    bad_cos: dict[str, float] = {}
    for i, name in enumerate(bad_names):
        bad_cos[name] = e165.cosine(move, bad_basis[i])
    max_bad_axis = max(bad_cos, key=bad_cos.get) if bad_cos else ""
    out: dict[str, Any] = {
        "move_norm_vs_e95": norm,
        "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move))),
        "max_abs_logit_move_vs_e95": float(np.max(np.abs(move))) if move.size else 0.0,
        "bad_span_energy": float(bad_energy),
        "bad_span_residual": float(bad_resid),
        "max_bad_axis": max_bad_axis,
        "max_bad_cos": float(bad_cos[max_bad_axis]) if max_bad_axis else 0.0,
        "cos_e101_axis": e165.cosine(move, (logit(refs["e101"]) - logit(e95)).reshape(-1)),
        "cos_mixmin_axis": e165.cosine(move, (logit(refs["mixmin"]) - logit(e95)).reshape(-1)),
        "cos_e154_axis": e165.cosine(move, (logit(refs["e154"]) - logit(e95)).reshape(-1)),
    }
    for name, cos_value in bad_cos.items():
        out[f"cos_bad_{name}"] = float(cos_value)
    return out


def candidate_rows(sample: pd.DataFrame) -> pd.DataFrame:
    priors = e162.prior_arrays(sample)
    e95 = load_prob(E95_FILE, sample)
    z_e95 = logit(e95)
    bad_names, bad_basis = e165.bad_axes(sample, z_e95)
    refs = {
        "e95": e95,
        "e101": load_prob(E101_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
    }
    specs = [
        {
            "candidate": "mixmin",
            "file": MIXMIN_FILE,
            "stage": "pre-hardtail anchor",
            "known_public_lb": MIXMIN_PUBLIC,
            "claim": "binary/prior mix anchor before hardtail localization",
        },
        {
            "candidate": "e101_q2s3tail",
            "file": E101_FILE,
            "stage": "resolved negative sensor",
            "known_public_lb": E101_PUBLIC,
            "claim": "Q2/S3 active-tail rollback after E95",
        },
        {
            "candidate": "e154_s3repair",
            "file": E154_FILE,
            "stage": "conservative sibling",
            "known_public_lb": np.nan,
            "claim": "S3-active boundary repair branch",
        },
        {
            "candidate": "e166_broad_raw",
            "file": E166_FILE,
            "stage": "broad body before safety",
            "known_public_lb": np.nan,
            "claim": "large broad hidden body, unsafe without context/tail controls",
        },
        {
            "candidate": "e169_context_veto",
            "file": E169_FILE,
            "stage": "context safety mask",
            "known_public_lb": np.nan,
            "claim": "broad body after context/veto repair",
        },
        {
            "candidate": "e172_tail_repair",
            "file": E172_FILE,
            "stage": "visible-tail repair",
            "known_public_lb": np.nan,
            "claim": "rollback public-visible critical tail risk",
        },
        {
            "candidate": "e174_full_q2_reopen",
            "file": E174_FILE,
            "stage": "partial reopen max-edge",
            "known_public_lb": np.nan,
            "claim": "recover expected body edge by reopening top rollback cells",
        },
        {
            "candidate": "e176_q2_underopen",
            "file": E176_FILE,
            "stage": "risk-adjusted current candidate",
            "known_public_lb": np.nan,
            "claim": "keep E174 body but damp reopened Q2 amplitude",
        },
    ]
    rows: list[dict[str, Any]] = []
    top_rows: list[pd.DataFrame] = []
    for spec in specs:
        pred = load_prob(str(spec["file"]), sample)
        rec, top = e162.pair_metrics(str(spec["candidate"]), "e95", pred, e95, priors)
        rec.update(spec)
        rec["known_delta_vs_e95"] = (
            float(spec["known_public_lb"]) - E95_PUBLIC if pd.notna(spec["known_public_lb"]) else np.nan
        )
        rec["known_delta_vs_mixmin"] = (
            float(spec["known_public_lb"]) - MIXMIN_PUBLIC if pd.notna(spec["known_public_lb"]) else np.nan
        )
        rec.update(target_move_shares(pred, e95))
        rec.update(geometry_metrics(pred, e95, bad_names, bad_basis, refs))
        expected = float(rec.get("expected_delta_focus_mean", np.nan))
        rec["abs_expected_focus"] = abs(expected) if np.isfinite(expected) else np.nan
        rec["top1_swing_over_e95_edge"] = float(rec["top1_swing"] / abs(E95_PUBLIC - MIXMIN_PUBLIC))
        rec["top5_swing_over_e95_edge"] = float(rec["top5_swing"] / abs(E95_PUBLIC - MIXMIN_PUBLIC))
        rec["selector_p90_over_expected_focus"] = np.nan
        rec["hard_label_resolution_warning"] = bool(
            int(rec.get("cells_for_e95_edge", 9999)) > 0 and int(rec.get("cells_for_e95_edge", 9999)) <= 4
        )
        rows.append(rec)
        if not top.empty:
            top["candidate"] = str(spec["candidate"])
            top_rows.append(top)
    out = pd.DataFrame(rows)

    if E98_SELECTOR.exists():
        selector = pd.read_csv(E98_SELECTOR).sort_values("p90_abs_error").iloc[0]
        p90 = float(selector["p90_abs_error"])
        out["selector_p90_over_expected_focus"] = p90 / out["abs_expected_focus"].replace(0.0, np.nan)
    return out.sort_values(["known_public_lb", "expected_delta_focus_mean"], na_position="last").reset_index(drop=True)


def evidence_rows(metrics: pd.DataFrame) -> pd.DataFrame:
    selector = pd.read_csv(E98_SELECTOR).sort_values("p90_abs_error").iloc[0]
    selector_p90 = float(selector["p90_abs_error"])
    selector_mae = float(selector["mae"])
    e95_edge = abs(E95_PUBLIC - MIXMIN_PUBLIC)
    e101_loss = E101_PUBLIC - E95_PUBLIC
    row_e176 = metrics[metrics["candidate"].eq("e176_q2_underopen")].iloc[0]
    row_e174 = metrics[metrics["candidate"].eq("e174_full_q2_reopen")].iloc[0]
    row_e166 = metrics[metrics["candidate"].eq("e166_broad_raw")].iloc[0]
    row_e169 = metrics[metrics["candidate"].eq("e169_context_veto")].iloc[0]
    row_e101 = metrics[metrics["candidate"].eq("e101_q2s3tail")].iloc[0]

    e176_pair = pd.read_csv(E176_PAIRWISE)
    e176_vs_e174 = e176_pair[
        e176_pair["new"].eq("e176_q2_underopen") & e176_pair["base"].eq("e174_full_q2")
    ].iloc[0]
    q2_damping_cost = float(e176_vs_e174["expected_delta_focus_mean"])

    rows = [
        {
            "evidence": "frontier_edge_e95_vs_mixmin",
            "value": e95_edge,
            "unit": "logloss",
            "read": "E95 beat mixmin by a public-real but tiny hardtail edge.",
        },
        {
            "evidence": "e101_loss_vs_e95",
            "value": e101_loss,
            "unit": "logloss",
            "read": "Q2/S3 tail rollback returned 59.02% of the E95-over-mixmin gain; the axis is fragile.",
        },
        {
            "evidence": "selector_p90_over_e95_edge",
            "value": selector_p90 / e95_edge,
            "unit": "ratio",
            "read": "Known-LB selector p90 error is far too coarse for post-E95 ranking.",
        },
        {
            "evidence": "selector_mae_over_e95_edge",
            "value": selector_mae / e95_edge,
            "unit": "ratio",
            "read": "Even average selector error exceeds the frontier edge by an order of magnitude.",
        },
        {
            "evidence": "e166_broad_expected_over_e95_edge",
            "value": abs(float(row_e166["expected_delta_focus_mean"])) / e95_edge,
            "unit": "ratio",
            "read": "A broad body exists in local/focus-prior space, but it is unsafe before safety controls.",
        },
        {
            "evidence": "e169_context_expected_over_e95_edge",
            "value": abs(float(row_e169["expected_delta_focus_mean"])) / e95_edge,
            "unit": "ratio",
            "read": "Context/veto repair preserves a broad edge larger than E95's public gain.",
        },
        {
            "evidence": "e176_expected_over_e95_edge",
            "value": abs(float(row_e176["expected_delta_focus_mean"])) / e95_edge,
            "unit": "ratio",
            "read": "Current E176 candidate is still broad on expected score, but public resolution is cell-scale.",
        },
        {
            "evidence": "e176_cells_for_e95_edge",
            "value": float(row_e176["cells_for_e95_edge"]),
            "unit": "cells",
            "read": "Only a few row-target hard labels can swing an entire E95-over-mixmin edge.",
        },
        {
            "evidence": "e101_cells_for_e95_edge",
            "value": float(row_e101["cells_for_e95_edge"]),
            "unit": "cells",
            "read": "Resolved E101 loss sits in the same small-cell readability regime.",
        },
        {
            "evidence": "e176_q2_damping_cost_over_e95_edge",
            "value": q2_damping_cost / e95_edge,
            "unit": "ratio",
            "read": "The E176-vs-E174 Q2 damping decision is below public resolution from one scalar LB.",
        },
        {
            "evidence": "e176_bad_cos_reduction_vs_e174",
            "value": float(row_e174["max_bad_cos"] - row_e176["max_bad_cos"]),
            "unit": "cosine_delta",
            "read": "E176 buys a small but real LeJEPA-style bad-axis safety improvement over E174.",
        },
        {
            "evidence": "e176_q2s3_share_reduction_vs_e174",
            "value": float(row_e174["q2s3_share"] - row_e176["q2s3_share"]),
            "unit": "share_delta",
            "read": "The live candidate deliberately spends less Q2/S3 amplitude than E174.",
        },
    ]
    return pd.DataFrame(rows)


def category_status() -> pd.DataFrame:
    rows = [
        {
            "category": "A_data_signal_shortage",
            "status": "evidence_mixed",
            "reason": "E166/E169/E176 have large focus-prior expected edges, so signal is not absent; public-readable residuals are still cell-scale.",
            "kill_condition": "A non-public-aware validation object ranks E95/E101/E176 correctly with error below 5e-6.",
        },
        {
            "category": "B_validation_mismatch",
            "status": "evidence_strong",
            "reason": "Known-LB selector p90 error is over 50x the E95 edge and E101 local stress was optimistic.",
            "kill_condition": "Independent local stress predicts the next public delta within the 3e-6 tie band.",
        },
        {
            "category": "C_public_subset_mismatch",
            "status": "evidence_strong_but_underidentified",
            "reason": "E101 lost while preserving part of mixmin gain; public realizes some tail cells differently from broad local priors.",
            "kill_condition": "E176 cleanly wins without new public-subset machinery, implying the mismatch was mostly Q2 amplitude.",
        },
        {
            "category": "D_target_prior_calibration_tail",
            "status": "evidence_strong",
            "reason": "Hardtail E95 survives, E101 Q2/S3 rollback fails, and E176 only changes Q2 damping to buy safety.",
            "kill_condition": "A broad all-target move beats E95 while increasing Q2/S3 and bad-axis exposure.",
        },
        {
            "category": "E_representation_capacity",
            "status": "evidence_weak",
            "reason": "Representation/broad body exists, but LeJEPA-style bad-axis and tail-risk constraints dominate candidate acceptance.",
            "kill_condition": "A new latent creates a non-collinear movement with public-safe tail metrics and material expected edge.",
        },
        {
            "category": "F_candidate_selection",
            "status": "evidence_partial",
            "reason": "E176 is a better risk-adjusted choice than E174, but the difference is too small to rank from current public sensors.",
            "kill_condition": "E176 public result falls into a clean-win or branch-loss band and separates the family.",
        },
    ]
    return pd.DataFrame(rows)


def write_report(metrics: pd.DataFrame, evidence: pd.DataFrame, categories: pd.DataFrame) -> None:
    e95_edge = abs(E95_PUBLIC - MIXMIN_PUBLIC)
    e101_loss = E101_PUBLIC - E95_PUBLIC
    selector_ratio = float(evidence[evidence["evidence"].eq("selector_p90_over_e95_edge")]["value"].iloc[0])
    e176 = metrics[metrics["candidate"].eq("e176_q2_underopen")].iloc[0]
    e174 = metrics[metrics["candidate"].eq("e174_full_q2_reopen")].iloc[0]
    e166 = metrics[metrics["candidate"].eq("e166_broad_raw")].iloc[0]

    report = f"""# E178 Current Plateau Law Audit

## Question

Given the resolved E101 public LB (`{E101_PUBLIC:.10f}`) and the current E95
frontier (`{E95_PUBLIC:.10f}`), what is the shortest law that explains why the
post-E95 plateau exists?

## Compressed Law

The current plateau is not mainly a model-capacity wall. A broad hidden body is
visible (`E166` focus-prior edge `{float(e166['expected_delta_focus_mean']):.9f}`),
but public improvement after E95 is filtered through a few hard-label cells and
target-tail calibration. Ordinary CV/proxy ranking is too coarse: the best
known-LB selector p90 error is `{selector_ratio:.2f}x` the E95-over-mixmin edge
(`{e95_edge:.10f}`).

E101 is now the critical negative sensor: it loses to E95 by `{e101_loss:.10f}`
while still beating mixmin. That means the Q2/S3 tail direction was not useless,
but it was not public-positive enough to become the next frontier.

## Candidate Geometry

{md_table(metrics, [
    'candidate',
    'stage',
    'known_public_lb',
    'known_delta_vs_e95',
    'expected_delta_focus_mean',
    'moved_cells',
    'moved_rows',
    'cells_for_e95_edge',
    'cells_to_flip_expected_focus_mean',
    'top1_swing_over_e95_edge',
    'q2s3_share',
    'bad_span_energy',
    'max_bad_axis',
    'max_bad_cos',
    'hard_label_resolution_warning',
], 30)}

## Evidence

{md_table(evidence, ['evidence', 'value', 'unit', 'read'], 40)}

## Bottleneck Status

{md_table(categories, ['category', 'status', 'reason', 'kill_condition'], 20)}

## E174 vs E176 Reading

E174 has the slightly better focus-prior edge
(`{float(e174['expected_delta_focus_mean']):.9f}`), but E176 keeps almost the
same broad body (`{float(e176['expected_delta_focus_mean']):.9f}`) while reducing
Q2/S3 share from `{float(e174['q2s3_share']):.6f}` to
`{float(e176['q2s3_share']):.6f}` and max bad-axis cosine from
`{float(e174['max_bad_cos']):.6f}` to `{float(e176['max_bad_cos']):.6f}`.

The E176-vs-E174 Q2 damping cost is below the scale that a single public score
can reliably decode. Therefore the current best submission action remains:
submit E176 if spending a slot, then decode the result with E177. Do not create
another same-family keep-factor sibling before that observation.

## What Would Kill This Law

- E176 cleanly beats E95 by at least the E95-over-mixmin edge: Q/S-asymmetric
  broad reopening is more real than the hard-label-resolution warning.
- E176 loses worse than E101: E174/E176 broad partial reopening is public
  misaligned and the branch should be closed.
- A new latent movement produces material expected edge, low Q2/S3 exposure,
  and low bad-axis energy while not depending on known public scores.

## Next Most Informative Action

No new submission is created here. The only current risk-adjusted public sensor
is still:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

Its claim is not "E176 is certainly better"; its claim is "the broad hidden body
survives if Q2 is under-opened." The public response will decide whether the
plateau is mostly target-amplitude calibration or a deeper public-subset/block
mismatch.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    metrics = candidate_rows(sample)
    evidence = evidence_rows(metrics)
    categories = category_status()
    metrics.to_csv(METRICS_OUT, index=False)
    evidence.to_csv(EVIDENCE_OUT, index=False)
    categories.to_csv(CATEGORY_OUT, index=False)
    write_report(metrics, evidence, categories)


if __name__ == "__main__":
    main()
