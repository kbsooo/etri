#!/usr/bin/env python3
"""E205: executable E176 public-feedback decoder.

This combines E201 score routing, E202 component responsibility, E203
body/tail knockout anatomy, and E204 follow-up geometry into one routebook.

Usage:
  python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py
  python3 analysis_outputs/e205_e176_public_feedback_executable_decoder.py --score 0.57629

No submission is created.
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

E201_ROUTE = OUT / "e201_e176_public_sensor_packet_route_summary.csv"
E202_OUTCOME = OUT / "e202_e176_component_responsibility_outcome_summary.csv"
E203_COMPONENTS = OUT / "e203_e176_component_knockout_stress_components.csv"
E204_FOLLOWUP = OUT / "e204_e176_followup_correction_map_summary.csv"

OUT_ROUTEBOOK = OUT / "e205_e176_public_feedback_executable_decoder_routebook.csv"
OUT_EXAMPLES = OUT / "e205_e176_public_feedback_executable_decoder_examples.csv"
OUT_REPORT = OUT / "e205_e176_public_feedback_executable_decoder_report.md"
OUT_SELECTED = OUT / "e205_e176_public_feedback_executable_decoder_selected.json"

FOLLOWUP_FILES = {
    "e172_safety": "analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv",
    "e154_counterworld": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
    "e174_q2_reopen": "analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv",
    "e176": "analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv",
    "none": "",
    "search": "",
}


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()

    def render(v: Any) -> str:
        if isinstance(v, float):
            return f"{v:.12g}"
        return str(v)

    def clean(s: str) -> str:
        return s.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(str(c)) for c in view.columns) + " |",
        "| " + " | ".join("---" for _ in view.columns) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(render(row[c])) for c in view.columns) + " |")
    return "\n".join(lines)


def parse_bound(value: Any) -> float:
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"inf", "+inf", "infinity", "+infinity"}:
            return float("inf")
        if text in {"-inf", "-infinity"}:
            return float("-inf")
    return float(value)


def select_followup(outcome: str) -> tuple[str, str, str]:
    """Return candidate key, route role, and route condition."""
    if outcome in {"q2_underopen_breakthrough", "clean_win"}:
        return (
            "none",
            "no_immediate_submission",
            "First decompose broad S-stage / between-train-runs body; E174 only after an explicit Q2 amplitude question.",
        )
    if outcome == "micro_win":
        return (
            "e174_q2_reopen",
            "optional_q2_amplitude_probe",
            "Use only if deliberately spending a slot on Q2 amplitude after weak broad-body validation.",
        )
    if outcome == "tie":
        return (
            "e172_safety",
            "same_family_safety",
            "Use only if continuing the same family; no Q2 keep sweep.",
        )
    if outcome == "small_loss":
        return (
            "e172_safety",
            "same_family_safety_or_e154",
            "E172 if asking safety; E154 if asking whether to exit the E176 body.",
        )
    if outcome in {"e101_worse_mixmin_safe", "branch_loss"}:
        return (
            "e154_counterworld",
            "body_exit_counterworld",
            "Demote partial-reopen; test repaired-branch counter-world or search.",
        )
    if outcome == "hard_fail":
        return (
            "search",
            "non_collinear_search",
            "Close same-family expected-score lane and return to hidden-block/sequence/target-dependency search.",
        )
    return ("none", "unknown", "No route.")


def body_constants(e203: pd.DataFrame) -> dict[str, float]:
    lookup = e203.set_index("component")
    return {
        "e176_full_focus_delta": float(lookup.at["full", "expected_delta_focus"]),
        "s_only_focus_share": float(lookup.at["only_S", "expected_focus_share"]),
        "primary_s_focus_share": float(lookup.at["only_primary_S", "expected_focus_share"]),
        "between_train_runs_focus_share": float(lookup.at["only_between_train_runs", "expected_focus_share"]),
        "q2_only_focus_share": float(lookup.at["only_Q2", "expected_focus_share"]),
        "top33_focus_share": float(lookup.at["only_top33", "expected_focus_share"]),
        "drop_top33_remaining_focus_share": float(lookup.at["drop_top33", "expected_focus_share"]),
        "top33_visible_support": float(lookup.at["only_top33", "support_visible_swing_weighted"]),
    }


def build_routebook() -> pd.DataFrame:
    e201 = pd.read_csv(E201_ROUTE)
    e202 = pd.read_csv(E202_OUTCOME)
    e203 = pd.read_csv(E203_COMPONENTS)
    e204 = pd.read_csv(E204_FOLLOWUP)
    constants = body_constants(e203)

    merged = e201.merge(
        e202[
            [
                "outcome",
                "component_interpretation",
                "next_component_probe",
                "do_not_infer",
                "s_group_expected_share",
                "q_group_expected_share",
                "between_train_runs_expected_share",
                "q2_expected_share",
                "top33_visible_support_p_low",
            ]
        ],
        on="outcome",
        how="left",
    )

    rows: list[dict[str, Any]] = []
    follow_lookup = e204.set_index("candidate").to_dict("index")
    for _, r in merged.iterrows():
        outcome = str(r["outcome"])
        followup, followup_role, condition = select_followup(outcome)
        follow = follow_lookup.get(followup, {})
        rows.append(
            {
                "outcome": outcome,
                "public_lb_lo_exclusive": parse_bound(r["public_lb_lo_exclusive"]),
                "public_lb_hi_inclusive": parse_bound(r["public_lb_hi_inclusive"]),
                "worldview_update_class": r["worldview_update_class"],
                "component_interpretation": r["component_interpretation"],
                "followup_candidate": followup,
                "followup_file": FOLLOWUP_FILES.get(followup, ""),
                "followup_role": followup_role,
                "followup_condition": condition,
                "forbidden_action": "; ".join(
                    str(x)
                    for x in [
                        r.get("e177_forbidden_action", ""),
                        r.get("do_not_infer", ""),
                    ]
                    if str(x) and str(x) != "nan"
                ),
                "required_next_evidence": r["required_next_evidence"],
                "strengthened": r["strengthened"],
                "weakened": r["weakened"],
                "kill_switch": r["kill_switch"],
                "s_only_focus_share": constants["s_only_focus_share"],
                "primary_s_focus_share": constants["primary_s_focus_share"],
                "between_train_runs_focus_share": constants["between_train_runs_focus_share"],
                "q2_only_focus_share": constants["q2_only_focus_share"],
                "top33_focus_share": constants["top33_focus_share"],
                "drop_top33_remaining_focus_share": constants["drop_top33_remaining_focus_share"],
                "top33_visible_support": constants["top33_visible_support"],
                "followup_off_e176_abs_share": follow.get("off_e176_abs_share", np.nan),
                "followup_rollback_abs_share": follow.get("rollback_abs_share_in_overlap", np.nan),
                "followup_body_rollback_fraction": follow.get("e176_body_rollback_fraction", np.nan),
                "followup_changed_cells": follow.get("n_changed_cells_vs_e176", np.nan),
                "followup_top33_rollback_count": follow.get("top33_rollback_count", np.nan),
            }
        )
    return pd.DataFrame(rows)


def decode_score(routebook: pd.DataFrame, score: float) -> dict[str, Any]:
    rows = routebook.loc[
        (score > routebook["public_lb_lo_exclusive"]) & (score <= routebook["public_lb_hi_inclusive"])
    ]
    if rows.empty:
        raise ValueError(f"score {score} did not match any route")
    rec = rows.iloc[0].to_dict()
    rec["score"] = float(score)
    return rec


def example_scores(routebook: pd.DataFrame) -> pd.DataFrame:
    examples = [
        0.5762500000,
        0.5762700000,
        0.5762820000,
        0.5762910000,
        0.5762970000,
        0.5763030000,
        0.5763200000,
        0.5763500000,
    ]
    rows = []
    for score in examples:
        rec = decode_score(routebook, score)
        rows.append(
            {
                "score": score,
                "outcome": rec["outcome"],
                "worldview_update_class": rec["worldview_update_class"],
                "followup_candidate": rec["followup_candidate"],
                "followup_role": rec["followup_role"],
                "component_interpretation": rec["component_interpretation"],
            }
        )
    return pd.DataFrame(rows)


def write_report(routebook: pd.DataFrame, examples: pd.DataFrame, selected: dict[str, Any] | None) -> None:
    lines = [
        "# E205 E176 Public-Feedback Executable Decoder",
        "",
        "## Question",
        "",
        "Can the pending E176 public score be decoded without post-hoc scalar intuition?",
        "",
        "## Result",
        "",
        "E205 turns E201-E204 into an executable routebook. A future score maps to exactly one score band, one component interpretation, one forbidden-action set, and one follow-up role.",
        "",
        "Core invariants baked into the decoder:",
        "",
        "- E176 is broad S-stage / between-train-runs body first.",
        "- Q2-only share is small relative to S/body, so Q2 amplitude is never the first post-score explanation.",
        "- Top33 is a compact cancellation layer, not the whole signal.",
        "- E172, E154, and E174 are different route probes: safety rollback, body-exit counter-world, and Q2 amplitude.",
        "",
        "## Example Decodes",
        "",
        md_table(
            examples,
            [
                "score",
                "outcome",
                "worldview_update_class",
                "followup_candidate",
                "followup_role",
                "component_interpretation",
            ],
            n=20,
        ),
        "",
        "## Full Routebook",
        "",
        md_table(
            routebook,
            [
                "outcome",
                "public_lb_lo_exclusive",
                "public_lb_hi_inclusive",
                "worldview_update_class",
                "component_interpretation",
                "followup_candidate",
                "followup_role",
                "followup_condition",
                "forbidden_action",
            ],
            n=20,
        ),
        "",
        "## Body/Tail Constants",
        "",
        md_table(
            routebook[
                [
                    "outcome",
                    "s_only_focus_share",
                    "primary_s_focus_share",
                    "between_train_runs_focus_share",
                    "q2_only_focus_share",
                    "top33_focus_share",
                    "drop_top33_remaining_focus_share",
                    "top33_visible_support",
                ]
            ].head(1),
            n=1,
        ),
        "",
    ]
    if selected is not None:
        lines.extend(
            [
                "## Selected Score Decode",
                "",
                "```json",
                json.dumps(selected, indent=2, ensure_ascii=False, sort_keys=True),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Decision",
            "",
            "No submission is created. After E176 public feedback, run this decoder with `--score` before choosing any follow-up file.",
            "",
        ]
    )
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", type=float, default=None, help="Optional E176 public LB score to decode.")
    args = parser.parse_args()

    routebook = build_routebook()
    examples = example_scores(routebook)
    selected = decode_score(routebook, args.score) if args.score is not None else None
    routebook.to_csv(OUT_ROUTEBOOK, index=False)
    examples.to_csv(OUT_EXAMPLES, index=False)
    if selected is None:
        if OUT_SELECTED.exists():
            OUT_SELECTED.unlink()
    else:
        OUT_SELECTED.write_text(json.dumps(selected, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        print(json.dumps(selected, indent=2, ensure_ascii=False, sort_keys=True))
    write_report(routebook, examples, selected)
    print(f"wrote {OUT_ROUTEBOOK}")
    print(f"wrote {OUT_EXAMPLES}")
    print(f"wrote {OUT_REPORT}")


if __name__ == "__main__":
    main()
