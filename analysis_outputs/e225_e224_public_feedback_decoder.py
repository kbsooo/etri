#!/usr/bin/env python3
"""E225: pre-public feedback decoder for the E224 JEPA candidate.

E224 selected a capped-Q3 E211 translator:

    submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv

This script does not train a model and does not create a submission. It locks
how a future public LB for E224 should be interpreted before the score is
known, so the next action is not chosen by post-hoc scalar intuition.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E216_PUBLIC = 0.5772865088

E95_DELTA_VS_MIXMIN = E95_PUBLIC - MIXMIN_PUBLIC
E101_DELTA_VS_E95 = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA_VS_E95 = MIXMIN_PUBLIC - E95_PUBLIC
E216_DELTA_VS_E95 = E216_PUBLIC - E95_PUBLIC

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E211_FILE = "submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv"
E211_E95_FILE = "submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv"
E216_FILE = "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E223_FILE = "submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E224_E95_FILE = "submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv"

E224_SELECTED = OUT / "e224_e211_q3_scale_pareto_selected.csv"
E224_SUMMARY = OUT / "e224_e211_q3_scale_pareto_summary.csv"

ROUTEBOOK_OUT = OUT / "e225_e224_public_feedback_decoder_routebook.csv"
EXAMPLES_OUT = OUT / "e225_e224_public_feedback_decoder_examples.csv"
PAIRWISE_OUT = OUT / "e225_e224_public_feedback_decoder_pairwise.csv"
TARGET_OUT = OUT / "e225_e224_public_feedback_decoder_target_anatomy.csv"
REPORT_OUT = OUT / "e225_e224_public_feedback_decoder_report.md"
SELECTED_OUT = OUT / "e225_e224_public_feedback_decoder_selected.json"

EPS = 1.0e-12


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "capped_jepa_breakthrough",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update_class": "strong_support",
        "hidden_world_update": "E224 wins beyond normal post-E95 edge scale. The public hidden subset strongly rewards E211's S4 body plus capped Q3 residual.",
        "next_action": "Do not immediately increase Q3. First decompose the win into S4 body, Q3 residual, and E154 inherited body using an E224-vs-E95-anchor attribution audit.",
        "candidate_to_test": "conditional:e224_component_decomposition_or_e224_e95_anchor",
        "forbidden_action": "Do not submit E223/E211 full-Q3 next as a victory lap; a breakthrough specifically validates capped Q3, not larger Q3.",
        "strengthened": "H219 capped-Q3 JEPA translator; S4-body public alignment",
        "weakened": "FH195 q3_scale 0.75 optimality; E216-style all-JEPA-tail rejection",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": E95_DELTA_VS_MIXMIN,
        "world_update_class": "support",
        "hidden_world_update": "E224 wins by at least the E95-over-mixmin edge. Capped-Q3/S4-body translation is public-readable, but still within hard-label-resolution scale.",
        "next_action": "Promote E224 as the JEPA-family anchor. Use the E224 E95-anchor sibling only if the next public slot is a clean attribution sensor.",
        "candidate_to_test": f"analysis_outputs/{E224_E95_FILE}",
        "forbidden_action": "Do not infer that Q3 scale should be raised to 0.75 or 1.0 without a new tail audit.",
        "strengthened": "H219 and E224 ordering",
        "weakened": "E223 as first JEPA candidate",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": E95_DELTA_VS_MIXMIN,
        "delta_hi_inclusive": -3.0e-6,
        "world_update_class": "weak_support",
        "hidden_world_update": "E224 is public-positive but at one/few-cell scale. The capped-Q3 law may be right, but the result is underresolved.",
        "next_action": "Keep E224 as the preferred JEPA sensor, but do not submit a sibling until an exact-score attribution audit identifies whether Q3 or S4 carried the win.",
        "candidate_to_test": "conditional:e224_exact_score_attribution",
        "forbidden_action": "Do not tune q3_scale from one micro-win.",
        "strengthened": "capped-Q3 direction",
        "weakened": "broad JEPA breakthrough claim",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update_class": "underresolved",
        "hidden_world_update": "E224 does not separate from E95. The JEPA body and tail risk are balanced at public resolution.",
        "next_action": "Keep E95 practical. Treat E224 as an unresolved diagnostic and run a target/component attribution audit before any JEPA sibling.",
        "candidate_to_test": "",
        "forbidden_action": "Do not choose E223, E211, or q3_scale 0.5 from a tie; the scalar score does not identify the target component.",
        "strengthened": "plateau hard-label-resolution law",
        "weakened": "E224 expected-score claim",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": E101_DELTA_VS_E95,
        "world_update_class": "weak_rejection",
        "hidden_world_update": "E224 loses to E95 but no worse than E101. The capped-Q3 translator is not public-positive, but the JEPA lane is not hard-rejected.",
        "next_action": "Do not submit another amplitude sibling. Audit whether E154 inherited body or E224 Q3/S4 residual caused the loss, then decide between E154 branch and new JEPA target design.",
        "candidate_to_test": "conditional:e224_loss_attribution_then_e154_or_new_jepa",
        "forbidden_action": "Do not rescue by raising Q3 to 0.75 or reverting to full-Q3 E211.",
        "strengthened": "E216-derived support-tail skepticism",
        "weakened": "E224 as expected-score file",
    },
    {
        "outcome": "mixmin_safe_loss",
        "delta_lo_exclusive": E101_DELTA_VS_E95,
        "delta_hi_inclusive": MIXMIN_DELTA_VS_E95,
        "world_update_class": "rejection",
        "hidden_world_update": "E224 is worse than E101 but still mixmin-safe. Current E211 probability translation likely misses the public support tail.",
        "next_action": "Demote E211/E223/E224 as expected-score followups. Keep JEPA axes as diagnostics and move to a new representation or support-tail target.",
        "candidate_to_test": "conditional:new_jepa_support_tail_objective",
        "forbidden_action": "Do not submit E224 E95-anchor sibling or E223 as automatic followup.",
        "strengthened": "translation bottleneck",
        "weakened": "current E211 translator",
    },
    {
        "outcome": "branch_loss",
        "delta_lo_exclusive": MIXMIN_DELTA_VS_E95,
        "delta_hi_inclusive": 5.0e-5,
        "world_update_class": "strong_rejection",
        "hidden_world_update": "E224 gives back the E95-over-mixmin gain. The capped-Q3 repair did not make E211 public-safe.",
        "next_action": "Close current E211-family expected-score lane. Search for non-collinear hidden structure or build a JEPA objective with support/tail regularization baked in.",
        "candidate_to_test": "conditional:non_collinear_search_or_support_regularized_jepa",
        "forbidden_action": "Do not submit original E211, E223, or E224 siblings.",
        "strengthened": "public-tail/support mismatch",
        "weakened": "E211 probability translator",
    },
    {
        "outcome": "hard_fail",
        "delta_lo_exclusive": 5.0e-5,
        "delta_hi_inclusive": 3.0e-4,
        "world_update_class": "hard_rejection",
        "hidden_world_update": "E224 is strongly incompatible with public labels. This is not a one-cell plateau fluctuation.",
        "next_action": "Keep E208/E211 axes only as diagnostics. Rebuild target representation or return to block/sequence hidden-world search.",
        "candidate_to_test": "",
        "forbidden_action": "Do not tune Q3 scale, S4 mode, or anchor scale inside the same translator.",
        "strengthened": "JEPA translation failure",
        "weakened": "all current E211-family submissions",
    },
    {
        "outcome": "e216_like_fail",
        "delta_lo_exclusive": 3.0e-4,
        "delta_hi_inclusive": np.inf,
        "world_update_class": "translator_collapse",
        "hidden_world_update": "E224 fails on the same order as bad JEPA public translations. The public-facing translator is collapsed or shortcut-aligned despite local/geometry support.",
        "next_action": "Do a root-cause miss anatomy like E219 before any further JEPA submission. Treat current JEPA probability movement as unsafe.",
        "candidate_to_test": "conditional:e224_public_miss_anatomy",
        "forbidden_action": "Do not submit any E209/E210/E211/E223/E224 sibling before the miss anatomy is resolved.",
        "strengthened": "LeJEPA shortcut warning",
        "weakened": "JEPA probability movement as candidate source",
    },
]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    df = load_sub(file_name, sample)
    return np.clip(df[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def lb_bound(delta: float) -> float:
    return E95_PUBLIC + float(delta)


def build_routebook() -> pd.DataFrame:
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
                "world_update_class": band["world_update_class"],
                "hidden_world_update": band["hidden_world_update"],
                "next_action": band["next_action"],
                "candidate_to_test": band["candidate_to_test"],
                "forbidden_action": band["forbidden_action"],
                "strengthened": band["strengthened"],
                "weakened": band["weakened"],
            }
        )
    return pd.DataFrame(rows)


def decode_score(routebook: pd.DataFrame, score: float) -> dict[str, Any]:
    delta = float(score) - E95_PUBLIC
    rows = routebook.loc[
        routebook["delta_vs_e95_lo_exclusive"].lt(delta)
        & routebook["delta_vs_e95_hi_inclusive"].ge(delta)
    ]
    if len(rows) != 1:
        raise ValueError(f"score {score} mapped to {len(rows)} routebook rows")
    rec = rows.iloc[0].to_dict()
    rec["score"] = float(score)
    rec["delta_vs_e95"] = delta
    rec["delta_vs_e101"] = float(score) - E101_PUBLIC
    rec["delta_vs_mixmin"] = float(score) - MIXMIN_PUBLIC
    rec["delta_vs_e216"] = float(score) - E216_PUBLIC
    return rec


def build_examples(routebook: pd.DataFrame) -> pd.DataFrame:
    examples = [
        E95_PUBLIC - 4.0e-5,
        E95_PUBLIC - 2.0e-5,
        E95_PUBLIC - 8.0e-6,
        E95_PUBLIC,
        E101_PUBLIC,
        MIXMIN_PUBLIC,
        E95_PUBLIC + 2.5e-5,
        E95_PUBLIC + 1.0e-4,
        E216_PUBLIC,
    ]
    rows = []
    for score in examples:
        rec = decode_score(routebook, score)
        rows.append(
            {
                "score": score,
                "outcome": rec["outcome"],
                "world_update_class": rec["world_update_class"],
                "delta_vs_e95": rec["delta_vs_e95"],
                "next_action": rec["next_action"],
                "candidate_to_test": rec["candidate_to_test"],
            }
        )
    return pd.DataFrame(rows)


def movement(pred: np.ndarray, base: np.ndarray) -> np.ndarray:
    return logit(pred) - logit(base)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def target_share(abs_move: pd.DataFrame) -> str:
    total = float(abs_move.to_numpy().sum())
    if total <= EPS:
        return ""
    shares = (abs_move.sum(axis=0) / total).sort_values(ascending=False)
    return ";".join(f"{k}:{v:.6f}" for k, v in shares.items())


def build_pairwise_and_targets(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    files = {
        "e95": E95_FILE,
        "e154": E154_FILE,
        "e211_full_e154": E211_FILE,
        "e211_full_e95": E211_E95_FILE,
        "e216_s2_miss": E216_FILE,
        "e223_q3s0p75_e154": E223_FILE,
        "e224_q3s0p625_e154": E224_FILE,
        "e224_q3s0p625_e95": E224_E95_FILE,
    }
    probs = {name: load_prob(file_name, sample) for name, file_name in files.items()}
    e95_move = {
        name: movement(prob, probs["e95"])
        for name, prob in probs.items()
        if name != "e95"
    }
    pairs = [
        ("e224_q3s0p625_e154", "e95"),
        ("e224_q3s0p625_e154", "e154"),
        ("e224_q3s0p625_e154", "e223_q3s0p75_e154"),
        ("e224_q3s0p625_e154", "e211_full_e154"),
        ("e224_q3s0p625_e154", "e216_s2_miss"),
        ("e224_q3s0p625_e95", "e95"),
        ("e223_q3s0p75_e154", "e95"),
        ("e211_full_e154", "e95"),
        ("e216_s2_miss", "e95"),
    ]
    pair_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    for new, base in pairs:
        mv = movement(probs[new], probs[base])
        abs_mv = np.abs(mv)
        flat = abs_mv.reshape(-1)
        nonzero = flat > 1.0e-9
        pair = f"{new}_vs_{base}"
        row = {
            "pair": pair,
            "new": new,
            "base": base,
            "moved_cells": int(nonzero.sum()),
            "moved_rows": int((abs_mv.max(axis=1) > 1.0e-9).sum()),
            "mean_abs_logit_delta": float(abs_mv.mean()),
            "max_abs_logit_delta": float(abs_mv.max()),
            "top1_abs_logit": float(np.sort(flat)[-1]) if flat.size else 0.0,
            "top5_abs_logit": float(np.sort(flat)[-5:].sum()) if flat.size >= 5 else float(flat.sum()),
            "top1_share": float(np.sort(flat)[-1] / flat.sum()) if flat.sum() > EPS else 0.0,
            "top5_share": float(np.sort(flat)[-5:].sum() / flat.sum()) if flat.sum() > EPS and flat.size >= 5 else 0.0,
            "target_abs_share": target_share(pd.DataFrame(abs_mv, columns=TARGETS)),
        }
        if new != "e95":
            move_new_e95 = e95_move.get(new)
            if move_new_e95 is not None:
                for ref in ["e154", "e211_full_e154", "e223_q3s0p75_e154", "e216_s2_miss"]:
                    if ref in e95_move:
                        row[f"cosine_vs_{ref}_from_e95"] = cosine(move_new_e95, e95_move[ref])
        pair_rows.append(row)
        for j, target in enumerate(TARGETS):
            target_abs = abs_mv[:, j]
            target_rows.append(
                {
                    "pair": pair,
                    "target": target,
                    "moved_cells": int((target_abs > 1.0e-9).sum()),
                    "abs_logit_sum": float(target_abs.sum()),
                    "abs_logit_share": float(target_abs.sum() / abs_mv.sum()) if abs_mv.sum() > EPS else 0.0,
                    "mean_signed_logit_delta": float(mv[:, j].mean()),
                    "max_abs_logit_delta": float(target_abs.max()),
                }
            )
    return pd.DataFrame(pair_rows), pd.DataFrame(target_rows)


def selected_metrics() -> pd.DataFrame:
    selected = pd.read_csv(E224_SELECTED)
    summary = pd.read_csv(E224_SUMMARY)
    selected_id = "e224_q3s0p625_s4closer_e154_a0p5"
    rows = pd.concat(
        [
            selected[selected["candidate_id"].eq(selected_id)],
            summary[
                summary["candidate_id"].eq(selected_id)
                & summary["pair_kind"].eq("actual_vs_e95")
            ],
        ],
        ignore_index=True,
    )
    cols = [
        "candidate_id",
        "pair_kind",
        "q3_scale",
        "s4_mode",
        "anchor",
        "local_delta",
        "geometry_delta",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "q3_top1_over_abs_expected",
        "submission_file",
    ]
    return rows[[c for c in cols if c in rows.columns]]


def write_report(
    routebook: pd.DataFrame,
    examples: pd.DataFrame,
    pairwise: pd.DataFrame,
    target_df: pd.DataFrame,
    metrics: pd.DataFrame,
    selected: dict[str, Any] | None,
) -> None:
    compact_cols = [
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        "world_update_class",
        "next_action",
        "candidate_to_test",
    ]
    pair_cols = [
        "pair",
        "moved_cells",
        "moved_rows",
        "mean_abs_logit_delta",
        "max_abs_logit_delta",
        "top1_share",
        "target_abs_share",
        "cosine_vs_e154_from_e95",
        "cosine_vs_e211_full_e154_from_e95",
        "cosine_vs_e223_q3s0p75_e154_from_e95",
        "cosine_vs_e216_s2_miss_from_e95",
    ]
    target_focus = target_df[
        target_df["pair"].isin(
            [
                "e224_q3s0p625_e154_vs_e95",
                "e224_q3s0p625_e154_vs_e223_q3s0p75_e154",
                "e224_q3s0p625_e154_vs_e211_full_e154",
            ]
        )
    ].sort_values(["pair", "abs_logit_share"], ascending=[True, False])

    lines = [
        "# E225 E224 Public Feedback Decoder",
        "",
        "## Question",
        "",
        "Before E224 is submitted, how should its future public LB be decoded without post-hoc q3-scale tuning?",
        "",
        "## Locked Candidate",
        "",
        f"- candidate: `analysis_outputs/{E224_FILE}`",
        f"- current public frontier: `{E95_PUBLIC:.10f}` from `{E95_FILE}`",
        f"- E101 public reference: `{E101_PUBLIC:.10f}`",
        f"- mixmin public reference: `{MIXMIN_PUBLIC:.10f}`",
        f"- bad JEPA reference E216: `{E216_PUBLIC:.10f}`",
        "",
        "## E224 Metrics",
        "",
        md_table(metrics, n=5),
        "",
        "## Routebook",
        "",
        md_table(routebook, compact_cols, n=20),
        "",
        "## Example Scores",
        "",
        md_table(examples, n=20),
        "",
        "## Movement Anatomy",
        "",
        md_table(pairwise, pair_cols, n=20),
        "",
        "## Target Anatomy",
        "",
        md_table(target_focus, n=40),
        "",
        "## Decision Rules",
        "",
        "- A win strengthens capped-Q3/S4-body translation; it does not justify raising Q3 to `0.75` or `1.0`.",
        "- A tie or small loss requires exact attribution before any sibling. Do not tune q3_scale from one scalar score.",
        "- A loss worse than mixmin demotes the current E211 probability translator. Keep JEPA axes as diagnostics and rebuild the support/tail target.",
        "- An E216-like miss triggers a miss-anatomy audit before any further JEPA submission.",
    ]
    if selected is not None:
        lines += [
            "",
            "## Selected Score Decode",
            "",
            "```json",
            json.dumps(selected, indent=2, sort_keys=True),
            "```",
        ]
    lines += [
        "",
        "## Outputs",
        "",
        f"- routebook: `analysis_outputs/{ROUTEBOOK_OUT.name}`",
        f"- examples: `analysis_outputs/{EXAMPLES_OUT.name}`",
        f"- pairwise anatomy: `analysis_outputs/{PAIRWISE_OUT.name}`",
        f"- target anatomy: `analysis_outputs/{TARGET_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Optional observed public LB to decode.")
    args = parser.parse_args()

    sample_path = ROOT / "data" / "ch2026_submission_sample.csv"
    sample = pd.read_csv(sample_path, parse_dates=["sleep_date", "lifelog_date"])
    routebook = build_routebook()
    examples = build_examples(routebook)
    pairwise, target_df = build_pairwise_and_targets(sample)
    metrics = selected_metrics()
    selected = decode_score(routebook, args.score) if args.score is not None else None

    routebook.to_csv(ROUTEBOOK_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    if selected is not None:
        SELECTED_OUT.write_text(json.dumps(selected, indent=2, sort_keys=True), encoding="utf-8")
    write_report(routebook, examples, pairwise, target_df, metrics, selected)

    print(f"wrote: {REPORT_OUT}")
    if selected is not None:
        print(json.dumps(selected, indent=2, sort_keys=True))
    else:
        print(routebook[["outcome", "public_lb_lo_exclusive", "public_lb_hi_inclusive"]].to_string(index=False))


if __name__ == "__main__":
    main()
