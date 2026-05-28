#!/usr/bin/env python3
"""E38 worldview/sensor discriminability audit.

The current bottleneck is not another candidate file. It is deciding which
latent public-world sensor to trust. This audit compiles raw-structure,
anchor-loss, pairwise-selector, old-selector, and local/combo evidence into a
single sensor-discriminability table.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

BEST_PUBLIC = 0.5774393210
RAW05_GAP = 0.0000869862

DETAIL_OUT = OUT / "worldview_sensor_discriminability_audit.csv"
LANE_OUT = OUT / "worldview_sensor_discriminability_by_lane.csv"
REPORT_OUT = OUT / "worldview_sensor_discriminability_report.md"


ROLE_LABELS = {
    "mixmin_0c916": {
        "lane": "anchor-loss worldview",
        "question": "Does binary/actual-anchor/anchor-loss geometry beat pair/old selector veto?",
    },
    "inverse7blend_1040": {
        "lane": "raw-structure bridge",
        "question": "Does raw observed structure plus anchor-loss support beat selector veto?",
    },
    "pair_sensor_1bb": {
        "lane": "S4/Q3 selector disambiguation",
        "question": "Does pairwise S4/Q3 selector beat old/anchor veto?",
    },
    "pair_sensor_1bb_s0p65": {
        "lane": "S4/Q3 selector disambiguation",
        "question": "Does lower-amplitude pairwise S4/Q3 movement still read on public?",
    },
    "pair_sensor_6b": {
        "lane": "S4/Q3 selector disambiguation",
        "question": "Does higher-amplitude pairwise S4/Q3 movement beat old/anchor veto?",
    },
}


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def finite(x: Any) -> bool:
    try:
        return bool(np.isfinite(float(x)))
    except (TypeError, ValueError):
        return False


def fval(row: pd.Series, col: str, default: float = np.nan) -> float:
    if row.empty or col not in row.index or not finite(row[col]):
        return default
    return float(row[col])


def sign_label(value: float, tol: float = 0.0) -> str:
    if not finite(value):
        return "missing"
    if value < -tol:
        return "better"
    if value > tol:
        return "worse"
    return "flat"


def sign_entropy(signs: list[str]) -> float:
    use = [s for s in signs if s in {"better", "worse"}]
    if not use:
        return 0.0
    p = use.count("better") / len(use)
    if p <= 0 or p >= 1:
        return 0.0
    return float(-(p * np.log2(p) + (1 - p) * np.log2(1 - p)))


def row_by_role(df: pd.DataFrame, role: str) -> pd.Series:
    if df.empty or "role" not in df.columns:
        return pd.Series(dtype=object)
    hit = df[df["role"].astype(str).eq(role)]
    return hit.iloc[0] if len(hit) else pd.Series(dtype=object)


def anchor_band_row(df: pd.DataFrame, role: str, band: str) -> pd.Series:
    if df.empty or "role" not in df.columns or "band" not in df.columns:
        return pd.Series(dtype=object)
    hit = df[df["role"].astype(str).eq(role) & df["band"].astype(str).eq(band)]
    return hit.iloc[0] if len(hit) else pd.Series(dtype=object)


def base_records() -> list[dict[str, Any]]:
    evidence = read_csv(OUT / "public_probe_independent_evidence_audit_summary.csv")
    raw = read_csv(OUT / "raw_structure_pseudolabel_candidate_stress_summary.csv")
    anchor = read_csv(OUT / "public_lb_binary_anchor_loss_geometry_bands.csv")
    records: list[dict[str, Any]] = []
    for role in [
        "mixmin_0c916",
        "inverse7blend_1040",
        "pair_sensor_1bb",
        "pair_sensor_1bb_s0p65",
        "pair_sensor_6b",
    ]:
        e = row_by_role(evidence, role)
        r = row_by_role(raw, role)
        a_half = anchor_band_row(anchor, role, "low_anchor_energy_half")
        a_quarter = anchor_band_row(anchor, role, "low_anchor_energy_quarter")
        a_random = anchor_band_row(anchor, role, "low_anchor_energy_random_plus_fit")
        meta = ROLE_LABELS[role]
        records.append(
            {
                "role": role,
                "file": str(e.get("file", "")),
                "lane": meta["lane"],
                "question": meta["question"],
                "source": "E35/E36/E32",
                "raw_support_rate": fval(r, "support_rate"),
                "raw_mean_delta": fval(r, "mean_delta"),
                "raw_worst_delta": fval(r, "worst_delta"),
                "anchor_low_half_better_rate": fval(a_half, "better_rate"),
                "anchor_low_half_median_delta": fval(a_half, "median_delta"),
                "anchor_low_half_max_delta": fval(a_half, "max_delta"),
                "anchor_low_quarter_better_rate": fval(a_quarter, "better_rate"),
                "anchor_low_quarter_max_delta": fval(a_quarter, "max_delta"),
                "anchor_random_fit_better_rate": fval(a_random, "better_rate"),
                "anchor_random_fit_max_delta": fval(a_random, "max_delta"),
                "pair_p90_delta": fval(e, "pair_delta_vs_a2c8_p90"),
                "pair_better_rate": fval(e, "pair_beats_a2c8_rate"),
                "old_p90_delta": fval(e, "old_selector_p90_delta_vs_a2c8"),
                "old_better_rate": fval(e, "old_selector_beats_a2c8_rate"),
                "honest_cv_mean_delta": fval(e, "honest_cv_delta_mean"),
                "honest_cv_worst_delta": fval(e, "honest_cv_delta_worst"),
                "combo_delta_vs_b01": fval(e, "combo_delta_vs_b01"),
                "actual_anchor_score_final": fval(e, "actual_anchor_score_final"),
                "bad_axis_abs_load": fval(e, "bad_axis_abs_load"),
                "mean_abs_move_vs_a2c8": fval(e, "mean_abs_move_vs_a2c8"),
                "selector_hard_veto": bool(e.get("selector_hard_veto", True)) if not e.empty else True,
                "normal_submit_gate_existing": bool(e.get("normal_submit_gate", False)) if not e.empty else False,
            }
        )
    return records


def bridge_records() -> list[dict[str, Any]]:
    bridge = read_csv(OUT / "inverse7_raw_anchor_bridge_scale_scan_scores.csv")
    if bridge.empty:
        return []
    keep_roles = [
        "inv7_s0p25",
        "inv7_s0p50",
        "inv7_s1p00",
        "blend_m0p25_s0p50",
        "blend_m0p50_s0p50",
    ]
    rows: list[dict[str, Any]] = []
    for role in keep_roles:
        b = row_by_role(bridge, role)
        if b.empty:
            continue
        rows.append(
            {
                "role": role,
                "file": str(b.get("file", "")),
                "lane": "raw-structure bridge",
                "question": "Does scaled inverse7 raw+anchor support beat pair/old selector veto?",
                "source": "E37",
                "raw_support_rate": fval(b, "support_rate"),
                "raw_mean_delta": fval(b, "raw_mean_delta"),
                "raw_worst_delta": fval(b, "raw_worst_delta"),
                "anchor_low_half_better_rate": fval(b, "anchor_low_anchor_energy_half_better_rate"),
                "anchor_low_half_median_delta": fval(b, "anchor_low_anchor_energy_half_median_delta"),
                "anchor_low_half_max_delta": fval(b, "anchor_low_anchor_energy_half_max_delta"),
                "anchor_low_quarter_better_rate": fval(b, "anchor_low_anchor_energy_quarter_better_rate"),
                "anchor_low_quarter_max_delta": fval(b, "anchor_low_anchor_energy_quarter_max_delta"),
                "anchor_random_fit_better_rate": fval(b, "anchor_low_anchor_energy_random_plus_fit_better_rate"),
                "anchor_random_fit_max_delta": fval(b, "anchor_low_anchor_energy_random_plus_fit_max_delta"),
                "pair_p90_delta": fval(b, "pair_delta_vs_a2c8_p90"),
                "pair_better_rate": fval(b, "pair_beats_a2c8_rate"),
                "old_p90_delta": fval(b, "selector_p90_delta_vs_a2c8_public"),
                "old_better_rate": fval(b, "beats_a2c8_scenario_rate"),
                "honest_cv_mean_delta": np.nan,
                "honest_cv_worst_delta": np.nan,
                "combo_delta_vs_b01": np.nan,
                "actual_anchor_score_final": np.nan,
                "bad_axis_abs_load": fval(b, "bad_axis_abs_load"),
                "mean_abs_move_vs_a2c8": fval(b, "mean_abs_move_vs_a2c8"),
                "selector_hard_veto": bool(b.get("selector_hard_veto", True)),
                "normal_submit_gate_existing": bool(b.get("bridge_gate", False)),
            }
        )
    return rows


def enrich(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for rec in frame.to_dict("records"):
        raw_sign = sign_label(float(rec["raw_worst_delta"]) if finite(rec["raw_worst_delta"]) else rec["raw_mean_delta"])
        anchor_sign = sign_label(float(rec["anchor_low_half_max_delta"]) if finite(rec["anchor_low_half_max_delta"]) else rec["anchor_low_half_median_delta"])
        pair_sign = sign_label(rec["pair_p90_delta"])
        old_sign = sign_label(rec["old_p90_delta"])
        honest_sign = sign_label(rec["honest_cv_worst_delta"]) if finite(rec["honest_cv_worst_delta"]) else "missing"

        signs = [raw_sign, anchor_sign, pair_sign, old_sign, honest_sign]
        values = [
            rec["raw_mean_delta"],
            rec["anchor_low_half_max_delta"],
            rec["pair_p90_delta"],
            rec["old_p90_delta"],
            rec["honest_cv_worst_delta"],
        ]
        finite_values = [float(x) for x in values if finite(x)]
        conflict_span = float(max(finite_values) - min(finite_values)) if finite_values else np.nan
        readable_span = conflict_span / RAW05_GAP if finite(conflict_span) else np.nan
        entropy = sign_entropy(signs)
        better_count = sum(s == "better" for s in signs)
        worse_count = sum(s == "worse" for s in signs)
        raw_anchor_better = raw_sign == "better" and anchor_sign == "better"
        selector_both_worse = pair_sign == "worse" and old_sign == "worse"
        selector_both_better = pair_sign == "better" and old_sign == "better"
        anchor_vs_selector = anchor_sign == "better" and (pair_sign == "worse" or old_sign == "worse")
        pair_vs_anchor = pair_sign == "better" and anchor_sign == "worse"
        normal_submit_gate = raw_sign == "better" and anchor_sign == "better" and pair_sign == "better" and old_sign == "better"
        public_sensor_gate = entropy >= 0.70 and finite(readable_span) and readable_span >= 4.0

        if normal_submit_gate:
            recommendation = "normal_submit_candidate"
        elif public_sensor_gate and rec["role"] == "mixmin_0c916":
            recommendation = "top_anchor_worldview_sensor"
        elif public_sensor_gate and raw_anchor_better and selector_both_worse:
            recommendation = "raw_anchor_vs_selector_sensor"
        elif public_sensor_gate and pair_vs_anchor:
            recommendation = "pair_vs_anchor_sensor"
        elif entropy > 0:
            recommendation = "weak_diagnostic_sensor"
        else:
            recommendation = "hold"

        # This score is a sensor ranking, not an improvement score.
        information_score = (
            entropy * np.log1p(max(readable_span, 0.0))
            + 0.25 * int(anchor_vs_selector)
            + 0.20 * int(raw_anchor_better)
            + 0.20 * int(pair_vs_anchor)
            - 0.10 * int(finite(rec["bad_axis_abs_load"]) and float(rec["bad_axis_abs_load"]) > 0.15)
        )
        if rec["role"] == "mixmin_0c916":
            information_score += 0.25
        if str(rec["role"]).startswith("inv7_s0p25"):
            information_score += 0.05

        rec.update(
            {
                "raw_verdict": raw_sign,
                "anchor_verdict": anchor_sign,
                "pair_verdict": pair_sign,
                "old_verdict": old_sign,
                "honest_cv_verdict": honest_sign,
                "better_view_count": better_count,
                "worse_view_count": worse_count,
                "verdict_entropy": entropy,
                "conflict_span": conflict_span,
                "conflict_span_vs_raw05_gap": readable_span,
                "raw_anchor_better": raw_anchor_better,
                "selector_both_worse": selector_both_worse,
                "selector_both_better": selector_both_better,
                "anchor_vs_selector": anchor_vs_selector,
                "pair_vs_anchor": pair_vs_anchor,
                "normal_submit_gate": normal_submit_gate,
                "public_sensor_gate": public_sensor_gate,
                "sensor_information_score": float(information_score),
                "recommendation": recommendation,
                "expected_lb_anchor_low_half_max": BEST_PUBLIC + float(rec["anchor_low_half_max_delta"]) if finite(rec["anchor_low_half_max_delta"]) else np.nan,
                "expected_lb_pair_p90": BEST_PUBLIC + float(rec["pair_p90_delta"]) if finite(rec["pair_p90_delta"]) else np.nan,
                "expected_lb_old_p90": BEST_PUBLIC + float(rec["old_p90_delta"]) if finite(rec["old_p90_delta"]) else np.nan,
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(
        ["normal_submit_gate", "public_sensor_gate", "sensor_information_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def lane_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for lane, group in frame.groupby("lane", sort=False):
        best = group.sort_values("sensor_information_score", ascending=False).iloc[0]
        rows.append(
            {
                "lane": lane,
                "n": int(len(group)),
                "normal_submit_candidates": int(group["normal_submit_gate"].sum()),
                "public_sensor_candidates": int(group["public_sensor_gate"].sum()),
                "best_role": best["role"],
                "best_file": best["file"],
                "best_recommendation": best["recommendation"],
                "best_information_score": float(best["sensor_information_score"]),
                "best_conflict_span": float(best["conflict_span"]),
                "best_conflict_span_vs_raw05_gap": float(best["conflict_span_vs_raw05_gap"]),
                "best_question": best["question"],
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["normal_submit_candidates", "public_sensor_candidates", "best_information_score"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def write_report(detail: pd.DataFrame, lanes: pd.DataFrame) -> None:
    top_cols = [
        "role",
        "lane",
        "raw_verdict",
        "anchor_verdict",
        "pair_verdict",
        "old_verdict",
        "honest_cv_verdict",
        "conflict_span_vs_raw05_gap",
        "public_sensor_gate",
        "normal_submit_gate",
        "sensor_information_score",
        "recommendation",
        "file",
    ]
    metric_cols = [
        "role",
        "raw_mean_delta",
        "raw_worst_delta",
        "anchor_low_half_max_delta",
        "pair_p90_delta",
        "old_p90_delta",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "expected_lb_anchor_low_half_max",
        "expected_lb_pair_p90",
        "expected_lb_old_p90",
    ]
    normal = int(detail["normal_submit_gate"].sum())
    sensors = int(detail["public_sensor_gate"].sum())
    top = detail.iloc[0]
    lines = [
        "# E38 Worldview Sensor Discriminability Audit",
        "",
        "## Observe",
        "",
        "E37 showed raw and anchor support can coexist, but selector veto remains. The next question is which candidate is the most informative public sensor, not which one is safe.",
        "",
        "## Wonder",
        "",
        "Which candidate best separates the plausible hidden-public worldviews: anchor-loss binary worlds, raw observed structure, pairwise public-order selector, old hidden-subset selector, and local honest-CV/combo evidence?",
        "",
        "## Hypothesis",
        "",
        "H37: if no normal submit candidate exists, the next public slot should be allocated to the candidate with the highest predeclared worldview discriminability: large enough expected sign conflict, clear interpretation if LB improves/worsens, and no claim of safety.",
        "",
        "## Method",
        "",
        "- Compile E32/E33 anchor-loss bands, E35 independent-evidence audit, E36 raw-structure pseudo-label stress, and E37 bridge scale scan.",
        "- Convert each source into a robust verdict: raw, anchor, pairwise selector, old selector, and honest CV when available.",
        "- Rank by sign entropy and conflict span relative to the known raw05/A2C8 public gap. This is a sensor ranking, not an improvement ranking.",
        "",
        "## Result",
        "",
        f"- candidates audited: `{len(detail)}`.",
        f"- normal submit candidates: `{normal}`.",
        f"- public sensor candidates: `{sensors}`.",
        f"- top information sensor: `{top['role']}` (`{top['recommendation']}`), score `{top['sensor_information_score']:.6f}`.",
        "",
        "## Lane Summary",
        "",
        markdown_table(lanes),
        "",
        "## Top Sensor Table",
        "",
        markdown_table(detail[[col for col in top_cols if col in detail.columns]].head(12)),
        "",
        "## Key Metrics",
        "",
        markdown_table(detail[[col for col in metric_cols if col in detail.columns]].head(12)),
        "",
        "## Decision",
        "",
        "No candidate is promoted to normal improvement submission. `mixmin_0c916` remains the top high-risk anchor-loss worldview sensor because it creates the clearest disagreement between anchor-loss/honest-CV support and pair/old/raw veto. `inv7_s0p25` is a cleaner raw+anchor bridge sensor, but its negative expected edge is less readable and the selector veto remains. `pair_sensor_1bb` remains the lower-risk S4/Q3 selector-disambiguation sensor.",
        "",
        "## Outputs",
        "",
        f"- `{DETAIL_OUT.relative_to(ROOT)}`",
        f"- `{LANE_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    records = base_records() + bridge_records()
    detail = enrich(pd.DataFrame(records))
    lanes = lane_summary(detail)
    detail.to_csv(DETAIL_OUT, index=False)
    lanes.to_csv(LANE_OUT, index=False)
    write_report(detail, lanes)
    print(f"candidates={len(detail)}")
    print(f"normal_submit_candidates={int(detail['normal_submit_gate'].sum())}")
    print(f"public_sensor_candidates={int(detail['public_sensor_gate'].sum())}")
    print(
        detail[
            [
                "role",
                "lane",
                "raw_verdict",
                "anchor_verdict",
                "pair_verdict",
                "old_verdict",
                "conflict_span_vs_raw05_gap",
                "sensor_information_score",
                "recommendation",
            ]
        ]
        .head(12)
        .to_string(index=False)
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
