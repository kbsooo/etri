from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

PAIR_IN = OUT / "public_pairwise_order_selector_candidates.csv"
FOCUS_IN = OUT / "focused_label_flow_survival_review.csv"
OLD_IN = OUT / "old_positive_anchor_pairwise_rescore.csv"
SUMMARY_OUT = OUT / "s4q3_anchor_gap_audit_summary.csv"
EXAMPLES_OUT = OUT / "s4q3_anchor_gap_audit_examples.csv"
REPORT_OUT = OUT / "s4q3_anchor_gap_audit_report.md"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def normalize(frame: pd.DataFrame, source: str) -> pd.DataFrame:
    out = frame.copy()
    out["audit_source"] = source
    if "source_path" not in out.columns:
        out["source_path"] = out["file"].astype(str)
    move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS if f"move_abs_a2c8_{target}" in out.columns]
    if "q3s4_move_share" not in out.columns:
        if "q3s4_share" in out.columns:
            out["q3s4_move_share"] = out["q3s4_share"]
        elif move_cols:
            out["q3s4_move_share"] = (
                out.get("move_abs_a2c8_Q3", 0.0) + out.get("move_abs_a2c8_S4", 0.0)
            ) / (out[move_cols].sum(axis=1) + 1e-12)
        else:
            out["q3s4_move_share"] = np.nan
    if "dominant_target" not in out.columns and move_cols:
        out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    if "old_majority" not in out.columns:
        if "scenario_majority_beats_a2c8" in out.columns:
            out["old_majority"] = out["scenario_majority_beats_a2c8"].fillna(False).astype(bool)
        elif "independent_majority_beats_a2c8" in out.columns:
            out["old_majority"] = out["independent_majority_beats_a2c8"].fillna(False).astype(bool)
        else:
            out["old_majority"] = False
    out["pair_p90_negative"] = out.get("pair_delta_vs_a2c8_p90", pd.Series(np.nan, index=out.index)) < 0.0
    out["pair_majority"] = out.get("pair_beats_a2c8_rate", pd.Series(0.0, index=out.index)) >= 0.50
    out["pair_probe_bool"] = out.get("pair_probe_gate", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    out["q3s4_share70"] = out["q3s4_move_share"] >= 0.70
    out["q3s4_share90"] = out["q3s4_move_share"] >= 0.90
    out["agreement_anchor_like"] = out["q3s4_share70"] & out["old_majority"] & out["pair_majority"]
    out["strict_anchor_like"] = out["q3s4_share70"] & out["old_majority"] & out["pair_p90_negative"]
    return out


def summary_for(frame: pd.DataFrame) -> dict[str, object]:
    return {
        "audit_source": str(frame["audit_source"].iloc[0]) if len(frame) else "",
        "n": int(len(frame)),
        "q3s4_share70": int(frame["q3s4_share70"].sum()),
        "q3s4_share90": int(frame["q3s4_share90"].sum()),
        "pair_p90_negative": int(frame["pair_p90_negative"].sum()),
        "pair_majority": int(frame["pair_majority"].sum()),
        "pair_probe": int(frame["pair_probe_bool"].sum()),
        "old_majority": int(frame["old_majority"].sum()),
        "q3s4_and_pair_p90_negative": int((frame["q3s4_share70"] & frame["pair_p90_negative"]).sum()),
        "q3s4_and_old_majority": int((frame["q3s4_share70"] & frame["old_majority"]).sum()),
        "q3s4_and_pair_majority_and_old_majority": int(frame["agreement_anchor_like"].sum()),
        "q3s4_and_pair_p90_negative_and_old_majority": int(frame["strict_anchor_like"].sum()),
    }


def top_examples(frame: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "audit_source",
        "source_path",
        "candidate_family",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "q3s4_move_share",
        "dominant_target",
        "move_abs_a2c8_Q3",
        "move_abs_a2c8_S4",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "pair_probe_bool",
        "old_majority",
    ]
    cols = [c for c in cols if c in frame.columns]
    slices = []
    for label, mask, sort_cols in [
        ("q3s4_shape", frame["q3s4_share70"], ["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]),
        ("old_majority", frame["old_majority"], ["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]),
        ("pair_positive", frame["pair_p90_negative"], ["selector_p90_delta_vs_a2c8_public", "pair_delta_vs_a2c8_p90"]),
    ]:
        sub = frame[mask].copy()
        if sub.empty:
            continue
        sub["example_slice"] = label
        slices.append(sub.sort_values(sort_cols).head(20)[["example_slice", *cols]])
    if not slices:
        return pd.DataFrame(columns=["example_slice", *cols])
    return pd.concat(slices, ignore_index=True, sort=False)


def main() -> None:
    frames = [
        normalize(pd.read_csv(PAIR_IN), "pairwise_scored_universe"),
        normalize(pd.read_csv(FOCUS_IN), "focused_s4q3_family"),
        normalize(pd.read_csv(OLD_IN), "old_positive_rescore"),
    ]
    summary = pd.DataFrame([summary_for(frame) for frame in frames])
    examples = pd.concat([top_examples(frame) for frame in frames], ignore_index=True, sort=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)

    lines = [
        "# S4/Q3 Anchor Gap Audit",
        "",
        "Question: does any existing candidate family provide an independent S4/Q3 positive anchor that both public-sensitive selectors agree on?",
        "",
        "## Summary",
        "",
        summary.to_csv(index=False).strip(),
        "",
        "## Examples",
        "",
        examples.head(80).round(9).to_csv(index=False).strip(),
        "",
        "## Interpretation",
        "",
        "- Existing pairwise-scored universe: has some Q3/S4-shaped candidates, but none also have old-majority support or pairwise p90 below zero.",
        "- Focused S4/Q3 family: every row is Q3/S4-shaped and pairwise-positive, but old-majority support is zero.",
        "- Old-positive rescore: contains old-majority candidates, but they are broad/Q3+S3-like moves; no Q3/S4 anchor-like candidates survive pairwise.",
        "- Therefore current artifacts do not contain an independent S4/Q3 positive anchor. The missing object is not another weight on the focused S4/Q3 gate; it is either a new validation signal for that direction or a larger safe movement that both selectors can price consistently.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT_OUT)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
