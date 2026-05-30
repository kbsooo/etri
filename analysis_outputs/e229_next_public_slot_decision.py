#!/usr/bin/env python3
"""E229: next public-slot decision audit after the E216 miss.

This script creates no submission and trains no model. It treats the next
public slot as an observation-design problem: choose the file whose score will
kill or keep the most important hidden-world belief.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E95_PUBLIC = 0.5762913298
E216_PUBLIC = 0.5772865088

E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"

E225_ROUTE = OUT / "e225_e224_public_feedback_decoder_routebook.csv"
E227_ROUTE = OUT / "e227_e166_public_feedback_decoder_routebook.csv"
E160_ROUTE = OUT / "e160_e154_postfeedback_interpreter_summary.csv"
E227_ORDER = OUT / "e227_e166_public_feedback_decoder_candidate_order.csv"
E228_SUMMARY = OUT / "e228_triworld_conflict_atlas_summary.csv"
E228_PAIRWISE = OUT / "e228_triworld_conflict_atlas_pairwise.csv"
ANCHOR_MODELS = OUT / "public_anchor_bottleneck_model_scores.csv"

SUMMARY_OUT = OUT / "e229_next_public_slot_decision_summary.csv"
ROUTE_OUT = OUT / "e229_next_public_slot_decision_route_summary.csv"
REPORT_OUT = OUT / "e229_next_public_slot_decision_report.md"


def md_table(frame: pd.DataFrame, n: int = 20, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n)
    lines = [
        "| " + " | ".join(str(c) for c in view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for rec in view.to_dict("records"):
        values: list[str] = []
        for col in view.columns:
            value = rec[col]
            if pd.isna(value):
                values.append("")
            elif isinstance(value, (float, np.floating)):
                if np.isposinf(value):
                    values.append("inf")
                elif np.isneginf(value):
                    values.append("-inf")
                else:
                    values.append(format(float(value), floatfmt))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required E229 input: {path}")
    return pd.read_csv(path)


def route_stats(frame: pd.DataFrame, class_col: str = "world_update_class") -> dict[str, Any]:
    candidate_col = "candidate_to_test"
    if candidate_col not in frame.columns:
        candidate_col = "allowed_next"
    candidate_series = frame[candidate_col].fillna("").astype(str) if candidate_col in frame.columns else pd.Series([])
    return {
        "routebook_outcomes": int(len(frame)),
        "routebook_world_classes": int(frame[class_col].nunique()) if class_col in frame.columns else int(len(frame)),
        "routebook_conditional_actions": int(candidate_series.str.contains("conditional", regex=False).sum())
        if len(candidate_series)
        else 0,
        "routebook_named_candidate_actions": int(
            candidate_series.str.contains(".csv", regex=False).sum()
        )
        if len(candidate_series)
        else 0,
    }


def compact_route(frame: pd.DataFrame, candidate: str, class_col: str = "world_update_class") -> pd.DataFrame:
    cols = [
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        class_col,
        "next_action",
        "allowed_next",
        "candidate_to_test",
        "forbidden_action",
        "forbidden",
    ]
    keep = [c for c in cols if c in frame.columns]
    out = frame[keep].copy()
    out.insert(0, "candidate", candidate)
    return out


def edge_factor(expected_focus: float, proxy_mae: float) -> float:
    if proxy_mae <= 0:
        return float("nan")
    return float(abs(expected_focus) / proxy_mae)


def pair_lookup(pairwise: pd.DataFrame, left: str, right: str, column: str) -> float:
    direct = pairwise[(pairwise["left"] == left) & (pairwise["right"] == right)]
    if not direct.empty:
        return float(direct.iloc[0][column])
    reverse = pairwise[(pairwise["left"] == right) & (pairwise["right"] == left)]
    if not reverse.empty:
        return float(reverse.iloc[0][column])
    return float("nan")


def build_summary() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    e225 = read_csv(E225_ROUTE)
    e227 = read_csv(E227_ROUTE)
    e160 = read_csv(E160_ROUTE)
    order = read_csv(E227_ORDER)
    tri = read_csv(E228_SUMMARY).set_index("tag")
    pairwise = read_csv(E228_PAIRWISE)
    anchor_models = read_csv(ANCHOR_MODELS)

    raw05_proxy = anchor_models.loc[anchor_models["model"] == "raw05_a2c8_compat"].iloc[0]
    proxy_mae = float(raw05_proxy["mae"])
    proxy_p90 = float(raw05_proxy["p90_abs_error"])
    e216_loss_vs_e95 = E216_PUBLIC - E95_PUBLIC

    route_by_tag = {
        "e224": (e225, route_stats(e225), "jepa_first"),
        "e166": (e227, route_stats(e227), "independent_broad"),
        "e154": (e160, route_stats(e160, class_col="branch_status"), "conservative_branch"),
    }

    records: list[dict[str, Any]] = []
    for tag, (route, stats, slot_role) in route_by_tag.items():
        order_row = order.loc[order["submission"].astype(str).str.contains(str(tri.loc[tag, "file_name"]), regex=False)]
        if order_row.empty:
            order_row = order.loc[order["submission"].astype(str).str.contains(tag, regex=False)]
        order_rec = order_row.iloc[0].to_dict() if not order_row.empty else {}
        expected_focus = float(order_rec.get("expected_focus", np.nan))
        adverse_delta = float(order_rec.get("adverse_delta", np.nan))
        support_prob = float(order_rec.get("support_prob_focus_swing_weighted", np.nan))
        cos_vs_e216 = float(tri.loc[tag, "cos_vs_e216"])
        cos_vs_e224 = float(tri.loc[tag, "cos_vs_e224"])
        moved_cells = int(tri.loc[tag, "moved_cells_vs_e95"])
        moved_rows = int(tri.loc[tag, "moved_rows_vs_e95"])
        q3_share = float(tri.loc[tag, "abs_share_Q3"])
        s2_share = float(tri.loc[tag, "abs_share_S2"])
        s4_share = float(tri.loc[tag, "abs_share_S4"])

        inherited_penalty = 0.0
        if tag == "e154":
            inherited_penalty = pair_lookup(
                pairwise, "e224", "e154", "right_mass_covered_same_sign_by_left"
            )

        if tag == "e224":
            primary_question = "Was E216 a narrow S2-rank JEPA failure, or does public reject the current JEPA translator family?"
            recommended_when = "The active question is JEPA-first: test Q3/S4 capped context-to-target translation directly."
            not_recommended_when = "The next slot must minimize downside rather than maximize JEPA information."
            if_forced = "yes_current_goal"
            forced_reason = "It is the only live JEPA-specific sensor, and its cos_vs_e216 is low enough that E216 did not already answer it."
            jepa_rank = 1
            independent_rank = 2
            conservative_rank = 3
        elif tag == "e166":
            primary_question = "Is the safety atlas overconservative on broad survivor context outside the JEPA/E154 body?"
            recommended_when = "The active question is escaping the JEPA lane with a non-collinear hidden-world sensor."
            not_recommended_when = "The next slot is explicitly reserved for testing JEPA after E216."
            if_forced = "no_first_followup_if_e224_loses_or_ties"
            forced_reason = "It is the clean independent counter-world; E224/E166 cosine is only 0.074348."
            jepa_rank = 2
            independent_rank = 1
            conservative_rank = 2
        else:
            primary_question = "Does the repaired E144/E154 branch transfer after broad/JEPA losses?"
            recommended_when = "Both the JEPA and independent broad questions have been demoted or a low-movement conservative sensor is required."
            not_recommended_when = "We need maximum new information from the very next slot."
            if_forced = "no_conditional"
            forced_reason = "E154 is partly inherited by E224: E224 covers 88.6% of E154 mass same-sign, so first-slot information is lower."
            jepa_rank = 3
            independent_rank = 3
            conservative_rank = 1

        records.append(
            {
                "candidate": tag,
                "submission": f"analysis_outputs/{tri.loc[tag, 'file_name']}",
                "slot_role": slot_role,
                "primary_question": primary_question,
                "forced_one_slot_decision": if_forced,
                "forced_reason": forced_reason,
                "recommended_when": recommended_when,
                "not_recommended_when": not_recommended_when,
                "jepa_first_rank": jepa_rank,
                "independent_world_rank": independent_rank,
                "conservative_rank": conservative_rank,
                "expected_focus_vs_e95": expected_focus,
                "expected_edge_over_proxy_mae": edge_factor(expected_focus, proxy_mae),
                "adverse_delta": adverse_delta,
                "adverse_over_proxy_mae": edge_factor(adverse_delta, proxy_mae),
                "support_prob_focus_swing_weighted": support_prob,
                "cos_vs_e216": cos_vs_e216,
                "one_minus_abs_cos_vs_e216": float(1.0 - abs(cos_vs_e216)),
                "cos_vs_e224": cos_vs_e224,
                "moved_cells_vs_e95": moved_cells,
                "moved_rows_vs_e95": moved_rows,
                "abs_share_Q3": q3_share,
                "abs_share_S2": s2_share,
                "abs_share_S4": s4_share,
                "e154_inherited_penalty_if_any": inherited_penalty,
                "public_anchor_proxy_mae": proxy_mae,
                "public_anchor_proxy_p90": proxy_p90,
                "e216_loss_vs_e95": e216_loss_vs_e95,
                **stats,
            }
        )

    summary = pd.DataFrame(records).sort_values(["jepa_first_rank", "candidate"]).reset_index(drop=True)
    route_snippets = pd.concat(
        [
            compact_route(e225, "e224"),
            compact_route(e227, "e166"),
            compact_route(e160, "e154", class_col="branch_status"),
        ],
        ignore_index=True,
    )
    caveat = (
        f"raw05_a2c8_compat proxy MAE={proxy_mae:.9f}, p90={proxy_p90:.9f}; "
        "this is larger than the E95/E101/mixmin frontier gaps, so it is a geometry descriptor, not a score selector."
    )
    return summary, route_snippets, caveat


def write_report(summary: pd.DataFrame, route_snippets: pd.DataFrame, caveat: str) -> None:
    focus_cols = [
        "candidate",
        "forced_one_slot_decision",
        "jepa_first_rank",
        "independent_world_rank",
        "expected_focus_vs_e95",
        "expected_edge_over_proxy_mae",
        "adverse_delta",
        "cos_vs_e216",
        "cos_vs_e224",
        "routebook_outcomes",
        "primary_question",
    ]
    geometry_cols = [
        "candidate",
        "moved_cells_vs_e95",
        "moved_rows_vs_e95",
        "abs_share_Q3",
        "abs_share_S2",
        "abs_share_S4",
        "one_minus_abs_cos_vs_e216",
        "e154_inherited_penalty_if_any",
        "recommended_when",
        "not_recommended_when",
    ]
    route_cols = [
        "candidate",
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        "world_update_class",
        "branch_status",
        "next_action",
        "allowed_next",
        "candidate_to_test",
    ]
    route_view = route_snippets[[c for c in route_cols if c in route_snippets.columns]].copy()

    report = f"""# E229 Next Public Slot Decision

This is a no-submission audit. It folds the E216 public miss into the reusable
public-observation ledger, then decides which live file is the next most
informative public sensor.

## Core Decision

- Forced one-slot decision under the current JEPA-first question:
  `analysis_outputs/{E224_FILE}`.
- First independent follow-up if E224 ties or loses:
  `analysis_outputs/{E166_FILE}`.
- Conservative branch only after attribution or after JEPA/broad questions are
  demoted:
  `analysis_outputs/{E154_FILE}`.

The reason is not a reliable score forecast. `{caveat}` E224 is selected only
because it asks the live JEPA question directly and is nearly orthogonal to the
failed E216 S2 translator (`cos_vs_e216=0.043542`).

## Decision Table

{md_table(summary[focus_cols], n=10)}

## Geometry And Risk

{md_table(summary[geometry_cols], n=10)}

## What The Public Score Would Mean

{md_table(route_view, n=30)}

## Interpretation

- E216 does not kill every JEPA idea. It kills the masked-family S2/rank
  translator as a public-safe submission family. E224 is mostly Q3/S4 movement,
  with low E216 cosine, so it remains a separate JEPA test.
- E224/E166 are genuinely different sensors (`cosine=0.074348`, top50 overlap
  `1`). A blind blend would erase the value of the next public observation.
- E154 is useful, but not first-slot maximal information: E224 covers `0.885621`
  of E154 mass same-sign, so E154 is partly an inherited-body counterfactual.
- The public-anchor proxy still cannot choose frontier files by score. Its
  best LOOCV MAE is larger than the public gaps that separate E95, E101,
  mixmin, and E176.

## Beliefs Killed

- Killed: "E216 means all JEPA-family probes are dead." It only resolves the S2
  support-tail translator.
- Killed: "A scalar public-anchor proxy can rank the next frontier candidate."
  The proxy is useful for geometry and failure-class detection, not for
  post-E95 one-cell ordering.
- Killed for now: "Submit an E224/E166/E154 blend." E228 shows E224 and E166
  are separate high-information sensors; blending before feedback destroys the
  experiment.

## Next Action

Submit E224 only if the next public slot is meant to answer the JEPA question.
After its public score, decode it with:

```bash
python3 analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>
```

If the next slot is instead meant to escape JEPA and test an independent
counter-world, submit E166 and decode with:

```bash
python3 analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>
```
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    summary, route_snippets, caveat = build_summary()
    summary.to_csv(SUMMARY_OUT, index=False)
    route_snippets.to_csv(ROUTE_OUT, index=False)
    write_report(summary, route_snippets, caveat)
    print(f"wrote {SUMMARY_OUT.relative_to(ROOT)}")
    print(f"wrote {ROUTE_OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
