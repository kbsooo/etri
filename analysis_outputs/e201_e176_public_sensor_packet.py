#!/usr/bin/env python3
"""E201: file audit and pre-registered public sensor packet for E176.

This does not create a new submission. It freezes how to interpret the next
public observation from E176 before the score is known.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1.0e-12

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405

FILES = {
    "e95": "submission_e95_hardtail_541e3973.csv",
    "e176": "submission_e176_abl_q2_to0p75_91e49725.csv",
    "e172": "submission_e172_vis_pos_all_keep0p25_d90f4407.csv",
    "e174": "submission_e174_ro_fc_top75_to1p0_95638e73.csv",
    "e154": "submission_e154_s3repair_9f2e2e73.csv",
}

OUT_FILE_SUMMARY = OUT / "e201_e176_public_sensor_packet_file_summary.csv"
OUT_ROUTE_SUMMARY = OUT / "e201_e176_public_sensor_packet_route_summary.csv"
OUT_SUMMARY = OUT / "e201_e176_public_sensor_packet_summary.csv"
OUT_REPORT = OUT / "e201_e176_public_sensor_packet_report.md"


@dataclass(frozen=True)
class RouteRule:
    worldview_update_class: str
    next_candidate_role: str
    strengthened: str
    weakened: str
    kill_switch: str
    private_risk_read: str
    required_next_evidence: str


ROUTE_RULES: dict[str, RouteRule] = {
    "q2_underopen_breakthrough": RouteRule(
        worldview_update_class="promote_broad_q2_underopen",
        next_candidate_role="no_immediate_sibling; decompose non-Q2/S-stage responsibility",
        strengthened="H176 broad partial-reopen body + Q2 under-opening is public-real",
        weakened="E172-first safety priority; E174 full-Q2 reopen as score file",
        kill_switch="If the gain is driven only by a single public-cell illusion in later contrast, demote amplitude tuning.",
        private_risk_read="Upside is real but still hard-label fragile; avoid over-increasing Q2.",
        required_next_evidence="Target/component attribution that separates Q2 damping from S1/S2/S3 reopening.",
    ),
    "clean_win": RouteRule(
        worldview_update_class="anchor_e176_as_current_world",
        next_candidate_role="conditional component responsibility audit",
        strengthened="Q/S-asymmetric partial reopening is readable beyond the E95-mixmin edge",
        weakened="Conservative E154-first branch; E172-first private-risk branch",
        kill_switch="A later E174 loss would confirm Q2 damping, not invalidate E176 body.",
        private_risk_read="Score-safe enough to become the expected-score anchor, not enough for 0.54 claims.",
        required_next_evidence="Which target family contributed: Q2 damping versus S-stage body.",
    ),
    "micro_win": RouteRule(
        worldview_update_class="weakly_promote_e176_but_keep_resolution_doubt",
        next_candidate_role="E174 only as deliberate Q2-amplitude sensor",
        strengthened="E176 direction is plausible under public hard labels",
        weakened="Large-margin broad-body worldview",
        kill_switch="If E174 does not improve in the next contrast, stop Q2 amplitude siblings.",
        private_risk_read="Very thin edge; one or two cells can reverse it.",
        required_next_evidence="E174-vs-E176 Q2 amplitude contrast or post-score cell-attribution audit.",
    ),
    "tie": RouteRule(
        worldview_update_class="underresolved_same_family",
        next_candidate_role="E172 same-family safety if continuing this branch",
        strengthened="Hard-label resolution/cancellation explains plateau",
        weakened="E176 as decisive broad-body signal",
        kill_switch="Do not tune Q2 keep from a tie; it is below resolution.",
        private_risk_read="E95 remains practical; E176 may be neither good nor bad enough to inform score path.",
        required_next_evidence="E172 safety contrast or a non-collinear branch; no keep-factor sweep.",
    ),
    "small_loss": RouteRule(
        worldview_update_class="demote_e176_but_not_family",
        next_candidate_role="E172 if testing broad-tail repair, otherwise E154",
        strengthened="Q2 damping did not fully neutralize broad partial-reopen risk",
        weakened="E176-first expected-score dominance",
        kill_switch="Another E176 sibling by Q2 keep-factor is disallowed.",
        private_risk_read="Family may still be useful, but public expected-score file should be safer.",
        required_next_evidence="E172 same-family safety or E154 counter-world branch, chosen by question.",
    ),
    "e101_worse_mixmin_safe": RouteRule(
        worldview_update_class="demote_partial_reopen_branch",
        next_candidate_role="E154 repaired-branch counter-world",
        strengthened="Partial-reopen public misalignment survived Q2 damping",
        weakened="E174/E176/E172 as score-improving line",
        kill_switch="Do not submit E174 next except as falsification, not score improvement.",
        private_risk_read="Branch remains mixmin-safe but below current frontier logic.",
        required_next_evidence="Counter-world repaired branch or new latent, not same-family amplitude.",
    ),
    "branch_loss": RouteRule(
        worldview_update_class="close_same_family_expected_score_lane",
        next_candidate_role="E154 or rebuild bad-axis model",
        strengthened="Current broad partial-reopen axis gives back frontier edge",
        weakened="E176/E174/E172/E169 as expected-score follow-ups",
        kill_switch="Close same-family followups unless explicitly spending a falsification slot.",
        private_risk_read="Risk is not just Q2; dominant bad axis is unresolved.",
        required_next_evidence="Non-collinear latent or repaired-branch counter-world.",
    ),
    "hard_fail": RouteRule(
        worldview_update_class="search_non_collinear_latent",
        next_candidate_role="no same-family submission; return to structure discovery",
        strengthened="Dominant negative axis is outside Q2 damping and partial-reopen family",
        weakened="All current same-family frontier challenge assumptions",
        kill_switch="Stop threshold/keep-factor/target-drop siblings.",
        private_risk_read="Public observation says the family is incompatible, not merely noisy.",
        required_next_evidence="New hidden block/sequence/target-dependency evidence before next submission.",
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_submission(file_name: str) -> pd.DataFrame:
    path = OUT / file_name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def same_key_order(left: pd.DataFrame, right: pd.DataFrame) -> bool:
    return left[KEYS].astype(str).equals(right[KEYS].astype(str))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    rendered: list[list[str]] = []
    for _, row in view.iterrows():
        vals: list[str] = []
        for col in view.columns:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.12g}")
            else:
                vals.append(str(val))
        rendered.append(vals)
    header = [str(c) for c in view.columns]

    def clean(cell: str) -> str:
        return cell.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(c) for c in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for vals in rendered:
        lines.append("| " + " | ".join(clean(v) for v in vals) + " |")
    return "\n".join(lines)


def delta_share_string(delta_abs: pd.DataFrame) -> str:
    total = float(delta_abs.to_numpy().sum())
    if total <= EPS:
        return "none"
    shares = delta_abs.sum(axis=0).sort_values(ascending=False) / total
    return ";".join(f"{k}:{v:.6f}" for k, v in shares.items())


def audit_files() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    base = read_submission(FILES["e95"])
    expected_cols = KEYS + TARGETS
    rows: list[dict[str, Any]] = []
    for candidate, file_name in FILES.items():
        path = OUT / file_name
        df = read_submission(file_name)
        target = df[TARGETS].astype(float)
        delta = target - base[TARGETS].astype(float)
        changed = delta.abs() > EPS
        abs_delta = delta.abs()
        max_abs_delta = float(abs_delta.to_numpy().max())
        rows.append(
            {
                "candidate": candidate,
                "file": str(path.relative_to(ROOT)),
                "sha256": sha256_file(path),
                "n_rows": len(df),
                "n_cols": len(df.columns),
                "columns_match_sample": list(df.columns) == expected_cols,
                "key_order_match_sample": same_key_order(df, sample),
                "duplicate_key_rows": int(df.duplicated(KEYS).sum()),
                "target_min": float(target.to_numpy().min()),
                "target_max": float(target.to_numpy().max()),
                "finite_targets": bool(np.isfinite(target.to_numpy()).all()),
                "valid_probability_range": bool((target.to_numpy() >= 0).all() and (target.to_numpy() <= 1).all()),
                "changed_cells_vs_e95": int(changed.to_numpy().sum()),
                "changed_rows_vs_e95": int(changed.any(axis=1).sum()),
                "mean_abs_delta_vs_e95": float(abs_delta.to_numpy().mean()),
                "max_abs_delta_vs_e95": max_abs_delta,
                "target_abs_delta_share_vs_e95": delta_share_string(abs_delta),
                "ready_for_submission": bool(
                    len(df) == len(sample)
                    and list(df.columns) == expected_cols
                    and same_key_order(df, sample)
                    and int(df.duplicated(KEYS).sum()) == 0
                    and np.isfinite(target.to_numpy()).all()
                    and (target.to_numpy() >= 0).all()
                    and (target.to_numpy() <= 1).all()
                ),
            }
        )
    return pd.DataFrame(rows)


def augment_routes() -> pd.DataFrame:
    bands = pd.read_csv(OUT / "e177_e176_public_feedback_decoder_bands.csv")
    pairwise = pd.read_csv(OUT / "e177_e176_public_feedback_decoder_pairwise.csv")
    e197 = pd.read_csv(OUT / "e197_public_support_mass_candidate_profiles.csv")
    e199 = pd.read_csv(OUT / "e199_candidate_shape_e72_exposure_summary.csv")
    e200 = pd.read_csv(OUT / "e200_e176_vs_e172_first_sensor_metrics.csv")

    def metric(name: str) -> float:
        rows = e200.loc[e200["metric"].eq(name), "value"]
        if rows.empty:
            return float("nan")
        return float(rows.iloc[0])

    def pmetric(new: str, base: str, col: str) -> float:
        rows = pairwise.loc[pairwise["new"].eq(new) & pairwise["base"].eq(base), col]
        if rows.empty:
            return float("nan")
        return float(rows.iloc[0])

    def profile(candidate: str, col: str) -> Any:
        rows = e197.loc[e197["candidate"].eq(candidate), col]
        if rows.empty:
            return ""
        return rows.iloc[0]

    def shape(candidate: str, col: str) -> Any:
        rows = e199.loc[e199["candidate"].eq(candidate), col]
        if rows.empty:
            return ""
        return rows.iloc[0]

    route_rows: list[dict[str, Any]] = []
    for _, band in bands.iterrows():
        rule = ROUTE_RULES[band["outcome"]]
        route_rows.append(
            {
                "outcome": band["outcome"],
                "public_lb_lo_exclusive": band["public_lb_lo_exclusive"],
                "public_lb_hi_inclusive": band["public_lb_hi_inclusive"],
                "beats_e95": band["beats_e95"],
                "beats_e101": band["beats_e101"],
                "beats_mixmin": band["beats_mixmin"],
                "worldview_update_class": rule.worldview_update_class,
                "next_candidate_role": rule.next_candidate_role,
                "strengthened": rule.strengthened,
                "weakened": rule.weakened,
                "kill_switch": rule.kill_switch,
                "private_risk_read": rule.private_risk_read,
                "required_next_evidence": rule.required_next_evidence,
                "e177_next_action": band["next_action"],
                "e177_forbidden_action": band["forbidden_action"],
                "e176_vs_e95_focus_expected_delta": pmetric("e176_q2_underopen", "e95", "expected_delta_focus_mean"),
                "e176_vs_e95_cells_for_edge": pmetric("e176_q2_underopen", "e95", "cells_for_e95_edge"),
                "e176_vs_e172_focus_expected_delta": pmetric("e176_q2_underopen", "e172_tail_repair", "expected_delta_focus_mean"),
                "e176_vs_e172_moved_cells": pmetric("e176_q2_underopen", "e172_tail_repair", "moved_cells"),
                "e176_vs_e154_focus_expected_delta": pmetric("e176_q2_underopen", "e154", "expected_delta_focus_mean"),
                "e176_vs_e154_moved_cells": pmetric("e176_q2_underopen", "e154", "moved_cells"),
                "e176_support_surplus_visible": profile("e176", "surplus_to_tie_visible_mean"),
                "e172_support_surplus_visible": profile("e172", "surplus_to_tie_visible_mean"),
                "e176_shape_e72_prob": shape("e176", "direct_shape_e72_prob"),
                "e172_shape_e72_prob": shape("e172", "direct_shape_e72_prob"),
                "e154_shape_e72_prob": shape("e154", "direct_shape_e72_prob"),
                "e200_e176_expected_edge_over_e172": metric("e176_expected_edge_over_e172"),
                "e200_same_family_to_counterworld_delta_ratio": metric("same_family_to_counterworld_delta_ratio"),
            }
        )
    return pd.DataFrame(route_rows)


def build_summary(file_summary: pd.DataFrame, route_summary: pd.DataFrame) -> pd.DataFrame:
    e176 = file_summary.loc[file_summary["candidate"].eq("e176")].iloc[0]
    e172 = file_summary.loc[file_summary["candidate"].eq("e172")].iloc[0]
    first_route = route_summary.loc[route_summary["outcome"].eq("clean_win")].iloc[0]
    rows = [
        ("recommended_submission", e176["file"]),
        ("recommended_sha256", e176["sha256"]),
        ("recommended_ready_for_submission", e176["ready_for_submission"]),
        ("recommended_changed_cells_vs_e95", e176["changed_cells_vs_e95"]),
        ("recommended_changed_rows_vs_e95", e176["changed_rows_vs_e95"]),
        ("e176_vs_e172_changed_cells", 75),
        ("e172_ready_for_submission", e172["ready_for_submission"]),
        ("current_frontier_file", "analysis_outputs/submission_e95_hardtail_541e3973.csv"),
        ("current_frontier_public_lb", E95_PUBLIC),
        ("mixmin_public_lb", MIXMIN_PUBLIC),
        ("e101_public_lb", E101_PUBLIC),
        ("clean_win_hi_public_lb", first_route["public_lb_hi_inclusive"]),
        ("router_rule", "Use route_summary outcome matching observed E176 public LB before making another file."),
        ("decoder_command", "python3 analysis_outputs/e177_e176_public_feedback_decoder.py --score <E176_PUBLIC_LB>"),
    ]
    return pd.DataFrame(rows, columns=["key", "value"])


def write_report(file_summary: pd.DataFrame, route_summary: pd.DataFrame, summary: pd.DataFrame) -> None:
    e176 = file_summary.loc[file_summary["candidate"].eq("e176")].iloc[0]
    lines = [
        "# E201 E176 Public Sensor Packet",
        "",
        "## Question",
        "",
        "Before submitting E176, can we freeze the file identity and the score-to-worldview router so the next public LB observation is interpreted as evidence rather than post-hoc tuning fuel?",
        "",
        "## Result",
        "",
        "E176 remains the first public sensor, and this packet fixes how to read its public score before that score is known.",
        "",
        f"- File: `{e176['file']}`",
        f"- SHA256: `{e176['sha256']}`",
        f"- Ready for submission: `{e176['ready_for_submission']}`",
        f"- Changed cells vs E95: `{e176['changed_cells_vs_e95']}` over `{e176['changed_rows_vs_e95']}` rows",
        f"- Target delta share vs E95: `{e176['target_abs_delta_share_vs_e95']}`",
        "",
        "The important rule is negative: do not interpret the E176 public score with scalar intuition after seeing it. Use the pre-registered route below.",
        "",
        "## File Audit",
        "",
        md_table(
            file_summary,
            [
                "candidate",
                "ready_for_submission",
                "n_rows",
                "columns_match_sample",
                "key_order_match_sample",
                "duplicate_key_rows",
                "target_min",
                "target_max",
                "changed_cells_vs_e95",
                "changed_rows_vs_e95",
                "mean_abs_delta_vs_e95",
                "max_abs_delta_vs_e95",
            ],
        ),
        "",
        "## Score Router",
        "",
        md_table(
            route_summary,
            [
                "outcome",
                "public_lb_lo_exclusive",
                "public_lb_hi_inclusive",
                "worldview_update_class",
                "next_candidate_role",
                "strengthened",
                "weakened",
                "kill_switch",
            ],
            n=20,
        ),
        "",
        "## Minimal Decision Rule",
        "",
        "- Better than `0.5762883298`: E176 is useful; decompose responsibility, do not rush another sibling.",
        "- `0.5762883298` to `0.576300366`: same-family signal is underresolved or slightly bad; E172 is the only coherent same-family follow-up.",
        "- Worse than `0.576300366`: demote partial-reopen branch; prefer E154 or a non-collinear latent search.",
        "- Worse than `0.5763413298`: close same-family expected-score lane.",
        "",
        "## Summary Keys",
        "",
        md_table(summary),
        "",
        "## Interpretation",
        "",
        "E201 does not add score. It removes degrees of freedom. The next E176 public LB should resolve a worldview branch, not invite another Q2 keep-factor sweep.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n")


def main() -> None:
    file_summary = audit_files()
    route_summary = augment_routes()
    summary = build_summary(file_summary, route_summary)

    file_summary.to_csv(OUT_FILE_SUMMARY, index=False)
    route_summary.to_csv(OUT_ROUTE_SUMMARY, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    write_report(file_summary, route_summary, summary)

    print(f"wrote {OUT_FILE_SUMMARY.relative_to(ROOT)}")
    print(f"wrote {OUT_ROUTE_SUMMARY.relative_to(ROOT)}")
    print(f"wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"wrote {OUT_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
