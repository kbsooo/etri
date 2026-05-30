#!/usr/bin/env python3
"""E202: pre-public component responsibility router for E176.

E201 fixes which file to submit and how to route its scalar public score. E202
pre-computes which E176 components should be blamed or credited under each score
band, so the result does not collapse into a generic Q2 tuning story.

No submission is created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

E95_FILE = OUT / "submission_e95_hardtail_541e3973.csv"
E176_FILE = OUT / "submission_e176_abl_q2_to0p75_91e49725.csv"

OUT_COMPONENT = OUT / "e202_e176_component_responsibility_component_summary.csv"
OUT_SUBJECT = OUT / "e202_e176_component_responsibility_subject_summary.csv"
OUT_OUTCOME = OUT / "e202_e176_component_responsibility_outcome_summary.csv"
OUT_REPORT = OUT / "e202_e176_component_responsibility_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    header = [str(c) for c in view.columns]

    def render(v: Any) -> str:
        if isinstance(v, float):
            return f"{v:.12g}"
        return str(v)

    def clean(s: str) -> str:
        return s.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(c) for c in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(render(row[c])) for c in view.columns) + " |")
    return "\n".join(lines)


def movement_abs_share() -> pd.DataFrame:
    e95 = pd.read_csv(E95_FILE)
    e176 = pd.read_csv(E176_FILE)
    delta_abs = (e176[TARGETS].astype(float) - e95[TARGETS].astype(float)).abs()
    sums = delta_abs.sum(axis=0)
    total = float(sums.sum())
    return pd.DataFrame(
        {
            "target": sums.index,
            "prob_abs_delta_sum": sums.values,
            "prob_abs_delta_share": sums.values / total,
        }
    )


def role_read(row: pd.Series) -> str:
    target = str(row["target"])
    expected_rank = int(row["expected_rank"])
    abs_rank = int(row["abs_movement_rank"])
    e72_rate = float(row["e72_active_rate"])
    safe_density = float(row["mean_safe_density"])
    visible_support = float(row["support_swing_weighted_visible_mean"])
    if target in {"S3", "S1", "S4"} and expected_rank <= 3:
        return "primary_s_stage_body"
    if target == "Q2" and abs_rank == 1 and expected_rank >= 5:
        return "name_mismatch_large_movement_mid_expected_gain"
    if target == "Q3" and visible_support >= 0.55:
        return "visible_supported_low_expected_share"
    if e72_rate >= 0.50:
        return "e72_like_tail_risk_component"
    if safe_density <= 0.20:
        return "low_safe_density_component"
    return "secondary_body_component"


def build_component_summary() -> pd.DataFrame:
    target_contrast = pd.read_csv(OUT / "e177_e176_public_feedback_decoder_target_contrast.csv")
    set_summary = pd.read_csv(OUT / "e179_e176_critical_cell_visibility_set_summary.csv")
    abs_share = movement_abs_share()

    full = target_contrast.loc[target_contrast["pair"].eq("e176_vs_e95_full_move")].copy()
    full["expected_abs"] = full["expected_delta_focus_mean"].abs()
    full["expected_abs_share"] = full["expected_abs"] / full["expected_abs"].sum()
    full["expected_rank"] = full["expected_abs_share"].rank(ascending=False, method="first").astype(int)

    target_sets = set_summary.loc[set_summary["set"].str.startswith("target_")].copy()
    target_sets["target"] = target_sets["set"].str.replace("target_", "", regex=False)
    target_sets = target_sets[
        [
            "target",
            "expected_delta_visible_mean",
            "support_swing_weighted_visible_mean",
            "hard_support_rate_visible_mean",
            "support_prob_min_mean",
            "all_prior_support_rate",
            "prior_split_rate",
            "flank_conflict_rate",
            "between_train_runs_rate",
        ]
    ]

    comp = full.merge(abs_share, on="target", how="left").merge(target_sets, on="target", how="left")
    comp["abs_movement_rank"] = comp["prob_abs_delta_share"].rank(ascending=False, method="first").astype(int)
    comp["expected_minus_abs_rank"] = comp["expected_rank"] - comp["abs_movement_rank"]
    comp["q_or_s"] = np.where(comp["target"].str.startswith("Q"), "Q", "S")
    comp["role_read"] = comp.apply(role_read, axis=1)
    comp = comp.sort_values(["expected_rank", "abs_movement_rank"]).reset_index(drop=True)
    return comp


def build_subject_summary() -> pd.DataFrame:
    cells = pd.read_csv(OUT / "e179_e176_critical_cell_visibility_cells.csv")
    cells["top33"] = cells["swing_rank"] <= 33
    cells["top8"] = cells["swing_rank"] <= 8
    rows: list[dict[str, Any]] = []
    for subject, g in cells.groupby("subject_id", sort=False):
        target_swing = g.groupby("target")["swing"].sum().sort_values(ascending=False)
        rows.append(
            {
                "subject_id": subject,
                "n_cells": len(g),
                "n_rows": int(g["sub_idx"].nunique()),
                "swing_sum": float(g["swing"].sum()),
                "swing_share": float(g["swing"].sum() / cells["swing"].sum()),
                "expected_delta_focus_sum": float(g["expected_delta_focus_mean"].sum()),
                "expected_delta_visible_sum": float(g["expected_delta_visible_mean"].sum()),
                "top33_cells": int(g["top33"].sum()),
                "top8_cells": int(g["top8"].sum()),
                "between_train_runs_rate": float(g["between_train_runs"].mean()),
                "e72_active_rate": float(g["e72_active"].mean()),
                "flank_conflict_rate": float(g["flank_conflict"].mean()),
                "support_visible_swing_weighted": float(np.average(g["support_probability_visible_mean"], weights=g["swing"])),
                "top_target_by_swing": str(target_swing.index[0]),
                "top_target_swing_share": float(target_swing.iloc[0] / target_swing.sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("swing_share", ascending=False).reset_index(drop=True)


def scalar_from_group_attr(pair: str, group_kind: str, group: Any, col: str) -> float:
    ga = pd.read_csv(OUT / "e177_e176_public_feedback_decoder_group_attribution.csv")
    rows = ga.loc[
        ga["pair"].eq(pair)
        & ga["group_kind"].eq(group_kind)
        & ga["group"].astype(str).eq(str(group)),
        col,
    ]
    if rows.empty:
        return float("nan")
    return float(rows.iloc[0])


def scalar_from_component(component: pd.DataFrame, target: str, col: str) -> float:
    rows = component.loc[component["target"].eq(target), col]
    if rows.empty:
        return float("nan")
    return float(rows.iloc[0])


def build_outcome_router(component: pd.DataFrame) -> pd.DataFrame:
    route = pd.read_csv(OUT / "e201_e176_public_sensor_packet_route_summary.csv")
    nulls = pd.read_csv(OUT / "e179_e176_critical_cell_visibility_null.csv")
    q2_damp = pd.read_csv(OUT / "e179_e176_q2_damping_visibility.csv")
    focus_q2 = q2_damp.loc[q2_damp["prior"].eq("focus_mean")].iloc[0]
    visible_q2 = q2_damp.loc[q2_damp["prior"].eq("visible_mean")].iloc[0]

    s_expected = scalar_from_group_attr("e176_vs_e95", "target_group", "S", "abs_expected_share")
    q_expected = scalar_from_group_attr("e176_vs_e95", "target_group", "Q", "abs_expected_share")
    between_expected = scalar_from_group_attr("e176_vs_e95", "context_type", "between_train_runs", "abs_expected_share")
    top33 = nulls.loc[nulls["set"].eq("top33_expected_flip")].iloc[0]

    common = {
        "s_group_expected_share": s_expected,
        "q_group_expected_share": q_expected,
        "between_train_runs_expected_share": between_expected,
        "q2_prob_abs_delta_share": scalar_from_component(component, "Q2", "prob_abs_delta_share"),
        "q2_expected_share": scalar_from_component(component, "Q2", "expected_abs_share"),
        "s3_expected_share": scalar_from_component(component, "S3", "expected_abs_share"),
        "s1_expected_share": scalar_from_component(component, "S1", "expected_abs_share"),
        "top33_visible_support_p_low": float(top33["p_low"]),
        "q2_damping_focus_delta": float(focus_q2["expected_delta"]),
        "q2_damping_visible_delta": float(visible_q2["expected_delta"]),
    }

    reads = {
        "q2_underopen_breakthrough": (
            "Credit broad S-stage/between-train-runs body first; Q2 damping is a secondary guard, not the whole explanation.",
            "Decompose S3/S1/S4 body and then test Q2 amplitude only as a paired contrast.",
        ),
        "clean_win": (
            "Treat E176 as a broad-body anchor; the win supports Q/S asymmetry but does not prove Q2 keep=0.75 is optimal.",
            "Run component responsibility audit before E174 or another sibling.",
        ),
        "micro_win": (
            "The sign is right but hard-label resolution is still thin; body and tail probably nearly cancel.",
            "Only E174-vs-E176 is coherent if deliberately asking the Q2 amplitude question.",
        ),
        "tie": (
            "The broad body exists but top critical cells are underresolved; the top33 visible support p_low is the warning.",
            "Use E172 only as same-family safety; no Q2 keep sweep.",
        ),
        "small_loss": (
            "Read as tail/cancellation failure, not as proof that Q2 alone is wrong.",
            "E172 if testing same-family safety; otherwise E154.",
        ),
        "e101_worse_mixmin_safe": (
            "Partial-reopen is public-misaligned despite Q2 damping.",
            "Demote E176/E174; prefer E154 repaired-branch counter-world.",
        ),
        "branch_loss": (
            "The broad partial-reopen body gives back the frontier edge.",
            "Close same-family expected-score followups and use E154/search.",
        ),
        "hard_fail": (
            "Dominant negative axis is outside this component family.",
            "Return to non-collinear latent/hidden-block search.",
        ),
    }

    rows: list[dict[str, Any]] = []
    for _, r in route.iterrows():
        interpretation, next_probe = reads[str(r["outcome"])]
        rec = {
            "outcome": r["outcome"],
            "public_lb_lo_exclusive": r["public_lb_lo_exclusive"],
            "public_lb_hi_inclusive": r["public_lb_hi_inclusive"],
            "component_interpretation": interpretation,
            "next_component_probe": next_probe,
            "do_not_infer": "Do not infer Q2-only causality from the scalar score.",
        }
        rec.update(common)
        rows.append(rec)
    return pd.DataFrame(rows)


def write_report(component: pd.DataFrame, subject: pd.DataFrame, outcome: pd.DataFrame) -> None:
    group_s = outcome["s_group_expected_share"].iloc[0]
    group_q = outcome["q_group_expected_share"].iloc[0]
    between = outcome["between_train_runs_expected_share"].iloc[0]
    q2_abs = scalar_from_component(component, "Q2", "prob_abs_delta_share")
    q2_exp = scalar_from_component(component, "Q2", "expected_abs_share")
    top33_p = outcome["top33_visible_support_p_low"].iloc[0]

    lines = [
        "# E202 E176 Component Responsibility Router",
        "",
        "## Question",
        "",
        "If E176's public score arrives, which hidden component should be credited or blamed before creating any follow-up file?",
        "",
        "## Result",
        "",
        "E176 should not be read as a Q2-only experiment. The name is misleading at component level.",
        "",
        f"- S-target group carries `{group_s:.6f}` of focus-prior expected movement versus `{group_q:.6f}` for Q targets.",
        f"- Between-train-runs rows carry `{between:.6f}` of the expected movement.",
        f"- Q2 is the largest raw probability movement share (`{q2_abs:.6f}`) but only `{q2_exp:.6f}` of expected focus contribution.",
        f"- The top33 hard-label cells remain weakly visible: target-matched visible-support `p_low={top33_p:.6f}`.",
        "",
        "Therefore a good E176 score mainly supports the broad S-stage / between-train-runs body with Q2 damping as a guard. A weak or bad score mainly says the hard-label tail/cancellation layer was unresolved; it should not trigger Q2 keep-factor tuning.",
        "",
        "## Target Components",
        "",
        md_table(
            component,
            [
                "target",
                "q_or_s",
                "n_cells",
                "expected_delta_focus_mean",
                "expected_abs_share",
                "prob_abs_delta_share",
                "expected_rank",
                "abs_movement_rank",
                "support_swing_weighted_visible_mean",
                "e72_active_rate",
                "mean_safe_density",
                "role_read",
            ],
        ),
        "",
        "## Subject Concentration",
        "",
        md_table(
            subject,
            [
                "subject_id",
                "n_cells",
                "n_rows",
                "swing_share",
                "expected_delta_focus_sum",
                "top33_cells",
                "top8_cells",
                "between_train_runs_rate",
                "e72_active_rate",
                "support_visible_swing_weighted",
                "top_target_by_swing",
                "top_target_swing_share",
            ],
            n=10,
        ),
        "",
        "## Outcome Component Router",
        "",
        md_table(
            outcome,
            [
                "outcome",
                "public_lb_lo_exclusive",
                "public_lb_hi_inclusive",
                "component_interpretation",
                "next_component_probe",
                "do_not_infer",
            ],
            n=20,
        ),
        "",
        "## Decision",
        "",
        "No submission is created. E202 is a pre-public interpretation guard layered on top of E201. If E176 wins, start by decomposing S3/S1/S4 and between-train-runs body. If it ties or loses, read the result through hard-tail/cancellation and the E201 route table before any E172/E154/E174 choice.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n")


def main() -> None:
    component = build_component_summary()
    subject = build_subject_summary()
    outcome = build_outcome_router(component)

    component.to_csv(OUT_COMPONENT, index=False)
    subject.to_csv(OUT_SUBJECT, index=False)
    outcome.to_csv(OUT_OUTCOME, index=False)
    write_report(component, subject, outcome)

    print(f"wrote {OUT_COMPONENT.relative_to(ROOT)}")
    print(f"wrote {OUT_SUBJECT.relative_to(ROOT)}")
    print(f"wrote {OUT_OUTCOME.relative_to(ROOT)}")
    print(f"wrote {OUT_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
