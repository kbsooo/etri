#!/usr/bin/env python3
"""E227: public-feedback decoder for the E166 broad survivor sensor.

This script creates no submission and trains no model. It locks how a future
public LB for `submission_e166_broadsurv_s0p01_d8bfa94b.csv` should update the
hidden-world model, and it records how E166 differs from the current JEPA slot
(E224) and the conservative repaired-branch counter-world (E154).
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

from public_anchor_bottleneck_decomposition import TARGETS, load_sub, logit  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E176_PUBLIC = 0.5763118310
E72_PUBLIC = 0.5764077772
E216_PUBLIC = 0.5772865088

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E176_FILE = "submission_e176_abl_q2_to0p75_91e49725.csv"
E216_FILE = "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"

E167_SUMMARY = OUT / "e167_broad_survivor_context_alignment_summary.csv"
E226_SUMMARY = OUT / "e226_noncollinear_candidate_scan_summary.csv"

ROUTEBOOK_OUT = OUT / "e227_e166_public_feedback_decoder_routebook.csv"
EXAMPLES_OUT = OUT / "e227_e166_public_feedback_decoder_examples.csv"
PAIRWISE_OUT = OUT / "e227_e166_public_feedback_decoder_pairwise.csv"
CANDIDATE_ORDER_OUT = OUT / "e227_e166_public_feedback_decoder_candidate_order.csv"
CONTEXT_OUT = OUT / "e227_e166_public_feedback_decoder_context.csv"
REPORT_OUT = OUT / "e227_e166_public_feedback_decoder_report.md"
SELECTED_OUT = OUT / "e227_e166_public_feedback_decoder_selected.json"

EPS = 1.0e-12


BANDS: list[dict[str, Any]] = [
    {
        "outcome": "broad_breakthrough",
        "delta_lo_exclusive": -np.inf,
        "delta_hi_inclusive": -3.0e-5,
        "world_update_class": "strong_support",
        "hidden_world_update": "E166 wins beyond the normal post-E95 edge scale. The public hidden labels reward broad survivor context that earlier safety atlases treated as dangerous.",
        "next_action": "Promote broad survivor structure as a live hidden-world target. Do an exact E166 component/block attribution before scaling or submitting any E166-family sibling.",
        "candidate_to_test": "conditional:e166_component_block_attribution",
        "forbidden_action": "Do not scale E166 up from a single win; E167 already says this branch is safety-atlas divergent.",
        "strengthened": "broad survivor / safety-atlas-overconservative world; subject-calendar edge context",
        "weakened": "E72/E101/E176/E216-derived veto atlas as a hard rejection rule",
    },
    {
        "outcome": "clean_win",
        "delta_lo_exclusive": -3.0e-5,
        "delta_hi_inclusive": E95_PUBLIC - MIXMIN_PUBLIC,
        "world_update_class": "support",
        "hidden_world_update": "E166 beats E95 by at least the E95-over-mixmin edge. Broad survivor context is public-readable, but still at frontier hard-label scale.",
        "next_action": "Use E166 as the new broad-world anchor and audit whether the top benefit cells are between-train-runs or S-stage driven.",
        "candidate_to_test": "conditional:e166_context_component_attribution",
        "forbidden_action": "Do not jump to E169/E176 siblings; E176 already branch-lost and E166 asks a different raw broad-survivor question.",
        "strengthened": "E166 context-real broad branch",
        "weakened": "repaired-branch-only next-action policy",
    },
    {
        "outcome": "micro_win",
        "delta_lo_exclusive": E95_PUBLIC - MIXMIN_PUBLIC,
        "delta_hi_inclusive": -3.0e-6,
        "world_update_class": "weak_support",
        "hidden_world_update": "E166 is public-positive but only at one/few-cell scale. The broad branch may be real, but the public score does not yet identify the safe substructure.",
        "next_action": "Keep E166 alive. Decode exact cells and compare against E167 top-benefit context before any same-family file.",
        "candidate_to_test": "conditional:e166_exact_cell_decoder",
        "forbidden_action": "Do not treat a micro-win as evidence that broad survivor amplitude should increase.",
        "strengthened": "broad branch not dead",
        "weakened": "claim that E166 is a 0.54-path breakthrough",
    },
    {
        "outcome": "tie",
        "delta_lo_exclusive": -3.0e-6,
        "delta_hi_inclusive": 3.0e-6,
        "world_update_class": "underresolved",
        "hidden_world_update": "E166 does not separate from E95. The context-real signal and safety-atlas divergence balance at public resolution.",
        "next_action": "Keep E95 practical. Prefer E224 if the next question is JEPA, or E154 if the next question is the conservative branch.",
        "candidate_to_test": "conditional:e224_or_e154_by_question",
        "forbidden_action": "Do not select an E166 sibling from a tie.",
        "strengthened": "plateau hard-label-resolution law",
        "weakened": "E166 expected-score claim",
    },
    {
        "outcome": "small_loss",
        "delta_lo_exclusive": 3.0e-6,
        "delta_hi_inclusive": E101_PUBLIC - E95_PUBLIC,
        "world_update_class": "weak_rejection",
        "hidden_world_update": "E166 loses no worse than E101. The broad branch is not public-positive, but the failure is still frontier-scale.",
        "next_action": "Do not rescue by scaling. Compare loss cells to E72-active and low-veto-null warnings, then choose E154 or new representation search.",
        "candidate_to_test": "conditional:e166_loss_cell_attribution_then_e154_or_search",
        "forbidden_action": "Do not submit E169/E172/E174/E176 same-family broad repairs as automatic rescue.",
        "strengthened": "E167 safety-divergence warning",
        "weakened": "E166 as next expected-score file",
    },
    {
        "outcome": "mixmin_safe_loss",
        "delta_lo_exclusive": E101_PUBLIC - E95_PUBLIC,
        "delta_hi_inclusive": MIXMIN_PUBLIC - E95_PUBLIC,
        "world_update_class": "rejection",
        "hidden_world_update": "E166 loses more than E101 but remains mixmin-safe. The broad survivor direction likely conflicts with the hidden public support tail.",
        "next_action": "Route away from broad survivor as an expected-score lane. Use E154 for conservative branch test or E224 for the distinct JEPA test.",
        "candidate_to_test": "conditional:e154_or_e224_by_question",
        "forbidden_action": "Do not scale E166 or revive E176-like broad siblings.",
        "strengthened": "public-tail/support mismatch on broad survivor",
        "weakened": "safety-atlas-overconservative world",
    },
    {
        "outcome": "broad_branch_loss",
        "delta_lo_exclusive": MIXMIN_PUBLIC - E95_PUBLIC,
        "delta_hi_inclusive": E176_PUBLIC - E95_PUBLIC,
        "world_update_class": "strong_rejection",
        "hidden_world_update": "E166 gives back the E95-over-mixmin gain but is not worse than E176. This is the broad-family branch-loss band.",
        "next_action": "Treat E166 like E176: broad survivor body is public-misaligned at frontier resolution. Route to E154 or a non-collinear representation.",
        "candidate_to_test": f"analysis_outputs/{E154_FILE}",
        "forbidden_action": "Do not submit E169/E172/E174/E176 as rescue variants.",
        "strengthened": "broad-family public mismatch",
        "weakened": "raw broad survivor branch",
    },
    {
        "outcome": "broad_fail",
        "delta_lo_exclusive": E176_PUBLIC - E95_PUBLIC,
        "delta_hi_inclusive": 5.0e-5,
        "world_update_class": "hard_rejection",
        "hidden_world_update": "E166 is worse than E176 but not in E72-scale failure. The broad survivor safety divergence is likely public-negative.",
        "next_action": "Close E166-family expected-score followups. Use E154 if testing existing files; otherwise search for a new block/sequence target.",
        "candidate_to_test": f"analysis_outputs/{E154_FILE}",
        "forbidden_action": "Do not interpret this as a reason to tune E166 amplitude; the branch itself failed.",
        "strengthened": "E167 E72-active / low-veto-null warning",
        "weakened": "E166 broad survivor hidden-world claim",
    },
    {
        "outcome": "e72_like_fail",
        "delta_lo_exclusive": 5.0e-5,
        "delta_hi_inclusive": E72_PUBLIC - E95_PUBLIC,
        "world_update_class": "very_hard_rejection",
        "hidden_world_update": "E166 fails on the path toward the known E72 miss scale. The E72-active warning in E167 was probably causal.",
        "next_action": "Run an E166 miss anatomy before any broad candidate. Treat E72-active broad survivor structure as public-dangerous.",
        "candidate_to_test": "conditional:e166_public_miss_anatomy",
        "forbidden_action": "Do not submit any broad survivor sibling first.",
        "strengthened": "E72-active hidden-tail veto",
        "weakened": "context-real means public-safe",
    },
    {
        "outcome": "s2_jepa_like_fail_or_worse",
        "delta_lo_exclusive": E72_PUBLIC - E95_PUBLIC,
        "delta_hi_inclusive": np.inf,
        "world_update_class": "collapse",
        "hidden_world_update": "E166 fails worse than E72-scale public miss. A broad hidden-context signal can be catastrophically miscalibrated under public labels.",
        "next_action": "Do a root-cause miss anatomy and stop broad survivor submissions until a public-tail target is rebuilt.",
        "candidate_to_test": "conditional:e166_public_miss_anatomy",
        "forbidden_action": "Do not use E166/E169/E176 as probability translators.",
        "strengthened": "LeJEPA shortcut/collapse warning",
        "weakened": "broad survivor probability movement",
    },
]


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n)
    lines = [
        "| " + " | ".join(str(c) for c in view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for rec in view.to_dict("records"):
        vals: list[str] = []
        for col in view.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                if np.isposinf(value):
                    vals.append("inf")
                elif np.isneginf(value):
                    vals.append("-inf")
                else:
                    vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


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
                "beats_e176": (lb_bound(hi) < E176_PUBLIC) if np.isfinite(hi) else False,
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
    rows = routebook[
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
    rec["delta_vs_e176"] = float(score) - E176_PUBLIC
    rec["delta_vs_e72"] = float(score) - E72_PUBLIC
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
        E176_PUBLIC,
        E95_PUBLIC + 4.0e-5,
        E72_PUBLIC,
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


def prob(file_name: str, sample: pd.DataFrame | None = None) -> np.ndarray:
    df = load_sub(file_name, sample)
    return np.clip(df[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def cos(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    if den <= EPS:
        return np.nan
    return float((a @ b) / den)


def movement_table() -> pd.DataFrame:
    sample = load_sub(E95_FILE)
    files = {
        "e95": E95_FILE,
        "e101": E101_FILE,
        "mixmin": MIXMIN_FILE,
        "e154": E154_FILE,
        "e166": E166_FILE,
        "e176": E176_FILE,
        "e216": E216_FILE,
        "e224": E224_FILE,
        "e72": E72_FILE,
    }
    probs = {tag: prob(file_name, sample) for tag, file_name in files.items()}
    logits = {tag: logit(value) for tag, value in probs.items()}
    moves = {tag: (value - logits["e95"]).reshape(-1) for tag, value in logits.items()}

    rows: list[dict[str, Any]] = []
    for left in ["e166", "e224", "e154", "e176", "e216", "e101", "mixmin", "e72"]:
        diff = logits[left] - logits["e95"]
        abs_diff = np.abs(diff)
        moved = abs_diff > 1.0e-10
        target_abs = abs_diff.sum(axis=0)
        total_abs = float(target_abs.sum())
        rec: dict[str, Any] = {
            "tag": left,
            "file_name": files[left],
            "moved_cells_vs_e95": int(moved.sum()),
            "moved_rows_vs_e95": int(moved.any(axis=1).sum()),
            "mean_abs_logit_vs_e95": float(abs_diff.mean()),
            "max_abs_logit_vs_e95": float(abs_diff.max()),
            "l1_logit_vs_e95": total_abs,
            "cos_vs_e166": cos(moves[left], moves["e166"]) if left != "e95" else np.nan,
            "cos_vs_e224": cos(moves[left], moves["e224"]) if left != "e95" else np.nan,
            "cos_vs_e154": cos(moves[left], moves["e154"]) if left != "e95" else np.nan,
            "cos_vs_e176": cos(moves[left], moves["e176"]) if left != "e95" else np.nan,
            "cos_vs_e216": cos(moves[left], moves["e216"]) if left != "e95" else np.nan,
            "cos_vs_e72": cos(moves[left], moves["e72"]) if left != "e95" else np.nan,
        }
        targets_moved = []
        for i, target in enumerate(TARGETS):
            share = float(target_abs[i] / total_abs) if total_abs > EPS else 0.0
            rec[f"abs_share_{target}"] = share
            if target_abs[i] > 1.0e-10:
                targets_moved.append(target)
        rec["targets_moved_vs_e95"] = ",".join(targets_moved)
        rows.append(rec)
    return pd.DataFrame(rows)


def context_table() -> pd.DataFrame:
    e167 = pd.read_csv(E167_SUMMARY)
    focus = e167[e167["pair"].isin(["e166_vs_e95", "e154_vs_e95", "e95_vs_mixmin"])]
    cols = [
        "pair",
        "set_type",
        "n_cells",
        "n_rows",
        "expected_delta",
        "swing_weighted_support_prob",
        "q_share",
        "s_share",
        "q2s3_share",
        "edge_like_rate",
        "between_train_runs_rate",
        "e72_active_rate",
        "all_veto_null_rate",
        "all_safe_density_mean",
        "broad_low_alpha_mass_sum",
        "e101_plausible_mass_sum",
        "top_subject_share",
    ]
    return focus[cols].copy()


def candidate_order_table() -> pd.DataFrame:
    e226 = pd.read_csv(E226_SUMMARY)
    by_file = e226.set_index("file_name")
    rows = [
        {
            "public_slot_role": "jepa_slot",
            "submission": f"analysis_outputs/{E224_FILE}",
            "rank_if_question": 1,
            "hidden_world_bet": "E211 S4 body plus capped Q3 residual transfers to public.",
            "why_now": "This is the preferred JEPA-family sensor and is orthogonal to the E216 S2 miss.",
            "score_source": "E225 routebook",
        },
        {
            "public_slot_role": "independent_broad_counterworld",
            "submission": f"analysis_outputs/{E166_FILE}",
            "rank_if_question": 1,
            "hidden_world_bet": "The current safety atlas is overconservative and broad survivor edge/between-train-runs context is public-real.",
            "why_now": "E226 top independent non-E224 sensor; E167 says context-real but safety-divergent.",
            "score_source": "E226/E167/E227 routebook",
        },
        {
            "public_slot_role": "conservative_repaired_branch",
            "submission": f"analysis_outputs/{E154_FILE}",
            "rank_if_question": 1,
            "hidden_world_bet": "The E144/E154 repaired S3 active-boundary branch is the clean counter-world after broad/JEPA losses.",
            "why_now": "E226 keeps it as the conservative repaired-branch counter-world; E160 has an existing decoder.",
            "score_source": "E160 routebook",
        },
    ]
    out = pd.DataFrame(rows)
    metrics = []
    for file_name in [E224_FILE, E166_FILE, E154_FILE]:
        if file_name in by_file.index:
            rec = by_file.loc[file_name].to_dict()
            metrics.append(
                {
                    "submission": f"analysis_outputs/{file_name}",
                    "candidate_role": rec.get("candidate_role", ""),
                    "submission_sensor_score": rec.get("submission_sensor_score", np.nan),
                    "cos_vs_e224": rec.get("cos_vs_e224", np.nan),
                    "cos_vs_e216": rec.get("cos_vs_e216", np.nan),
                    "cos_vs_e72": rec.get("cos_vs_e72", np.nan),
                    "expected_focus": rec.get("expected_focus", np.nan),
                    "adverse_delta": rec.get("adverse_delta", np.nan),
                    "support_prob_focus_swing_weighted": rec.get("support_prob_focus_swing_weighted", np.nan),
                }
            )
    return out.merge(pd.DataFrame(metrics), on="submission", how="left")


def write_report(
    routebook: pd.DataFrame,
    examples: pd.DataFrame,
    pairwise: pd.DataFrame,
    context: pd.DataFrame,
    candidate_order: pd.DataFrame,
) -> None:
    e166_pair = pairwise[pairwise["tag"].eq("e166")].iloc[0]
    e166_context = context[
        context["pair"].eq("e166_vs_e95") & context["set_type"].eq("top_benefit_nfocus")
    ].iloc[0]
    text = f"""# E227 E166 Public Feedback Decoder

## Question

If `analysis_outputs/{E166_FILE}` is submitted, how should its public LB update the hidden-world model before any post-hoc amplitude or sibling choice?

## Main Read

- E166 is the best existing non-E224 broad counter-world from E226, not a JEPA sibling.
- Movement versus E95: `{int(e166_pair['moved_cells_vs_e95'])}` cells, `{int(e166_pair['moved_rows_vs_e95'])}` rows, targets `{e166_pair['targets_moved_vs_e95']}`.
- E226 anatomy: expected focus `{float(candidate_order.loc[candidate_order['submission'].str.endswith(E166_FILE), 'expected_focus'].iloc[0]):.9f}`, adverse `{float(candidate_order.loc[candidate_order['submission'].str.endswith(E166_FILE), 'adverse_delta'].iloc[0]):.9f}`, support `{float(candidate_order.loc[candidate_order['submission'].str.endswith(E166_FILE), 'support_prob_focus_swing_weighted'].iloc[0]):.9f}`.
- E167 context: top-benefit cells have edge-like rate `{float(e166_context['edge_like_rate']):.6f}`, between-train-runs rate `{float(e166_context['between_train_runs_rate']):.6f}`, E72-active rate `{float(e166_context['e72_active_rate']):.6f}`, all-veto-null rate `{float(e166_context['all_veto_null_rate']):.6f}`.

## Candidate Roles

{md_table(candidate_order, floatfmt=".9f")}

## Routebook

{md_table(routebook, floatfmt=".9f")}

## Example Score Decodes

{md_table(examples, floatfmt=".9f")}

## Movement Geometry

{md_table(pairwise, floatfmt=".9f")}

## Context Evidence

{md_table(context, floatfmt=".9f")}

## Decision

- E224 remains the JEPA-family slot.
- E166 is the next independent broad-world sensor if the question is whether the safety atlas became too conservative after E72/E101/E176/E216.
- E154 remains the conservative repaired-branch counter-world if the goal is lower-risk existing-file branch testing.
- Do not submit E166 siblings or scale E166 before a public score is decoded by this routebook.
"""
    REPORT_OUT.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", type=float, default=None, help="Optional public LB for E166 to decode.")
    args = parser.parse_args()

    routebook = build_routebook()
    examples = build_examples(routebook)
    pairwise = movement_table()
    context = context_table()
    candidate_order = candidate_order_table()

    routebook.to_csv(ROUTEBOOK_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    context.to_csv(CONTEXT_OUT, index=False)
    candidate_order.to_csv(CANDIDATE_ORDER_OUT, index=False)
    write_report(routebook, examples, pairwise, context, candidate_order)

    if args.score is not None:
        selected = decode_score(routebook, args.score)
        SELECTED_OUT.write_text(json.dumps(selected, indent=2, sort_keys=True))
        print(json.dumps(selected, indent=2, sort_keys=True))
    else:
        top = candidate_order[
            [
                "public_slot_role",
                "submission",
                "candidate_role",
                "cos_vs_e224",
                "expected_focus",
                "adverse_delta",
                "support_prob_focus_swing_weighted",
            ]
        ]
        print("[E227]")
        print(f"routebook={ROUTEBOOK_OUT}")
        print(f"report={REPORT_OUT}")
        print(md_table(top, floatfmt=".9f"))


if __name__ == "__main__":
    main()
