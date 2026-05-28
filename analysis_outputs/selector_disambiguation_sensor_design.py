from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

KNOWN_IN = OUT / "public_anchor_bottleneck_known.csv"
PAIR_MODEL_IN = OUT / "public_pairwise_order_selector_models.csv"
OLD_MODEL_IN = OUT / "hidden_subset_selector_stress_model_scores.csv"
TOPOLOGY_IN = OUT / "selector_support_topology_audit.csv"

RELIABILITY_OUT = OUT / "selector_disambiguation_reliability.csv"
SENSORS_OUT = OUT / "selector_disambiguation_sensor_candidates.csv"
REPORT_OUT = OUT / "selector_disambiguation_sensor_design_report.md"

A2C8 = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05 = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"


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


def selector_reliability() -> tuple[pd.DataFrame, dict[str, float]]:
    known = pd.read_csv(KNOWN_IN)
    pair = pd.read_csv(PAIR_MODEL_IN)
    old = pd.read_csv(OLD_MODEL_IN)

    a2 = float(known.loc[known["file"].eq(A2C8), "public_lb"].iloc[0])
    raw = float(known.loc[known["file"].eq(RAW05), "public_lb"].iloc[0])
    actual_a2_minus_raw = a2 - raw

    pair_order = pair[pair["order_pass"].fillna(False).astype(bool)].copy()
    old_loo = old[old["stress"].eq("loo")].copy()
    old_l2o = old[old["stress"].eq("l2o")].copy()

    rows = [
        {
            "selector": "pairwise_public_order",
            "models": int(len(pair)),
            "pass_models": int(pair["order_pass"].fillna(False).sum()),
            "pass_rate": float(pair["order_pass"].fillna(False).mean()),
            "median_loo_mae": float(pair_order["loo_mae"].median()),
            "best_loo_mae": float(pair_order["loo_mae"].min()),
            "median_l2o_mae": float(pair_order["l2o_mae"].median()),
            "best_l2o_mae": float(pair_order["l2o_mae"].min()),
            "median_rank_accuracy": float(pair_order["known_rank_accuracy_vs_a2c8"].median()),
            "raw05_direction_correct_rate": float((pair["pred_a2c8_minus_raw05"] < 0).mean()),
            "raw05_margin_definition": "pred_a2c8_minus_raw05; correct if margin < 0",
            "median_raw05_direction_margin": float(pair_order["pred_a2c8_minus_raw05"].median()),
            "actual_a2_minus_raw": actual_a2_minus_raw,
            "read": "matches known a2c8<raw05 direction in most models; still not precise enough for tiny submit claims",
        },
        {
            "selector": "old_hidden_subset",
            "models": int(old_loo["model"].nunique()),
            "pass_models": int(old_loo.drop_duplicates("model")["selector_gate_pass"].fillna(False).sum()),
            "pass_rate": float(old_loo.drop_duplicates("model")["selector_gate_pass"].fillna(False).mean()),
            "median_loo_mae": float(old_loo["mae"].median()),
            "best_loo_mae": float(old_loo["mae"].min()),
            "median_l2o_mae": float(old_l2o["mae"].median()),
            "best_l2o_mae": float(old_l2o["mae"].min()),
            "median_rank_accuracy": float(old_loo["rank_accuracy"].median()),
            "raw05_direction_correct_rate": float(old_loo["a2c8_beats_raw05"].fillna(False).mean()),
            "raw05_margin_definition": "pred_raw05_minus_a2c8; correct if margin > 0",
            "median_raw05_direction_margin": float(old_loo["a2c8_raw05_pred_margin"].median()),
            "actual_a2_minus_raw": actual_a2_minus_raw,
            "read": "over-endorses raw05/stage2-like hidden subset geometry; useful veto but not a submit selector",
        },
    ]
    reliability = pd.DataFrame(rows)
    context = {
        "a2c8_public": a2,
        "raw05_public": raw,
        "actual_a2_minus_raw": actual_a2_minus_raw,
    }
    return reliability, context


def choose_sensors() -> pd.DataFrame:
    topo = pd.read_csv(TOPOLOGY_IN, low_memory=False)
    target = topo[~topo.get("pool_source", pd.Series("", index=topo.index)).astype(str).eq("known_anchor")].copy()
    target["pair_submit_gate"] = target.get("pair_submit_gate", False).fillna(False).astype(bool)
    target["pair_probe_gate"] = target.get("pair_probe_gate", False).fillna(False).astype(bool)
    target["pair_only"] = target.get("pair_only", False).fillna(False).astype(bool)
    target["old_only"] = target.get("old_only", False).fillna(False).astype(bool)
    target["q3s4_shape70"] = target.get("q3s4_shape70", False).fillna(False).astype(bool)

    pair_submit = target[target["pair_only"] & target["pair_submit_gate"]].copy()
    pair_probe = target[target["pair_probe_gate"]].copy()
    old_only = target[target["old_only"]].copy()

    records: list[dict[str, object]] = []

    def add(role: str, frame: pd.DataFrame, sort_cols: list[str], ascending: list[bool], rationale: str) -> None:
        if frame.empty:
            return
        row = frame.sort_values(sort_cols, ascending=ascending).iloc[0]
        records.append(
            {
                "role": role,
                "source_path": row.get("source_path", row.get("file", "")),
                "support_source": row.get("support_source", ""),
                "support_zone": row.get("support_zone", ""),
                "dominant_target": row.get("dominant_target", ""),
                "pair_delta_vs_a2c8_p90": row.get("pair_delta_vs_a2c8_p90", np.nan),
                "pair_beats_a2c8_rate": row.get("pair_beats_a2c8_rate", np.nan),
                "selector_p90_delta_vs_a2c8_public": row.get("selector_p90_delta_vs_a2c8_public", np.nan),
                "beats_a2c8_scenario_rate": row.get("beats_a2c8_scenario_rate", np.nan),
                "bad_axis_abs_load": row.get("bad_axis_abs_load", np.nan),
                "movement_scale": row.get("movement_scale", row.get("mean_abs_move_vs_a2c8", np.nan)),
                "q3s4_move_share": row.get("q3s4_move_share", np.nan),
                "pair_submit_gate": bool(row.get("pair_submit_gate", False)),
                "pair_probe_gate": bool(row.get("pair_probe_gate", False)),
                "rationale": rationale,
            }
        )

    add(
        "pair_selector_high_contrast_sensor",
        pair_submit,
        ["pair_delta_vs_a2c8_p90", "bad_axis_abs_load"],
        [True, True],
        "maximum contrast for S4/Q3 pairwise-public hypothesis; not an improvement claim because old support is weak",
    )
    add(
        "pair_selector_conservative_sensor",
        pair_submit,
        ["selector_p90_delta_vs_a2c8_public", "movement_scale", "pair_delta_vs_a2c8_p90"],
        [True, True, True],
        "least-bad old-selector p90 among pair-submit files; preferred if spending one diagnostic public slot",
    )
    block_probe = pair_probe[pair_probe["support_source"].eq("block_measurement_rescore")]
    add(
        "raw05_blockcount_probe_sensor",
        block_probe,
        ["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"],
        [True, True],
        "low-risk raw05-compatible blockcount probe; expected not to beat a2c8, useful only for raw05 tangent calibration",
    )
    add(
        "old_selector_redundant_sensor",
        old_only,
        ["selector_p90_delta_vs_a2c8_public", "pair_delta_vs_a2c8_p90"],
        [True, True],
        "old-only hypothesis is largely already tested by raw05 being public-worse than a2c8; do not prioritize",
    )

    out = pd.DataFrame(records)
    if out.empty:
        raise RuntimeError("No sensor candidates found.")
    out["expected_information"] = [
        "If public improves, pairwise S4/Q3 latent world is real and old selector is miscalibrated for this movement. If public worsens, pairwise-focused S4/Q3 is overfit."
        if role.startswith("pair_selector")
        else "If public unexpectedly improves, raw05/blockcount tangent has unmodeled public signal. If public worsens or is flat, current raw05-probe branch remains closed."
        if role == "raw05_blockcount_probe_sensor"
        else "Redundant with known raw05 LB; only useful if deliberately retesting old hidden-subset world."
        for role in out["role"]
    ]
    out["recommendation"] = [
        "diagnostic submit only; conservative sensor should go before high-contrast unless public slots are plentiful"
        if role == "pair_selector_high_contrast_sensor"
        else "best single diagnostic if user wants to resolve selector conflict"
        if role == "pair_selector_conservative_sensor"
        else "hold"
        for role in out["role"]
    ]
    return out


def write_report(reliability: pd.DataFrame, sensors: pd.DataFrame, context: dict[str, float]) -> None:
    lines = [
        "# Selector Disambiguation Sensor Design",
        "",
        "Question: after E21 showed an empty two-selector intersection, which public sensor would most efficiently decide whether the pairwise S4/Q3 world or old hidden-subset Q3/raw05-drift world is miscalibrated?",
        "",
        "## Known Anchor Reliability",
        "",
        f"- A2C8 public: `{context['a2c8_public']:.10f}`.",
        f"- Raw05 public: `{context['raw05_public']:.10f}`.",
        f"- Actual A2C8 minus Raw05: `{context['actual_a2_minus_raw']:.9f}`; A2C8 is better by `{abs(context['actual_a2_minus_raw']):.9f}`.",
        "",
        markdown_table(reliability),
        "",
        "## Sensor Candidates",
        "",
        markdown_table(sensors),
        "",
        "## Decision",
        "",
        "- The old hidden-subset selector already failed the key known direction: it endorses raw05-like geometry even though raw05 is public-worse than a2c8.",
        "- The pairwise selector is still too noisy for a confident improvement claim, but it is the more faithful known-anchor order sensor.",
        "- Therefore a public slot, if used, should test the pair-only S4/Q3 hypothesis rather than an old-only candidate.",
        "- This is diagnostic, not an expected path to 0.54. A good result would reopen S4/Q3 and retire or downweight the old selector for that movement; a bad result would close focused S4/Q3 amplification.",
        "",
        "## Files",
        "",
        f"- `{RELIABILITY_OUT.name}`",
        f"- `{SENSORS_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reliability, context = selector_reliability()
    sensors = choose_sensors()
    reliability.to_csv(RELIABILITY_OUT, index=False)
    sensors.to_csv(SENSORS_OUT, index=False)
    write_report(reliability, sensors, context)
    print(REPORT_OUT)
    print("[reliability]")
    print(reliability.to_string(index=False))
    print("[sensors]")
    print(sensors[["role", "source_path", "pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public", "recommendation"]].to_string(index=False))


if __name__ == "__main__":
    main()
