#!/usr/bin/env python3
"""E108 E101-win amplitude follow-up materializer.

E107 says the next useful public branch is conditional:

- if E101 beats E95 by an edge/small amount, E104 active_all amplitude-up is
  the coherent follow-up;
- if E101 loses, the E99/E101 world model is strained and amplitude-up should
  not be used as a rescue.

This script turns that conditional branch into explicit files and a decision
table. It does not create a new immediate submission recommendation before the
E101 public result arrives.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e104_e101_amplitude_pareto_cliff as e104  # noqa: E402


E107_SUMMARY_IN = OUT / "e107_e101_feedback_decision_map_summary.csv"
E107_SCENARIOS_IN = OUT / "e107_e101_feedback_decision_map_scenarios.csv"

CANDIDATES_OUT = OUT / "e108_e101_win_amplitude_followup_candidates.csv"
CONDITIONED_OUT = OUT / "e108_e101_win_amplitude_followup_conditioned.csv"
DECISION_OUT = OUT / "e108_e101_win_amplitude_followup_decision.csv"
REPORT_OUT = OUT / "e108_e101_win_amplitude_followup_report.md"

SELECTED_SPECS = [
    {
        "role": "if_e101win_risk_amp050",
        "selector": "active_all",
        "graft_alpha": 0.500,
        "file_prefix": "submission_e108_if_e101win_amp050_",
        "risk_posture": "risk_tolerant_top_conditional",
        "submit_condition": "Only after E101 beats E95 by edge/small-win scale and higher amplitude risk is acceptable.",
    },
    {
        "role": "if_e101win_strict_amp038",
        "selector": "active_all",
        "graft_alpha": 0.380,
        "file_prefix": "submission_e108_if_e101win_strict_amp038_",
        "risk_posture": "strict_e101_pass_conservative",
        "submit_condition": "Only after E101 beats E95 and the next slot should minimize private-risk while testing amplitude-up.",
    },
]

OUTCOME_DECISIONS = [
    {
        "public_outcome": "E101 improves by roughly E95 edge or small-win scale",
        "e107_outcome_refs": "e95_edge_win,small_win_5e_minus6",
        "e101_delta_vs_e95_range": "[-0.000020, -0.000002]",
        "world_status": "coherent",
        "recommended_action": "Submit E108 risk amp050 if upside is prioritized; submit strict amp038 if conservative.",
        "why": "E107 matched many broad-plausible worlds and ranked active_all amp050 first versus both E95 and E101.",
    },
    {
        "public_outcome": "E101 is effectively tied with E95",
        "e107_outcome_refs": "tie",
        "e101_delta_vs_e95_range": "near 0",
        "world_status": "weak direction evidence",
        "recommended_action": "Do not submit amplitude-up automatically; treat E108 files as conditional probes only.",
        "why": "Amplitude rows still rank high in E107, but p95 becomes positive and the public sign evidence is weak.",
    },
    {
        "public_outcome": "E101 loses to E95",
        "e107_outcome_refs": "small_loss_1e_minus5,large_loss_4e_minus5",
        "e101_delta_vs_e95_range": "> 0",
        "world_status": "model tension",
        "recommended_action": "Do not rescue with E104/E106 masks; rebuild the public-world model around the failed rollback.",
        "why": "E107 needed nearest/tension worlds for loss cases, so the hidden-tail model would be falsified rather than refined.",
    },
    {
        "public_outcome": "E101 wins much more than expected",
        "e107_outcome_refs": "strong_win_5e_minus5",
        "e101_delta_vs_e95_range": "< -0.000020",
        "world_status": "possible model tension",
        "recommended_action": "Inspect first; amp050 is likely directionally right, but the win magnitude exceeds the current world support.",
        "why": "The strong-win hypothetical was top-ranked for amp050 but required nearest scenario selection.",
    },
]


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in frame.to_dict("records"):
        row: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                row.append("")
            elif isinstance(value, (float, np.floating)):
                row.append(format(float(value), floatfmt))
            else:
                row.append(str(value))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def e107_label(row: pd.Series) -> str:
    return f"e104_amp_{row['selector']}_a{float(row['graft_alpha']):.3f}_{str(row['tag'])[-8:]}"


def rebuild_e104_scan(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray]]:
    rows, preds, refs, tail_state = e104.build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    scan = e104.attach_flags(scan)
    return scan, preds


def pick_candidate(scan: pd.DataFrame, selector: str, alpha: float) -> pd.Series:
    hits = scan[
        scan["strategy"].eq("e95_q2s3_tail_graft")
        & scan["selector"].eq(selector)
        & np.isclose(scan["graft_alpha"].astype(float), alpha, atol=1.0e-12)
    ].copy()
    if len(hits) != 1:
        raise RuntimeError(f"expected one candidate for {selector=} {alpha=}, got {len(hits)}")
    return hits.iloc[0]


def materialize_submission(sample: pd.DataFrame, pred: np.ndarray, prefix: str) -> Path:
    tag = e83.stable_tag(pred, prefix)
    out = OUT / f"{tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def attach_scenario_refs(decision: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    scen = scenarios.set_index("outcome")
    for rec in decision.to_dict("records"):
        refs = [part.strip() for part in str(rec["e107_outcome_refs"]).split(",") if part.strip()]
        subset = scen.loc[refs].reset_index()
        rows.append(
            {
                **rec,
                "selection_modes": ",".join(sorted(subset["selection_mode"].astype(str).unique())),
                "scenario_counts": ",".join(f"{r.outcome}:{int(r.n_scenarios)}" for r in subset.itertuples()),
                "any_model_tension": bool(subset["model_tension"].astype(bool).any()),
            }
        )
    return pd.DataFrame(rows)


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scan, preds = rebuild_e104_scan(sample)
    e107_summary = pd.read_csv(E107_SUMMARY_IN)
    e107_scenarios = pd.read_csv(E107_SCENARIOS_IN)

    candidate_rows: list[dict[str, Any]] = []
    conditioned_parts: list[pd.DataFrame] = []

    for spec in SELECTED_SPECS:
        row = pick_candidate(scan, spec["selector"], spec["graft_alpha"])
        pred = preds[int(row["pred_index"])]
        output_path = materialize_submission(sample, pred, spec["file_prefix"])
        label = e107_label(row)
        conditioned = e107_summary[e107_summary["label"].eq(label)].copy()
        if conditioned.empty:
            raise RuntimeError(f"E107 conditioned rows missing for {label}")
        conditioned.insert(0, "role", spec["role"])
        conditioned["risk_posture"] = spec["risk_posture"]
        conditioned_parts.append(conditioned)

        edge = conditioned[conditioned["outcome"].eq("e95_edge_win")].iloc[0]
        small = conditioned[conditioned["outcome"].eq("small_win_5e_minus6")].iloc[0]
        tie = conditioned[conditioned["outcome"].eq("tie")].iloc[0]
        candidate_rows.append(
            {
                "role": spec["role"],
                "output_file": output_path.name,
                "label": label,
                "risk_posture": spec["risk_posture"],
                "submit_condition": spec["submit_condition"],
                "selector": row["selector"],
                "graft_alpha": float(row["graft_alpha"]),
                "e101_pass": bool(row["e101_pass"]),
                "dominates_e101_unconditional": bool(row["dominates_e101"]),
                "active_cells_vs_e95": int(row["active_cells_vs_e95"]),
                "move_cells": int(row["move_cells"]),
                "move_rows": int(row["move_rows"]),
                "move_edge_rate": float(row["move_edge_rate"]),
                "all_delta_vs_mixmin": float(row["all_delta_vs_mixmin"]),
                "e72_adverse_positive_exposure_all": float(row["e72_adverse_positive_exposure_all"]),
                "hidden_q2s3_mean_minus_base": float(row["hidden_q2s3_mean_minus_base"]),
                "world_support_minus_base": float(row["world_support_minus_base"]),
                "block_q2s3_beats_base_rate": float(row["block_q2s3_beats_base_rate"]),
                "block_q2s3_tail_safe_rate": float(row["block_q2s3_tail_safe_rate"]),
                "mean_vs_e95_broad_plausible": float(row["mean_vs_e95_broad_plausible"]),
                "p95_vs_e95_broad_plausible": float(row["p95_vs_e95_broad_plausible"]),
                "beat_e95_rate_broad_plausible": float(row["beat_e95_rate_broad_plausible"]),
                "mean_gain_vs_e101_unconditional": float(row["mean_gain_vs_e101"]),
                "p95_gain_vs_e101_unconditional": float(row["p95_gain_vs_e101"]),
                "beat_gap_vs_e101_unconditional": float(row["beat_gap_vs_e101"]),
                "edge_win_mean_vs_e101": float(edge["mean_vs_e101"]),
                "edge_win_p95_vs_e101": float(edge["p95_vs_e101"]),
                "edge_win_beat_e101_rate": float(edge["beat_e101_rate"]),
                "edge_win_rank_vs_e101": float(edge["rank_vs_e101"]),
                "small_win_mean_vs_e101": float(small["mean_vs_e101"]),
                "small_win_p95_vs_e101": float(small["p95_vs_e101"]),
                "small_win_beat_e101_rate": float(small["beat_e101_rate"]),
                "small_win_rank_vs_e101": float(small["rank_vs_e101"]),
                "tie_p95_vs_e101": float(tie["p95_vs_e101"]),
                "tie_beat_e101_rate": float(tie["beat_e101_rate"]),
            }
        )

    candidates = pd.DataFrame(candidate_rows)
    conditioned_all = pd.concat(conditioned_parts, ignore_index=True)
    decision = attach_scenario_refs(pd.DataFrame(OUTCOME_DECISIONS), e107_scenarios)
    return candidates, conditioned_all, decision


def write_report(candidates: pd.DataFrame, conditioned: pd.DataFrame, decision: pd.DataFrame) -> None:
    display_cols = [
        "role",
        "output_file",
        "risk_posture",
        "graft_alpha",
        "e101_pass",
        "active_cells_vs_e95",
        "edge_win_mean_vs_e101",
        "edge_win_p95_vs_e101",
        "edge_win_beat_e101_rate",
        "edge_win_rank_vs_e101",
        "small_win_mean_vs_e101",
        "small_win_p95_vs_e101",
        "small_win_beat_e101_rate",
        "small_win_rank_vs_e101",
        "tie_p95_vs_e101",
    ]
    cond_cols = [
        "role",
        "outcome",
        "mean_vs_e95",
        "p95_vs_e95",
        "beat_e95_rate",
        "mean_vs_e101",
        "p95_vs_e101",
        "beat_e101_rate",
        "rank_vs_e101",
    ]
    report = f"""# E108 E101-Win Amplitude Follow-Up

## Question

E107 says E104 amplitude-up should only become actionable if E101 wins. This
materializes the two useful post-feedback branches without changing the current
pre-feedback recommendation.

## Candidate Files

{md_table(candidates[display_cols], '.9f')}

## Outcome Decision Table

{md_table(decision, '.9f')}

## E107 Conditioned Behavior

{md_table(conditioned[cond_cols], '.9f')}

## Interpretation

- Current next public sensor is still E101, not E108.
- If E101 wins by edge/small-win scale, `if_e101win_risk_amp050` is the
  highest-upside branch: it ranks first in E107 for both edge and small-win
  outcomes, but it is not E101-pass unconditionally.
- If E101 wins but the next submission should preserve strict local stress,
  `if_e101win_strict_amp038` is the conservative branch: it is E101-pass, but
  ranks around the middle of the conditional E104 amplitude family.
- If E101 ties or loses, these files should not be used as a rescue. That would
  mean the E99/E101 public-world model needs revision before another submission.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    candidates, conditioned, decision = build_candidates(sample)

    candidates.to_csv(CANDIDATES_OUT, index=False)
    conditioned.to_csv(CONDITIONED_OUT, index=False)
    decision.to_csv(DECISION_OUT, index=False)
    write_report(candidates, conditioned, decision)

    risk = candidates[candidates["role"].eq("if_e101win_risk_amp050")].iloc[0]
    strict = candidates[candidates["role"].eq("if_e101win_strict_amp038")].iloc[0]
    assert not bool(risk["e101_pass"])
    assert bool(strict["e101_pass"])
    assert float(risk["edge_win_rank_vs_e101"]) == 1.0
    assert float(risk["small_win_rank_vs_e101"]) == 1.0
    assert float(strict["edge_win_beat_e101_rate"]) == 1.0
    assert len(candidates) == 2
    assert len(conditioned) == 12

    print(f"wrote {CANDIDATES_OUT}")
    print(f"wrote {CONDITIONED_OUT}")
    print(f"wrote {DECISION_OUT}")
    print(f"wrote {REPORT_OUT}")
    for file_name in candidates["output_file"]:
        print(f"materialized {OUT / file_name}")


if __name__ == "__main__":
    main()
