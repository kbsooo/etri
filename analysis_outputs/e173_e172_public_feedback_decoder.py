#!/usr/bin/env python3
"""E173: pre-public feedback decoder for E172.

E172 turns E169's broad context/veto body into a visible-tail-repaired
candidate. This script fixes the public score interpretation before feedback:
it asks whether E172 wins because the rollback constraint was real, ties
because the broad branch is still underresolved, or loses because the broad body
or visible-prior proxy is wrong.

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


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
E95_EDGE_VS_MIXMIN = E95_PUBLIC - MIXMIN_PUBLIC
E101_DELTA_VS_E95 = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA_VS_E95 = MIXMIN_PUBLIC - E95_PUBLIC

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E172_FILE = "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E169_DENSITY_FILE = "submission_e169_ctx_high_density_p50_51110c7e.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

E167_CELLS = OUT / "e167_broad_survivor_context_alignment_cells.csv"

BANDS_OUT = OUT / "e173_e172_public_feedback_decoder_bands.csv"
PAIRWISE_OUT = OUT / "e173_e172_public_feedback_decoder_pairwise.csv"
TOP_CELLS_OUT = OUT / "e173_e172_public_feedback_decoder_top_cells.csv"
GROUP_ATTR_OUT = OUT / "e173_e172_public_feedback_decoder_group_attribution.csv"
PRIOR_MOMENTS_OUT = OUT / "e173_e172_public_feedback_decoder_prior_moments.csv"
REPORT_OUT = OUT / "e173_e172_public_feedback_decoder_report.md"
OBSERVED_OUT = OUT / "e173_e172_observed_score_decision.csv"

EPS = 1.0e-12


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "tail_repair_breakthrough",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update": "E172 wins beyond ordinary post-E95 scale. The broad body and visible-tail rollback are both public-real.",
        "next_action": "Promote E172 as a new anchor; decompose rollback keep by target/context before considering larger broad moves.",
        "candidate_to_test": "",
        "forbidden_action": "Do not jump to raw E166 or raw E169. The public observation validated the repaired tensor, not the unrolled one.",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": E95_EDGE_VS_MIXMIN,
        "world_update": "E172 wins by at least the E95-over-mixmin edge. The E171 tail rollback constraint is public-readable.",
        "next_action": "Use E172 as broad-branch anchor and test target/context ablations around visible-positive-loss rollback.",
        "candidate_to_test": "conditional:e172_target_context_ablation",
        "forbidden_action": "Do not spend a slot on E169 high-density p50; it does not answer the rollback constraint.",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": E95_EDGE_VS_MIXMIN,
        "delta_hi_inclusive": -3.0e-6,
        "world_update": "E172 is public-positive but still frontier-resolution scale. Tail repair is alive but not a 0.54 path.",
        "next_action": "Promote cautiously. Prefer rollback responsibility analysis before any amplitude increase.",
        "candidate_to_test": "",
        "forbidden_action": "Do not claim broad JEPA is solved; the edge is still hidden-label-resolution limited.",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update": "E172 does not separate from E95. The broad body may be real but public tail labels remain underidentified.",
        "next_action": "Keep E95 as practical frontier. E169 is information-only; raw E166 only tests whether the safety atlas was overconservative.",
        "candidate_to_test": "conditional:E169_or_E166_information_only",
        "forbidden_action": "Do not tune the visible-positive threshold from a tie.",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": E101_DELTA_VS_E95,
        "world_update": "E172 loses to E95 but no worse than E101. Tail repair was insufficient or public labels favored some rolled-back cells.",
        "next_action": "Do not submit E169 automatically. Compare E172-vs-E169 rollback cells; E154 becomes the cleaner conservative branch if using a slot.",
        "candidate_to_test": "conditional:E154_or_raw_E169_by_question",
        "forbidden_action": "Do not conclude the broad body was fake unless E172 also loses beyond mixmin.",
    },
    {
        "outcome": "e101_worse_mixmin_safe",
        "delta_lo_exclusive": E101_DELTA_VS_E95,
        "delta_hi_inclusive": MIXMIN_DELTA_VS_E95,
        "world_update": "E172 is worse than E101 but still mixmin-safe. The visible-tail repair did not fix the public-negative axis.",
        "next_action": "Demote E172/E169 as expected-score files. Prefer E154 if the next public question is conservative repaired-branch structure.",
        "candidate_to_test": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
        "forbidden_action": "Do not rescue with same-family visible-threshold variants without a new axis.",
    },
    {
        "outcome": "branch_loss",
        "delta_lo_exclusive": MIXMIN_DELTA_VS_E95,
        "delta_hi_inclusive": 5.0e-5,
        "world_update": "E172 gives back the E95-over-mixmin gain. The broad context/veto body or visible-tail proxy is public-negative.",
        "next_action": "Close E172/E169 same-family expected-score followups and rebuild the broad safety axis.",
        "candidate_to_test": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
        "forbidden_action": "Do not submit raw E169 or raw E166 unless explicitly accepting high-risk falsification.",
    },
    {
        "outcome": "hard_fail",
        "delta_lo_exclusive": 5.0e-5,
        "delta_hi_inclusive": np.inf,
        "world_update": "E172 is strongly incompatible with public labels. The repaired broad lane missed a major public-negative axis.",
        "next_action": "Close E172/E169/E166 same-family broad-lane followups and use the failure to rebuild bad-axis geometry.",
        "candidate_to_test": "",
        "forbidden_action": "Do not submit threshold, keep-factor, or E169-density siblings.",
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


def target_group(target: str) -> str:
    return "Q" if target.startswith("Q") else "S"


def pairwise_metrics(sample: pd.DataFrame, priors: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    probs = {
        "e95": load_prob(E95_FILE, sample),
        "e172_tail_repair": load_prob(E172_FILE, sample),
        "e169_unrolled": load_prob(E169_FILE, sample),
        "e169_high_density": load_prob(E169_DENSITY_FILE, sample),
        "e166_raw": load_prob(E166_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e101": load_prob(E101_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
    }
    pairs = [
        ("e172_tail_repair", "e95"),
        ("e169_unrolled", "e95"),
        ("e172_tail_repair", "e169_unrolled"),
        ("e172_tail_repair", "e166_raw"),
        ("e172_tail_repair", "e154"),
        ("e172_tail_repair", "e101"),
        ("e172_tail_repair", "mixmin"),
        ("e172_tail_repair", "e169_high_density"),
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


def cell_detail(
    pair: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    priors: dict[str, np.ndarray],
) -> pd.DataFrame:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / e172.N_PUBLIC_CELLS
    dy0_s = dy0 / e172.N_PUBLIC_CELLS
    py = priors["focus_mean"][row_idx, target_idx]
    expected = py * dy1_s + (1.0 - py) * dy0_s
    swing = np.abs(dy1_s - dy0_s)
    support_label = np.where(dy1_s < dy0_s, 1, 0)
    support_prob = np.where(support_label == 1, py, 1.0 - py)
    detail = pd.DataFrame(
        {
            "pair": pair,
            "sub_idx": row_idx.astype(int),
            "target_idx": target_idx.astype(int),
            "target": [TARGETS[j] for j in target_idx],
            "target_group": [target_group(TARGETS[j]) for j in target_idx],
            "delta_y1": dy1_s,
            "delta_y0": dy0_s,
            "swing": swing,
            "support_label": support_label.astype(int),
            "support_prob_focus_mean": support_prob,
            "expected_delta_focus_mean": expected,
        }
    )
    context = pd.read_csv(E167_CELLS, low_memory=False)
    context = context[context["pair"].eq("e166_vs_e95")].copy()
    keep_cols = [
        "sub_idx",
        "target_idx",
        "subject_id",
        "sleep_date",
        "lifelog_date",
        "context_type",
        "pos_bin",
        "edge_like",
        "e72_active",
        "e101_active",
        "all_veto_null",
        "all_safe_density",
        "broad_low_alpha_mass",
        "e101_plausible_mass",
        "benefit_rank",
        "swing_rank",
    ]
    detail = detail.merge(
        context[keep_cols],
        on=["sub_idx", "target_idx"],
        how="left",
        validate="many_to_one",
    )
    detail["between_train_runs"] = detail["context_type"].eq("between_train_runs")
    detail["context_high"] = detail["edge_like"].fillna(False).astype(bool) | detail["between_train_runs"]
    density_rank = detail["all_safe_density"].fillna(0.0).rank(method="first")
    detail["safe_density_bin"] = pd.qcut(
        density_rank,
        q=4,
        labels=["q1_low", "q2", "q3", "q4_high"],
    ).astype(str)
    return detail


def summarize_group(detail: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    total_abs_expected = float(abs(detail["expected_delta_focus_mean"].sum()))
    for keys, part in detail.groupby(group_cols, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        rec = {col: val for col, val in zip(group_cols, keys)}
        expected = float(part["expected_delta_focus_mean"].sum())
        swing_sum = float(part["swing"].sum())
        rec.update(
            {
                "n_cells": int(len(part)),
                "n_rows": int(part["sub_idx"].nunique()),
                "expected_delta_focus_mean": expected,
                "abs_expected_share": float(abs(expected) / max(total_abs_expected, EPS)),
                "swing_sum": swing_sum,
                "top1_swing": float(part["swing"].max()) if len(part) else 0.0,
                "support_prob_swing_weighted": float(np.average(part["support_prob_focus_mean"], weights=part["swing"]))
                if swing_sum > 0
                else np.nan,
                "mean_safe_density": float(part["all_safe_density"].mean()),
                "e72_active_rate": float(part["e72_active"].fillna(False).astype(bool).mean()),
                "context_high_rate": float(part["context_high"].fillna(False).astype(bool).mean()),
            }
        )
        rows.append(rec)
    out = pd.DataFrame(rows)
    return out.sort_values(["expected_delta_focus_mean", "n_cells"], ascending=[True, False])


def build_group_attribution(details: list[pd.DataFrame]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    detail = pd.concat(details, ignore_index=True)
    for pair, part in detail.groupby("pair", sort=True):
        for kind, cols in [
            ("target", ["target"]),
            ("target_group", ["target_group"]),
            ("context_type", ["context_type"]),
            ("edge_like", ["edge_like"]),
            ("e72_active", ["e72_active"]),
            ("target_context", ["target", "context_type"]),
            ("target_safety", ["target", "safe_density_bin"]),
        ]:
            one = summarize_group(part, cols)
            one.insert(0, "pair", pair)
            one.insert(1, "group_kind", kind)
            one["group"] = one[cols].astype(str).agg(":".join, axis=1)
            frames.append(one)
    return pd.concat(frames, ignore_index=True, sort=False)


def prior_moment_table(sample: pd.DataFrame) -> pd.DataFrame:
    e95 = load_prob(E95_FILE, sample)
    preds = {
        "e169_unrolled_vs_e95": load_prob(E169_FILE, sample),
        "e172_tail_repair_vs_e95": load_prob(E172_FILE, sample),
    }
    cells = e171.build_cells()
    rows: list[dict[str, Any]] = []
    for candidate, pred in preds.items():
        rec: dict[str, Any] = {"candidate": candidate}
        for prior in e172.PRIORS:
            rec.update(e172.prior_moments(cells, pred, e95, prior))
        rows.append(rec)
    out = pd.DataFrame(rows)
    base = out[out["candidate"].eq("e169_unrolled_vs_e95")].iloc[0]
    for col in out.columns:
        if col.startswith(("mean_delta_", "p95_delta_norm_", "worse_than_e101_norm_")):
            out[f"delta_{col}_vs_e169"] = out[col] - float(base[col])
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
        "delta_mean_delta_visible_mean_vs_e169",
        "delta_p95_delta_norm_visible_mean_vs_e169",
        "delta_worse_than_e101_norm_visible_mean_vs_e169",
    ]
    group_focus = groups[
        groups["pair"].isin(["e172_vs_e95", "e172_vs_e169"])
        & groups["group_kind"].isin(["target", "context_type", "e72_active", "target_context"])
    ].sort_values(["pair", "group_kind", "expected_delta_focus_mean"])
    top_vs_e95 = top_cells[top_cells["pair"].eq("e172_tail_repair_vs_e95")].sort_values("swing", ascending=False)
    top_vs_e169 = top_cells[top_cells["pair"].eq("e172_tail_repair_vs_e169_unrolled")].sort_values("swing", ascending=False)
    observed_text = "_No observed E172 public score supplied._"
    if observed is not None:
        observed_text = md_table(pd.DataFrame([observed.to_dict()]), None, n=1)

    report = f"""# E173 E172 Public Feedback Decoder

## Question

If `submission_e172_vis_pos_all_keep0p25_d90f4407.csv` is submitted, how should
its public LB update the broad-branch world model without post-hoc threshold
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

## Prior-Moment Tail Repair

{md_table(prior_moments, moment_cols)}

## Pairwise Hard-Label Readability

{md_table(pairwise, pair_cols)}

## E172 Group Attribution

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
], n=80)}

## Top E172-vs-E95 Hard-Label Cells

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

## Top E172-vs-E169 Rollback Cells

{md_table(top_vs_e169, [
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

E173 creates no submission. The pre-feedback first broad expected-score file is
`analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`.

- A win below E95 validates visible-positive-loss rollback as the missing broad
  branch constraint.
- A tie or small loss keeps E95 practical and makes raw E169 information-only.
- A worse-than-E101 result demotes visible-tail repair and shifts priority to
  E154 or a new broad safety-axis search.
- A worse-than-mixmin result blocks E172/E169/E166 same-family broad followups.
"""
    REPORT_OUT.write_text(report)


def run(score: float | None = None) -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    bands = build_bands()
    pairwise, top_cells = pairwise_metrics(sample, priors)
    p95 = load_prob(E95_FILE, sample)
    p172 = load_prob(E172_FILE, sample)
    p169 = load_prob(E169_FILE, sample)
    groups = build_group_attribution(
        [
            cell_detail("e172_vs_e95", p172, p95, priors),
            cell_detail("e172_vs_e169", p172, p169, priors),
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
    parser.add_argument("--score", type=float, default=None, help="Optional observed public LB for E172.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(score=args.score)


if __name__ == "__main__":
    main()
