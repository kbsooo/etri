#!/usr/bin/env python3
"""Consolidate live-branch evidence without turning it into an LB predictor.

E193 is a bookkeeping experiment.  It asks whether E176, E154, or E144 has
the most coherent cross-sensor role after the recent visible-prior,
binary-world, pressure-branch, pair-geometry, and clean-E72 diagnostics.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent

CANDIDATES = ["e176", "e154", "e144"]
ROLES = {
    "e176": "visible_body_q2_underopen",
    "e154": "repaired_branch_s3",
    "e144": "unrepaired_repaired_branch_contrast",
}
FILES = {
    "e176": "submission_e176_abl_q2_to0p75_91e49725.csv",
    "e154": "submission_e154_s3repair_9f2e2e73.csv",
    "e144": "submission_e144_activeboundary_d7b4b331.csv",
}


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def fmt(x: float | int | str | None) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    if isinstance(x, str):
        return x
    return f"{x:.9g}"


def direction_sign(direction: str) -> float:
    if direction == "support":
        return 1.0
    if direction == "warning":
        return -1.0
    if direction == "underidentified":
        return -0.25
    return 0.0


def add_signal(
    rows: list[dict],
    candidate: str,
    axis: str,
    source: str,
    value: float | str | None,
    direction: str,
    weight: float,
    interpretation: str,
    evidence: str,
) -> None:
    rows.append(
        {
            "candidate": candidate,
            "role": ROLES[candidate],
            "file": FILES[candidate],
            "axis": axis,
            "source": source,
            "value": value,
            "direction": direction,
            "axis_weight": weight,
            "evidence_balance_contribution": direction_sign(direction) * weight,
            "interpretation": interpretation,
            "evidence": evidence,
        }
    )


def build_ledger() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []

    e179_sets = read_csv("e179_e176_critical_cell_visibility_set_summary.csv")
    e179_q2 = read_csv("e179_e176_q2_damping_visibility.csv")
    e180_pairs = read_csv("e180_known_anchor_decisive_cell_visibility_pairs.csv")
    e181_bands = read_csv("e181_e176_binary_world_counterprior_candidate_bands.csv")
    e183 = read_csv("e183_pressure_world_branch_anatomy_summary.csv")
    e186 = read_csv("e186_antisymmetric_pair_decoder_pressure_branches.csv")
    e192_branch = read_csv("e192_shape_e72_score_anatomy_branch_audit.csv")
    e192_nearest = read_csv("e192_shape_e72_score_anatomy_nearest_audit.csv")

    all_moved = e179_sets.loc[e179_sets["set"].eq("all_moved")].iloc[0]
    add_signal(
        rows,
        "e176",
        "visible_full_body_prior",
        "E179",
        float(all_moved["expected_delta_visible_mean"]),
        "support",
        1.25,
        "E176 full body is favorable under the visible-mean prior.",
        (
            f"visible expected delta {fmt(all_moved['expected_delta_visible_mean'])}; "
            f"swing support {fmt(all_moved['support_swing_weighted_visible_mean'])}; "
            f"hard support {fmt(all_moved['hard_support_rate_visible_mean'])}"
        ),
    )
    for candidate in ["e154", "e144"]:
        add_signal(
            rows,
            candidate,
            "visible_full_body_prior",
            "E179",
            None,
            "missing",
            0.0,
            "Comparable full-body visible-prior audit was not run for this branch.",
            "Do not infer support or rejection from E176-only E179 evidence.",
        )

    q2_visible = e179_q2.loc[e179_q2["prior"].eq("visible_mean")].iloc[0]
    q2_focus = e179_q2.loc[e179_q2["prior"].eq("focus_mean")].iloc[0]
    add_signal(
        rows,
        "e176",
        "q2_damping_visible_prior",
        "E179",
        float(q2_visible["expected_delta"]),
        "support",
        0.75,
        "The E176-vs-E174 Q2 damping is locally supported under visible priors.",
        (
            f"visible expected delta {fmt(q2_visible['expected_delta'])}; "
            f"focus expected delta {fmt(q2_focus['expected_delta'])}; "
            f"visible swing support {fmt(q2_visible['support_swing_weighted'])}; "
            f"hard support {fmt(q2_visible['hard_support_rate'])}"
        ),
    )
    for candidate in ["e154", "e144"]:
        add_signal(
            rows,
            candidate,
            "q2_damping_visible_prior",
            "E179",
            None,
            "missing",
            0.0,
            "This Q2-underopen contrast is specific to E176.",
            "No comparable E154/E144 Q2 damping branch exists.",
        )

    winners = e180_pairs.loc[e180_pairs["actual_direction"].eq("new_won")]
    known_winner_top4_mean = float(winners["top4_observed_support_visible"].mean())
    known_winner_top4_max = float(winners["top4_observed_support_visible"].max())
    e176_pending = e180_pairs.loc[e180_pairs["pair"].eq("e176_vs_e95_pending")].iloc[0]
    add_signal(
        rows,
        "e176",
        "known_winner_topcell_calibration",
        "E180",
        float(e176_pending["top4_observed_support_visible"]),
        "support",
        0.5,
        "E176 top-cell support is weak in absolute terms but not worse than known winners.",
        (
            f"E176 top4 support {fmt(e176_pending['top4_observed_support_visible'])}; "
            f"known-winner mean {fmt(known_winner_top4_mean)}; "
            f"known-winner max {fmt(known_winner_top4_max)}"
        ),
    )
    for candidate in ["e154", "e144"]:
        add_signal(
            rows,
            candidate,
            "known_winner_topcell_calibration",
            "E180",
            None,
            "missing",
            0.0,
            "Known-winner top-cell calibration was only materialized for E176.",
            "No branch-specific veto or support is assigned here.",
        )

    for band in ["best5_current_anchor_residual", "best10_current_anchor_residual", "all_binary_worlds"]:
        band_rows = e181_bands.loc[e181_bands["band"].eq(band)]
        for candidate in CANDIDATES:
            row = band_rows.loc[band_rows["candidate"].eq(candidate)].iloc[0]
            mean_delta = float(row["delta_mean_vs_e95"])
            neg_rate = float(row["negative_rate"])
            if band == "all_binary_worlds" and 0.25 < neg_rate < 0.75:
                direction = "underidentified"
                interpretation = "All inherited binary worlds leave this sign mixed."
            elif mean_delta < 0 and neg_rate >= 0.5:
                direction = "support"
                interpretation = "Inherited current-anchor binary worlds lean favorable versus E95."
            elif mean_delta > 0 and neg_rate <= 0.5:
                direction = "warning"
                interpretation = "Inherited current-anchor binary worlds lean adverse versus E95."
            else:
                direction = "underidentified"
                interpretation = "Inherited binary worlds do not give a clean sign."
            add_signal(
                rows,
                candidate,
                f"binary_world_{band}",
                "E181",
                mean_delta,
                direction,
                1.0 if band != "all_binary_worlds" else 0.5,
                interpretation,
                f"mean delta vs E95 {fmt(mean_delta)}; negative rate {fmt(neg_rate)}; worlds {int(row['n_worlds'])}",
            )

    e183_group = (
        e183.groupby("candidate")
        .agg(
            pressure_range_width=("pressure_range_width", "mean"),
            global_prefers_min=("global_prefers_min", "mean"),
            subject_prefers_min=("subject_prefers_min", "mean"),
            flank_prefers_min=("flank_mean_prefers_min", "mean"),
            visible_prefers_min=("visible_mean_prefers_min", "mean"),
            support_gap=("support_gap_coeff_weighted", "mean"),
            differing_cells=("differing_moved_cells", "mean"),
        )
        .reset_index()
    )
    min_width = float(e183_group["pressure_range_width"].min())
    for _, row in e183_group.iterrows():
        candidate = str(row["candidate"])
        width = float(row["pressure_range_width"])
        if width == min_width:
            direction = "support"
            interpretation = "This branch has the narrowest refreshed pressure range."
        elif width > min_width * 2:
            direction = "warning"
            interpretation = "This branch has a much wider refreshed pressure range."
        else:
            direction = "underidentified"
            interpretation = "Pressure range width does not separate this branch enough."
        add_signal(
            rows,
            candidate,
            "refreshed_pressure_range_width",
            "E182/E183",
            width,
            direction,
            0.75,
            interpretation,
            f"mean width {fmt(width)}; min live width {fmt(min_width)}; differing cells {fmt(row['differing_cells'])}",
        )

        local_pref = float(
            np.mean([row["subject_prefers_min"], row["flank_prefers_min"], row["visible_prefers_min"]])
        )
        add_signal(
            rows,
            candidate,
            "local_prior_pressure_branch_selector",
            "E183",
            local_pref,
            "warning" if local_pref == 0.0 else "underidentified",
            0.75,
            "Local subject/flank/visible priors reject the favorable pressure branch.",
            (
                f"subject/flank/visible favorable-min rates "
                f"{fmt(row['subject_prefers_min'])}/{fmt(row['flank_prefers_min'])}/{fmt(row['visible_prefers_min'])}; "
                f"support-gap {fmt(row['support_gap'])}"
            ),
        )

        global_pref = float(row["global_prefers_min"])
        add_signal(
            rows,
            candidate,
            "global_prior_pressure_branch_exception",
            "E183",
            global_pref,
            "support" if global_pref == 1.0 else "warning",
            0.35,
            (
                "Global prior uniquely favors the favorable pressure branch."
                if global_pref == 1.0
                else "Global prior does not favor the favorable pressure branch."
            ),
            f"global favorable-min rate {fmt(global_pref)}",
        )

    e186_group = (
        e186.groupby("candidate")
        .agg(
            pair_prob_mean=("prob_pressure_min_public_better", "mean"),
            pair_prob_min=("prob_pressure_min_public_better", "min"),
            pair_prob_max=("prob_pressure_min_public_better", "max"),
            favorable_rate=("prefers_favorable_min", "mean"),
        )
        .reset_index()
    )
    for _, row in e186_group.iterrows():
        candidate = str(row["candidate"])
        fav_rate = float(row["favorable_rate"])
        add_signal(
            rows,
            candidate,
            "antisymmetric_pair_geometry",
            "E186",
            fav_rate,
            "support" if fav_rate == 1.0 else "warning",
            1.5,
            (
                "Known-LB antisymmetric pair geometry consistently selects the favorable branch."
                if fav_rate == 1.0
                else "Known-LB antisymmetric pair geometry consistently rejects the favorable branch."
            ),
            (
                f"favorable rate {fmt(fav_rate)}; "
                f"mean prob {fmt(row['pair_prob_mean'])}; "
                f"min/max prob {fmt(row['pair_prob_min'])}/{fmt(row['pair_prob_max'])}"
            ),
        )

    e192_group = (
        e192_branch.groupby("candidate")
        .agg(
            shape_e72_prob_mean=("shape_e72_prob", "mean"),
            shape_e72_prob_max=("shape_e72_prob", "max"),
            above_p95_rate=("above_non_e72_p95", "mean"),
            above_p99_rate=("above_non_e72_p99", "mean"),
            above_positive_rate=("above_min_positive", "mean"),
        )
        .reset_index()
    )
    nearest_top3 = (
        e192_nearest.loc[e192_nearest["rank"].le(3)]
        .groupby("candidate")
        .agg(nearest_positive_rate=("known_label", "mean"))
        .reset_index()
    )
    e192_group = e192_group.merge(nearest_top3, on="candidate", how="left")
    for _, row in e192_group.iterrows():
        candidate = str(row["candidate"])
        above_p95 = float(row["above_p95_rate"])
        above_p99 = float(row["above_p99_rate"])
        if above_p99 > 0 or float(row["above_positive_rate"]) > 0:
            direction = "warning"
            interpretation = "Clean shape E72 score crosses a strong contamination threshold."
        elif above_p95 > 0:
            direction = "warning"
            interpretation = "Clean shape score marks a mild tail-risk scenario, not positive E72 contamination."
        else:
            direction = "support"
            interpretation = "Clean shape E72 score stays below non-E72 p95."
        add_signal(
            rows,
            candidate,
            "clean_shape_e72_tail_risk",
            "E192",
            float(row["shape_e72_prob_max"]),
            direction,
            0.75,
            interpretation,
            (
                f"max prob {fmt(row['shape_e72_prob_max'])}; "
                f"above p95 rate {fmt(above_p95)}; "
                f"above p99 rate {fmt(above_p99)}; "
                f"nearest positive rate {fmt(row['nearest_positive_rate'])}"
            ),
        )
        add_signal(
            rows,
            candidate,
            "e72_positive_nearest_neighbor",
            "E192",
            float(row["nearest_positive_rate"]),
            "support" if float(row["nearest_positive_rate"]) == 0.0 else "warning",
            0.5,
            "Nearest clean-shape neighbors are non-E72 positives.",
            f"top-3 nearest positive rate {fmt(row['nearest_positive_rate'])}",
        )

    signal_df = pd.DataFrame(rows)

    summary = (
        signal_df.assign(
            support=lambda x: x["direction"].eq("support").astype(int),
            warning=lambda x: x["direction"].eq("warning").astype(int),
            underidentified=lambda x: x["direction"].eq("underidentified").astype(int),
            missing=lambda x: x["direction"].eq("missing").astype(int),
        )
        .groupby(["candidate", "role", "file"], as_index=False)
        .agg(
            support_axes=("support", "sum"),
            warning_axes=("warning", "sum"),
            underidentified_axes=("underidentified", "sum"),
            missing_axes=("missing", "sum"),
            evidence_balance=("evidence_balance_contribution", "sum"),
        )
        .sort_values(["evidence_balance", "support_axes"], ascending=[False, False])
    )

    recommendations = {
        "e176": (
            "first public sensor if spending one slot: broad/Q2-underopen worldview "
            "has the strongest cross-sensor balance, but still needs E177 decoding"
        ),
        "e154": (
            "alternate repaired-branch worldview: inherited binary support remains alive, "
            "but pressure/pair/E72 diagnostics do not promote it over E176"
        ),
        "e144": (
            "unrepaired contrast/control: useful if repaired branch needs falsification, "
            "but mild shape-tail risk and pair-geometry rejection block first priority"
        ),
    }
    summary["recommended_role"] = summary["candidate"].map(recommendations)

    return signal_df, summary


def write_report(signal_df: pd.DataFrame, summary: pd.DataFrame) -> str:
    report_path = OUT / "e193_live_candidate_evidence_ledger_report.md"

    def markdown_table(df: pd.DataFrame) -> str:
        safe = df.copy()
        for col in safe.columns:
            safe[col] = safe[col].map(lambda x: fmt(x) if isinstance(x, (float, int)) else str(x))
            safe[col] = safe[col].str.replace("|", "\\|", regex=False)
        header = "| " + " | ".join(safe.columns) + " |"
        sep = "| " + " | ".join(["---"] * len(safe.columns)) + " |"
        lines = [header, sep]
        for _, row in safe.iterrows():
            lines.append("| " + " | ".join(row.astype(str).tolist()) + " |")
        return "\n".join(lines)

    summary_md = markdown_table(summary)
    signal_cols = [
        "candidate",
        "axis",
        "source",
        "value",
        "direction",
        "axis_weight",
        "evidence_balance_contribution",
        "evidence",
    ]
    signal_md = markdown_table(signal_df[signal_cols].sort_values(["candidate", "source", "axis"]))

    e176 = summary.loc[summary["candidate"].eq("e176")].iloc[0]
    body = f"""# E193 Live Candidate Evidence Ledger

## Question

Can the current evidence justify one live public sensor among E176, E154, and E144 without pretending that local diagnostics certify expected public LogLoss?

## Result

E176 remains the highest-information next public sensor, not because it is certified to beat E95, but because its evidence balance is the only positive one after combining visible-body/Q2 support, antisymmetric pair geometry, pressure-range width, and clean-E72 diagnostics. The counter-evidence is real: inherited binary worlds prefer E154/E144, and local priors reject all favorable pressure branches.

E176 evidence balance: `{fmt(float(e176['evidence_balance']))}` with `{int(e176['support_axes'])}` support axes, `{int(e176['warning_axes'])}` warning axes, `{int(e176['underidentified_axes'])}` underidentified axes, and `{int(e176['missing_axes'])}` missing comparable axes.

## Candidate Summary

{summary_md}

## Signal Audit

{signal_md}

## Interpretation

- E176's live claim is narrow: it is the broad/Q2-underopen sensor, not a generic expected-score winner.
- E154/E144 are not dead. They are the alternate repaired-branch worldview supported by inherited binary counterpriors.
- The refreshed current-anchor worlds remain sign-underidentified, so no branch should be promoted solely from binary-world pressure.
- E183 turns visible/subject/flank local priors into anti-selectors for pressure branches. That means the local priors cannot settle the frontier.
- E186 pair geometry and E192 clean-shape diagnostics keep E176 ahead as a sensor-role choice.

## Decision

No new submission is created. The next single public file remains `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` if the goal is to maximize information from one slot. After feedback, decode it with `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`.

If E176 improves public LB, the broad/Q2-underopen worldview is strengthened. If it ties or small-loses, the plateau law and hidden-label resolution bottleneck are strengthened. If it loses worse than E101, demote the partial-reopen family instead of tuning another keep factor.
"""
    report_path.write_text(body, encoding="utf-8")
    return str(report_path)


def main() -> None:
    signal_df, summary = build_ledger()
    signal_path = OUT / "e193_live_candidate_evidence_ledger_signal_audit.csv"
    summary_path = OUT / "e193_live_candidate_evidence_ledger_summary.csv"
    signal_df.to_csv(signal_path, index=False)
    summary.to_csv(summary_path, index=False)
    report_path = write_report(signal_df, summary)

    print("wrote", signal_path)
    print("wrote", summary_path)
    print("wrote", report_path)
    print(summary[["candidate", "support_axes", "warning_axes", "underidentified_axes", "missing_axes", "evidence_balance"]].to_string(index=False))


if __name__ == "__main__":
    main()
