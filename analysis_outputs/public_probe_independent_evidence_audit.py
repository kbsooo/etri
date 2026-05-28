#!/usr/bin/env python3
"""Audit whether current public probes have certification-grade independent evidence.

E32-E34 make mixmin a strong public sensor under anchor-loss/binary-world
geometry. This script separates that anchor-derived support from evidence that
is independent enough to justify a normal improvement submission.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"


CANDIDATES: dict[str, dict[str, str]] = {
    "mixmin_0c916": {
        "file": "submission_mixmin_0c916bb4.csv",
        "lane": "high-risk binary/actual-anchor sensor",
    },
    "inverse7blend_1040": {
        "file": "submission_inverse7blend_1040423d.csv",
        "lane": "secondary binary/anchor-loss sensor",
    },
    "pair_sensor_1bb": {
        "file": "submission_label_flow_focused_1bbfb735.csv",
        "lane": "pair-only S4/Q3 selector-disambiguation sensor",
    },
    "pair_sensor_1bb_s0p65": {
        "file": "submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv",
        "lane": "lower-amplitude pair-only S4/Q3 sensor",
    },
    "pair_sensor_6b": {
        "file": "submission_label_flow_focused_6b9335b1.csv",
        "lane": "higher-amplitude pair-only S4/Q3 sensor",
    },
}


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def basename(value: Any) -> str:
    if pd.isna(value):
        return ""
    return Path(str(value)).name


def row_by_file(df: pd.DataFrame, filename: str) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=object)
    mask = pd.Series(False, index=df.index)
    for col in ("file", "source_path", "basename", "best_pair_file", "best_rank_file"):
        if col in df.columns:
            mask = mask | df[col].map(basename).eq(filename)
    if not mask.any():
        return pd.Series(dtype=object)
    return df.loc[mask].iloc[0]


def row_by_role_band(df: pd.DataFrame, role: str, band: str) -> pd.Series:
    if df.empty or "role" not in df.columns or "band" not in df.columns:
        return pd.Series(dtype=object)
    mask = df["role"].eq(role) & df["band"].eq(band)
    if not mask.any():
        return pd.Series(dtype=object)
    return df.loc[mask].iloc[0]


def row_by_role_scenario_band(
    df: pd.DataFrame, role: str, scenario: str, band: str
) -> pd.Series:
    if (
        df.empty
        or "role" not in df.columns
        or "scenario" not in df.columns
        or "band" not in df.columns
    ):
        return pd.Series(dtype=object)
    mask = df["role"].eq(role) & df["scenario"].eq(scenario) & df["band"].eq(band)
    if not mask.any():
        return pd.Series(dtype=object)
    return df.loc[mask].iloc[0]


def val(row: pd.Series, col: str, default: float | str | bool | None = np.nan) -> Any:
    if row.empty or col not in row.index:
        return default
    return row[col]


def finite(x: Any) -> bool:
    try:
        return np.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def truthy_negative(x: Any) -> bool:
    return finite(x) and float(x) < 0


def support_label(flag: bool) -> str:
    return "yes" if flag else "no"


def main() -> None:
    direction = read_csv("direction_probe_selector_reconciliation.csv")
    focused_pair = read_csv("label_flow_combo_focused_submit_pairwise_scored.csv")
    focused_review = read_csv("focused_label_flow_survival_review.csv")
    scale_curve = read_csv("label_flow_sensor_scale_curve.csv")
    anchor_bands = read_csv("public_lb_binary_anchor_loss_geometry_bands.csv")
    loo_summary = read_csv("public_lb_binary_anchor_loss_loo_stability_summary.csv")
    family_summary = read_csv("public_lb_binary_anchor_loss_family_null_summary.csv")
    combo_summary = read_csv("jepa_direction_mixture_minimax_optimizer_combo_summary.csv")
    actual_anchor = read_csv("jepa_direction_mixture_minimax_optimizer_actual_anchor.csv")

    records: list[dict[str, Any]] = []
    for role, spec in CANDIDATES.items():
        filename = spec["file"]
        direction_row = row_by_file(direction, filename)
        focused_pair_row = row_by_file(focused_pair, filename)
        focused_review_row = row_by_file(focused_review, filename)
        scale_row = row_by_file(scale_curve, filename)
        combo_row = row_by_file(combo_summary, filename)
        actual_row = row_by_file(actual_anchor, filename)

        old_selector_p90 = val(
            direction_row,
            "selector_p90_delta_vs_a2c8_public",
            val(
                focused_review_row,
                "selector_p90_delta_vs_a2c8_public",
                val(scale_row, "selector_p90_delta_vs_a2c8_public"),
            ),
        )
        old_selector_rate = val(
            direction_row,
            "beats_a2c8_scenario_rate",
            val(focused_review_row, "beats_a2c8_scenario_rate", val(scale_row, "beats_a2c8_scenario_rate")),
        )
        pair_p90 = val(
            direction_row,
            "pair_delta_vs_a2c8_p90",
            val(focused_pair_row, "pair_delta_vs_a2c8_p90", val(scale_row, "pair_delta_vs_a2c8_p90")),
        )
        pair_rate = val(
            direction_row,
            "pair_beats_a2c8_rate",
            val(focused_pair_row, "pair_beats_a2c8_rate", val(scale_row, "pair_beats_a2c8_rate")),
        )
        bad_axis = val(
            direction_row,
            "bad_axis_abs_load",
            val(focused_pair_row, "bad_axis_abs_load", val(scale_row, "bad_axis_abs_load")),
        )
        movement = val(
            direction_row,
            "mean_abs_move_vs_a2c8",
            val(focused_pair_row, "mean_abs_move_vs_a2c8", val(scale_row, "mean_abs_move_vs_a2c8")),
        )

        all_band = row_by_role_band(anchor_bands, role, "all")
        random_fit_band = row_by_role_band(anchor_bands, role, "low_anchor_energy_random_plus_fit")
        low_half_band = row_by_role_band(anchor_bands, role, "low_anchor_energy_half")
        low_quarter_band = row_by_role_band(anchor_bands, role, "low_anchor_energy_quarter")
        loo_half = row_by_role_band(loo_summary, role, "loo_low_anchor_energy_half")
        loo_quarter = row_by_role_band(loo_summary, role, "loo_low_anchor_energy_quarter")
        medium_only = row_by_role_scenario_band(
            family_summary, role, "only_medium_non_jepa", "low_half"
        )
        bad_jepa_only = row_by_role_scenario_band(family_summary, role, "only_bad_jepa", "low_half")

        honest_mean = val(direction_row, "honest_cv_delta_mean")
        honest_worst = val(direction_row, "honest_cv_delta_worst")
        local_direction_support = truthy_negative(honest_mean) and truthy_negative(honest_worst)
        local_dependency_support = (
            truthy_negative(val(focused_pair_row, "energy_delta_vs_base"))
            or (not scale_row.empty and truthy_negative(pair_p90))
        )
        local_independentish_support = local_direction_support or local_dependency_support

        pair_support = truthy_negative(pair_p90) and finite(pair_rate) and float(pair_rate) >= 0.5
        old_support = truthy_negative(old_selector_p90) and finite(old_selector_rate) and float(old_selector_rate) >= 0.5
        public_selector_support = pair_support and old_support
        selector_hard_veto = not public_selector_support and (
            (finite(pair_p90) and float(pair_p90) > 0)
            or (finite(old_selector_p90) and float(old_selector_p90) > 0)
        )

        binary_world_support = (
            finite(val(all_band, "better_rate"))
            and float(val(all_band, "better_rate")) >= 0.8
            and finite(val(random_fit_band, "better_rate"))
            and float(val(random_fit_band, "better_rate")) >= 0.9
        )
        anchor_loss_support = (
            finite(val(low_half_band, "better_rate"))
            and float(val(low_half_band, "better_rate")) >= 1.0
            and truthy_negative(val(low_half_band, "max_delta"))
        )
        loo_support = (
            finite(val(loo_half, "better_rate_min"))
            and float(val(loo_half, "better_rate_min")) >= 1.0
            and truthy_negative(val(loo_half, "max_delta_max"))
        )
        family_support = (
            finite(val(medium_only, "better_rate"))
            and float(val(medium_only, "better_rate")) >= 1.0
            and truthy_negative(val(medium_only, "max_delta"))
        )

        normal_submit_gate = (
            local_independentish_support
            and public_selector_support
            and not selector_hard_veto
            and movement is not np.nan
        )

        sensor_priority_score = 0
        sensor_priority_score += int(local_independentish_support)
        sensor_priority_score += 2 * int(binary_world_support)
        sensor_priority_score += 3 * int(anchor_loss_support)
        sensor_priority_score += 2 * int(loo_support)
        sensor_priority_score += int(family_support)
        sensor_priority_score -= 3 * int(selector_hard_veto)
        if finite(bad_axis) and float(bad_axis) > 0.15:
            sensor_priority_score -= 1

        records.append(
            {
                "role": role,
                "file": f"analysis_outputs/{filename}",
                "lane": spec["lane"],
                "local_independentish_support": local_independentish_support,
                "local_direction_support": local_direction_support,
                "local_dependency_energy_support": local_dependency_support,
                "honest_cv_delta_mean": honest_mean,
                "honest_cv_delta_worst": honest_worst,
                "public_selector_support": public_selector_support,
                "selector_hard_veto": selector_hard_veto,
                "pair_delta_vs_a2c8_p90": pair_p90,
                "pair_beats_a2c8_rate": pair_rate,
                "old_selector_p90_delta_vs_a2c8": old_selector_p90,
                "old_selector_beats_a2c8_rate": old_selector_rate,
                "actual_anchor_score_final": val(
                    direction_row,
                    "actual_anchor_score_final",
                    val(actual_row, "actual_anchor_score_final"),
                ),
                "combo_delta_vs_b01": val(
                    direction_row,
                    "combo_weighted_delta_vs_b01_ladder",
                    val(combo_row, "combo_weighted_delta_vs_b01_ladder"),
                ),
                "combo_win_vs_b01": val(
                    direction_row,
                    "combo_weighted_win_vs_b01_ladder",
                    val(combo_row, "combo_weighted_win_vs_b01_ladder"),
                ),
                "binary_world_support": binary_world_support,
                "binary_all_better_rate": val(all_band, "better_rate"),
                "binary_random_fit_better_rate": val(random_fit_band, "better_rate"),
                "anchor_loss_support": anchor_loss_support,
                "low_half_better_rate": val(low_half_band, "better_rate"),
                "low_half_max_delta": val(low_half_band, "max_delta"),
                "low_quarter_better_rate": val(low_quarter_band, "better_rate"),
                "loo_support": loo_support,
                "loo_low_half_better_rate_min": val(loo_half, "better_rate_min"),
                "loo_low_half_max_delta_max": val(loo_half, "max_delta_max"),
                "loo_low_quarter_better_rate_min": val(loo_quarter, "better_rate_min"),
                "family_support": family_support,
                "only_medium_low_half_better_rate": val(medium_only, "better_rate"),
                "only_medium_low_half_max_delta": val(medium_only, "max_delta"),
                "only_bad_jepa_low_half_better_rate": val(bad_jepa_only, "better_rate"),
                "only_bad_jepa_low_half_max_delta": val(bad_jepa_only, "max_delta"),
                "bad_axis_abs_load": bad_axis,
                "mean_abs_move_vs_a2c8": movement,
                "normal_submit_gate": normal_submit_gate,
                "sensor_priority_score": sensor_priority_score,
                "decision": (
                    "normal_submit"
                    if normal_submit_gate
                    else "public_sensor_only"
                    if role == "mixmin_0c916"
                    else "diagnostic_hold"
                ),
            }
        )

    summary = pd.DataFrame(records).sort_values(
        ["normal_submit_gate", "sensor_priority_score", "role"], ascending=[False, False, True]
    )
    summary_path = OUT / "public_probe_independent_evidence_audit_summary.csv"
    summary.to_csv(summary_path, index=False)

    source_inventory = pd.DataFrame(
        [
            {
                "evidence_source": "honest_cv_delta_mean/worst",
                "tier": "local_independent-ish",
                "supports": "mixmin if both mean and worst are negative",
                "limitation": "local direction metadata; not an observed public subset and not available for all pair sensors",
            },
            {
                "evidence_source": "label-flow dependency energy",
                "tier": "local/representation",
                "supports": "pair-only S4/Q3 sensors",
                "limitation": "failed old-selector and independent survival; can be representation-real but public-wrong",
            },
            {
                "evidence_source": "pairwise public-order selector",
                "tier": "known-public-derived",
                "supports": "pair-only S4/Q3 sensors",
                "limitation": "better than old selector on raw05/A2C8 direction but still a public-anchor scenario family",
            },
            {
                "evidence_source": "old hidden-subset selector",
                "tier": "known-public/selector-derived",
                "supports": "none of current probes",
                "limitation": "failed raw05/A2C8 direction, but remains a veto against pair-only overfit",
            },
            {
                "evidence_source": "actual-anchor score",
                "tier": "anchor-derived",
                "supports": "mixmin",
                "limitation": "built from known public anchors; cannot certify unobserved public improvement",
            },
            {
                "evidence_source": "combo stress",
                "tier": "quasi-public/inverse-scenario",
                "supports": "mixmin weakly versus b01",
                "limitation": "scenario family comes from public-anchor/inverse assumptions",
            },
            {
                "evidence_source": "binary frontier-box worlds",
                "tier": "known-public + train subject prior",
                "supports": "mixmin/inverse7 as high-risk sensors",
                "limitation": "candidate-max worlds still allow adverse signs",
            },
            {
                "evidence_source": "anchor-loss geometry",
                "tier": "anchor-derived",
                "supports": "mixmin strongly",
                "limitation": "uses known anchor loss decomposition; E34 says it is broad cancellation geometry, not target-axis semantics",
            },
            {
                "evidence_source": "anchor-loss LOO/family/null",
                "tier": "anchor-derived robustness",
                "supports": "mixmin over inverse7",
                "limitation": "robustness to anchor removal/family split is not a new independent public observation",
            },
            {
                "evidence_source": "OOF/block/measurement archive",
                "tier": "local/representation",
                "supports": "none of current submit gates",
                "limitation": "E19-E20 directly found no two-selector-supported candidate source",
            },
        ]
    )
    inventory_path = OUT / "public_probe_independent_evidence_source_inventory.csv"
    source_inventory.to_csv(inventory_path, index=False)

    mixmin = summary.loc[summary["role"].eq("mixmin_0c916")].iloc[0]
    one_line = (
        "E35 result: normal_submit_gate remains 0. "
        "Mixmin has the strongest sensor score, but its strongest evidence is still "
        "known-public/anchor-derived rather than certification-grade independent evidence."
    )
    report = [
        "# E35 Public Probe Independent Evidence Audit",
        "",
        "## Observe",
        "",
        "E32-E34 made `analysis_outputs/submission_mixmin_0c916bb4.csv` the leading high-risk probe under binary frontier-box and anchor-loss geometry. The unresolved question is whether that support is independent enough to turn the file into a normal improvement submission.",
        "",
        "## Wonder",
        "",
        "Is there any currently available non-public, non-anchor-derived validation source that supports mixmin strongly enough to override the pairwise/old selector veto?",
        "",
        "## Hypothesis",
        "",
        "H34: mixmin has enough out-of-anchor evidence for a normal submission. If true, at least one local/representation source should support it, the public selector veto should not be hard, and the anchor-loss evidence should be corroborative rather than primary.",
        "",
        "## Method",
        "",
        "The audit joined direction-probe metadata, focused label-flow pairwise scores, focused survival review, scale-curve scores, mixture combo stress, actual-anchor scores, binary anchor-loss bands, LOO stability, and family/null summaries. Each evidence source was tagged as local-independent-ish, local/representation, quasi-public, known-public-derived, anchor-derived, or anchor-derived robustness.",
        "",
        "## Result",
        "",
        f"- candidates audited: `{len(summary)}`.",
        f"- normal submit gates passing: `{int(summary['normal_submit_gate'].sum())}`.",
        f"- top sensor by diagnostic score: `{mixmin['role']}`.",
        f"- mixmin local direction support: `{support_label(bool(mixmin['local_direction_support']))}`; honest CV mean/worst `{mixmin['honest_cv_delta_mean']}` / `{mixmin['honest_cv_delta_worst']}`.",
        f"- mixmin selector hard veto: `{support_label(bool(mixmin['selector_hard_veto']))}`; pair p90 `{mixmin['pair_delta_vs_a2c8_p90']}`, old p90 `{mixmin['old_selector_p90_delta_vs_a2c8']}`.",
        f"- mixmin anchor-loss support: `{support_label(bool(mixmin['anchor_loss_support']))}`; low-half better_rate `{mixmin['low_half_better_rate']}`, low-half max_delta `{mixmin['low_half_max_delta']}`.",
        f"- mixmin LOO support: `{support_label(bool(mixmin['loo_support']))}`; LOO low-half min better_rate `{mixmin['loo_low_half_better_rate_min']}`, worst max_delta `{mixmin['loo_low_half_max_delta_max']}`.",
        "",
        "## Interpretation",
        "",
        "The audit rejects H34 as a normal-submit claim. Mixmin does have one local-independent-ish positive signal from honest CV and very strong anchor-derived support from E32-E34. But the strongest support is still built from known-public anchor geometry, while both selector families veto it on unobserved candidate deltas. Pair-only S4/Q3 sensors have local dependency-energy and pairwise support, but fail old/independent survival and are weak under binary/anchor-loss geometry.",
        "",
        "## Decision",
        "",
        one_line,
        "",
        "Submission implication: keep strict submit candidate count at 0. If a public diagnostic slot is deliberately spent, mixmin is now more information-rich than another S4/Q3 pair-only variant because it directly tests the binary/actual-anchor/anchor-loss worldview. That is a sensor decision, not a validated improvement claim.",
        "",
        "## Outputs",
        "",
        f"- `{summary_path.relative_to(ROOT)}`",
        f"- `{inventory_path.relative_to(ROOT)}`",
    ]
    report_path = OUT / "public_probe_independent_evidence_audit_report.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(one_line)
    print(f"wrote {summary_path.relative_to(ROOT)}")
    print(f"wrote {inventory_path.relative_to(ROOT)}")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
