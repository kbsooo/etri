#!/usr/bin/env python3
"""E259: post-E247 public-observation routebook.

E247 is now the public frontier, but it is underidentified:

    E95 -> E224: capped-Q3/S4 body
    E224 -> E247: Q3 feature-NN1 rollback

This script creates a pre-registered interpretation table for the next two
high-information observations:

    E256: score-plus-information, broad vs high-amplitude Q3 smoothing
    E224: attribution, E247 body alone vs body plus rollback

It creates no submission and uses no unknown public LB. Optional score arguments
only decode a future observation through the routebook.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E247_PUBLIC = 0.5761589494
E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E216_PUBLIC = 0.5772865088

E247_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256_FILE = "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

ROUTEBOOK_OUT = OUT / "e259_post_e247_routebook.csv"
EXAMPLES_OUT = OUT / "e259_post_e247_score_examples.csv"
DECODED_OUT = OUT / "e259_post_e247_decoded_scores.json"
REPORT_OUT = OUT / "e259_post_e247_observation_routebook_report.md"

GROUP_SUMMARY_IN = OUT / "e257_e247_e256_cell_contrast_group_summary.csv"
COMPONENT_IN = OUT / "e258_e247_attribution_component_summary.csv"
OVERLAP_IN = OUT / "e258_e247_attribution_overlap_summary.csv"

EPS = 1.0e-12


def fmt(x: Any, digits: int = 9) -> str:
    if x is None:
        return ""
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return str(x)
    if np.isnan(xf):
        return "nan"
    if np.isposinf(xf):
        return "inf"
    if np.isneginf(xf):
        return "-inf"
    return f"{xf:.{digits}f}"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    headers = list(view.columns)
    rows = []
    for _, row in view.iterrows():
        rows.append([fmt(row[c]) if isinstance(row[c], (float, int, np.floating, np.integer)) else str(row[c]) for c in headers])
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    out.extend("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join(out)


def band(
    candidate_id: str,
    outcome: str,
    lo: float,
    hi: float,
    world_update_class: str,
    hidden_world_update: str,
    next_action: str,
    strengthened: str,
    weakened: str,
    private_risk: str,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "outcome": outcome,
        "public_lb_lo_exclusive": lo,
        "public_lb_hi_inclusive": hi,
        "delta_vs_e247_lo_exclusive": lo - E247_PUBLIC if np.isfinite(lo) else -np.inf,
        "delta_vs_e247_hi_inclusive": hi - E247_PUBLIC if np.isfinite(hi) else np.inf,
        "delta_vs_e95_hi_inclusive": hi - E95_PUBLIC if np.isfinite(hi) else np.inf,
        "beats_e247": hi < E247_PUBLIC,
        "beats_e95": hi < E95_PUBLIC,
        "world_update_class": world_update_class,
        "hidden_world_update": hidden_world_update,
        "next_action": next_action,
        "strengthened": strengthened,
        "weakened": weakened,
        "private_risk": private_risk,
    }


def build_routebook() -> pd.DataFrame:
    # Two-cell public movements around this frontier can land within a few e-6.
    near = 3.0e-6
    clean = 2.0e-5
    hard = 3.0e-5
    return pd.DataFrame(
        [
            band(
                "E256",
                "amplitude_smoothing_breakthrough",
                -np.inf,
                E247_PUBLIC - clean,
                "strong_support",
                "E256 wins by more than frontier noise. Public prefers high-amplitude/E230-aligned Q3 rollback over E247's broader low-amplitude smoothing mass.",
                "Promote amplitude-constrained smoothing. Search around high-amplitude cells only after auditing private risk; do not restore E247-only broad cells.",
                "H256/H257 amplitude-constrained feature-NN1 smoothing",
                "E247-only broad low-amplitude smoothness as necessary public signal",
                "May overfit public high-amplitude cells if the win is driven by a tiny hard-label subset.",
            ),
            band(
                "E256",
                "clean_win",
                E247_PUBLIC - clean,
                E247_PUBLIC - near,
                "support",
                "E256 beats E247 at readable scale but not enough to call a new law. The cell anatomy trade looks public-favorable.",
                "Use E256 as new operational anchor, then run an E256-vs-E247-only attribution audit before any sibling.",
                "high-amplitude smoothing",
                "broad top34 exactness",
                "Delta can still be a small public-cell realization rather than robust private improvement.",
            ),
            band(
                "E256",
                "tie",
                E247_PUBLIC - near,
                E247_PUBLIC + near,
                "underresolved",
                "E256 does not separate from E247. Broad smoothness and high-amplitude smoothing are tied at public resolution.",
                "Do not tune smoothing siblings. Use E224 if attribution is still needed, or switch to a non-collinear question.",
                "feature-NN1 smoothing family generally",
                "ranking E247 vs E256 from current stress metrics",
                "Tied public does not identify which cell group private prefers.",
            ),
            band(
                "E256",
                "near_loss",
                E247_PUBLIC + near,
                E247_PUBLIC + hard,
                "weak_rejection",
                "E247-only broad low-amplitude smoothing likely carries real public signal; E256's high-amplitude concentration prunes too much.",
                "Keep E247 as anchor. Do not submit high-amplitude siblings. If continuing, isolate E247-only cells rather than increasing amplitude.",
                "H257 broad low-amplitude smoothness",
                "amplitude-only rollback rule",
                "Near loss may still be public-cell noise; private may prefer the more concentrated E256.",
            ),
            band(
                "E256",
                "same_family_loss",
                E247_PUBLIC + hard,
                E95_PUBLIC,
                "rejection",
                "E256 loses the E247 edge but remains at or above the old E95 frontier. The exact E247 top34 set or E224-body interaction matters.",
                "Stop sibling sweeps. Submit E224 only if the next question is body attribution; otherwise search non-collinear structure.",
                "E247 exact top34 / body interaction",
                "amplitude-constrained smoothing as score route",
                "E247 may be public-overfit; E256 loss alone cannot prove E247 private safety.",
            ),
            band(
                "E256",
                "hard_loss",
                E95_PUBLIC,
                np.inf,
                "hard_rejection",
                "E256 gives back the E247 advantage and fails as a same-family refinement.",
                "Close E256-like refinements. Treat E247 as a fragile public observation until E224 attribution or another independent sensor confirms the body.",
                "fragility / attribution gap",
                "same-family smoothing refinements",
                "Hard loss could still be E256-specific; E247 itself remains observed best.",
            ),
            band(
                "E224",
                "body_breakthrough",
                -np.inf,
                E247_PUBLIC - clean,
                "strong_support",
                "The E224 body alone beats E247. The rollback likely over-pruned the true public body, and E247's win was carried by E224.",
                "Promote E224 body as the core law. Audit rollback harm cells; do not add Q3 smoothing until a body-preserving gate exists.",
                "E224 capped-Q3/S4 body",
                "Q3 rollback necessity",
                "A body-only win may amplify private risk because E224 has high adverse capacity and lower support probability.",
            ),
            band(
                "E224",
                "body_tie_or_micro_win",
                E247_PUBLIC - clean,
                E247_PUBLIC + near,
                "support",
                "E224 is as good as E247. Most of the public gain came from the body, while rollback is optional or underresolved.",
                "Use E224 as attribution-confirmed anchor. Revisit Q3 rollback only as a private-risk reducer, not as a score requirement.",
                "E224 body carried the win",
                "rollback as essential public signal",
                "E224 body has broad Q3/S4 movement and could be less private-safe despite public tie.",
            ),
            band(
                "E224",
                "rollback_helped",
                E247_PUBLIC + near,
                E95_PUBLIC,
                "mixed_support",
                "E224 remains better than old E95 but worse than E247. Body is public-real, and the Q3 rollback adds necessary tail correction.",
                "Keep E247 as anchor. Use E256 result if available to decide broad vs amplitude rollback; otherwise do not remove rollback.",
                "body plus tail-correction worldview",
                "body-only sufficiency",
                "Underidentified if the loss is tiny; do not over-tune Q3 scale from one score.",
            ),
            band(
                "E224",
                "body_not_enough",
                E95_PUBLIC,
                MIXMIN_PUBLIC,
                "weak_rejection",
                "E224 fails to preserve the old E95 advantage but stays mixmin-safe. The public win needs the rollback/interaction, not body alone.",
                "Demote body-only candidates. Keep E247; if exploring, target Q3 tail correction rather than larger body.",
                "Q3 rollback / interaction",
                "E224 body-only route",
                "Could be a calibration-tail miss, not a full body rejection.",
            ),
            band(
                "E224",
                "body_loss",
                MIXMIN_PUBLIC,
                E216_PUBLIC,
                "rejection",
                "E224 gives back the E95/mixmin gains. E247 rollback may have rescued a risky body or E224 was never public-safe alone.",
                "Do not submit E224 siblings. Treat E247 as a specific body-plus-trim construction and move to non-collinear structure.",
                "rollback as rescue / body risk",
                "current E211/E224 body translator",
                "If close to mixmin, the body might be neutral but not enough; if near E216, it is a bad translator.",
            ),
            band(
                "E224",
                "body_collapse",
                E216_PUBLIC,
                np.inf,
                "hard_rejection",
                "E224 fails like a bad JEPA translation. The body is shortcut/collapse-prone despite E247's observed rescue.",
                "Close current E211/E224 translator lane as submissions. Keep it only as a diagnostic latent.",
                "LeJEPA shortcut warning",
                "body translator as candidate source",
                "E247 remains an exception; attribution must not generalize the body without tail correction.",
            ),
        ]
    )


def decode_score(routebook: pd.DataFrame, candidate_id: str, score: float) -> dict[str, Any]:
    rows = routebook[
        routebook["candidate_id"].eq(candidate_id)
        & routebook["public_lb_lo_exclusive"].lt(score)
        & routebook["public_lb_hi_inclusive"].ge(score)
    ]
    if len(rows) != 1:
        raise ValueError(f"{candidate_id} score {score} mapped to {len(rows)} bands")
    out = rows.iloc[0].to_dict()
    out.update(
        {
            "score": float(score),
            "delta_vs_e247": float(score) - E247_PUBLIC,
            "delta_vs_e95": float(score) - E95_PUBLIC,
            "delta_vs_mixmin": float(score) - MIXMIN_PUBLIC,
        }
    )
    return out


def build_examples(routebook: pd.DataFrame) -> pd.DataFrame:
    probes = []
    for candidate_id in ["E256", "E224"]:
        for score in [
            E247_PUBLIC - 5.0e-5,
            E247_PUBLIC - 1.0e-5,
            E247_PUBLIC,
            E247_PUBLIC + 1.0e-5,
            E95_PUBLIC - 1.0e-5,
            E95_PUBLIC + 1.0e-5,
            MIXMIN_PUBLIC + 2.0e-5,
        ]:
            rec = decode_score(routebook, candidate_id, score)
            probes.append(
                {
                    "candidate_id": candidate_id,
                    "score": score,
                    "delta_vs_e247": rec["delta_vs_e247"],
                    "outcome": rec["outcome"],
                    "world_update_class": rec["world_update_class"],
                    "next_action": rec["next_action"],
                }
            )
    return pd.DataFrame(probes)


def read_existing_summaries() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    groups = pd.read_csv(GROUP_SUMMARY_IN) if GROUP_SUMMARY_IN.exists() else pd.DataFrame()
    components = pd.read_csv(COMPONENT_IN) if COMPONENT_IN.exists() else pd.DataFrame()
    overlap = pd.read_csv(OVERLAP_IN) if OVERLAP_IN.exists() else pd.DataFrame()
    return groups, components, overlap


def make_report(
    routebook: pd.DataFrame,
    examples: pd.DataFrame,
    decoded: list[dict[str, Any]],
    groups: pd.DataFrame,
    components: pd.DataFrame,
    overlap: pd.DataFrame,
) -> str:
    e256_cols = [
        "group",
        "n_rows",
        "rollback_amp_mean",
        "smooth_gain_sum",
        "affected_pair_abs_delta",
        "support_prob_focus_weighted",
        "top1_over_abs_expected",
    ]
    component_cols = [
        "component_id",
        "moved_cells",
        "targets_moved",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    overlap_cols = [
        "component_id",
        "selected_cells",
        "cos_body_rollback_selected",
        "rollback_abs_over_selected_body_abs",
        "opposite_sign_share_selected",
    ]
    route_cols = [
        "candidate_id",
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        "world_update_class",
        "next_action",
    ]
    decoded_text = "_No future score was supplied._"
    if decoded:
        decoded_text = md_table(pd.DataFrame(decoded)[["candidate_id", "score", "delta_vs_e247", "outcome", "world_update_class", "next_action"]])

    return f"""# E259 Post-E247 Observation Routebook

## Question

E247 is the public frontier, but what exactly did public reward: E224's body, E247's Q3 rollback, or the exact interaction?

This routebook pre-registers how to read the next two clean observations before those scores are known:

- `E256`: `{E256_FILE}` tests high-amplitude Q3 smoothing versus E247's broader top34 smoothing.
- `E224`: `{E224_FILE}` tests whether the E224 body alone carried the E247 win.

## Current Public Anchors

| anchor | public LB | delta vs E247 |
| --- | ---: | ---: |
| E247 current best | {E247_PUBLIC:.10f} | {0.0:.10f} |
| E95 previous hardtail | {E95_PUBLIC:.10f} | {E95_PUBLIC - E247_PUBLIC:.10f} |
| E101 Q2/S3 tail | {E101_PUBLIC:.10f} | {E101_PUBLIC - E247_PUBLIC:.10f} |
| mixmin | {MIXMIN_PUBLIC:.10f} | {MIXMIN_PUBLIC - E247_PUBLIC:.10f} |
| E216 bad JEPA S2 | {E216_PUBLIC:.10f} | {E216_PUBLIC - E247_PUBLIC:.10f} |

## Observed Anatomy Being Split

### E247 vs E256 Cell Groups

{md_table(groups, e256_cols, n=8)}

### Body/Rollback Components

{md_table(components, component_cols, n=8)}

### Rollback Opposes Body

{md_table(overlap, overlap_cols, n=4)}

## Routebook

{md_table(routebook, route_cols, n=20)}

## Score Examples

{md_table(examples, ["candidate_id", "score", "delta_vs_e247", "outcome", "world_update_class"], n=20)}

## Decoded Future Scores

{decoded_text}

## Decision

- If the next public slot should still try to improve score while answering a clean question, use E256.
- If the next public slot should maximize attribution information, use E224.
- Do not blend E247/E256/E224 before one of these two axes is observed; blending would hide the only clean causal split left.

## Interpretation Shortcut

- E256 win: high-amplitude constrained feature-NN1 smoothing is stronger than broad top34 smoothness.
- E256 close loss: E247-only low-amplitude broad smoothing is public signal.
- E256 hard loss: exact E247 top34 or body interaction matters.
- E224 win/tie: E224 body carried most of the win; rollback is optional or over-pruning.
- E224 better than E95 but worse than E247: body is real, rollback is necessary.
- E224 worse than mixmin: body-only translator is unsafe; E247 was a rescued interaction, not a general body law.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--e256-score", type=float, default=None)
    parser.add_argument("--e224-score", type=float, default=None)
    args = parser.parse_args()

    routebook = build_routebook()
    examples = build_examples(routebook)
    groups, components, overlap = read_existing_summaries()

    decoded: list[dict[str, Any]] = []
    if args.e256_score is not None:
        decoded.append(decode_score(routebook, "E256", args.e256_score))
    if args.e224_score is not None:
        decoded.append(decode_score(routebook, "E224", args.e224_score))

    routebook.to_csv(ROUTEBOOK_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)
    if decoded:
        DECODED_OUT.write_text(json.dumps(decoded, indent=2, ensure_ascii=False), encoding="utf-8")
    report = make_report(routebook, examples, decoded, groups, components, overlap)
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(f"wrote {ROUTEBOOK_OUT}")
    print(f"wrote {EXAMPLES_OUT}")
    print(f"wrote {REPORT_OUT}")
    if decoded:
        print(f"wrote {DECODED_OUT}")


if __name__ == "__main__":
    main()
