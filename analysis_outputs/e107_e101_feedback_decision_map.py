#!/usr/bin/env python3
"""E107 E101 feedback decision map.

E101 is the next public sensor, but the useful object is not only whether it
beats E95. The useful object is how that observed delta should update the
E95-conditioned hidden-tail worlds from E99.

This script does not use public labels and does not create a submission. It
conditions the existing E99 broad-plausible scenarios on hypothetical E101
public deltas, then asks which already-generated follow-up family would be
favored inside each conditional world:

- E104 amplitude variants: if E101 wins, should we spend more amplitude?
- E106 subject-prior gates: if the win is subject/S3 local, can a mask help?
- E89/E85/E90/E86 controls: if E101 fails, which older branch remains coherent?
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e96_public_miss_budget_tail_scenarios as e96mod  # noqa: E402
import e99_e95_conditioned_tail_transfer as e99mod  # noqa: E402
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e104_e101_amplitude_pareto_cliff as e104  # noqa: E402
import e106_e101_subject_prior_gate as e106  # noqa: E402


CANDIDATES_OUT = OUT / "e107_e101_feedback_decision_map_candidates.csv"
SCENARIOS_OUT = OUT / "e107_e101_feedback_decision_map_scenarios.csv"
SUMMARY_OUT = OUT / "e107_e101_feedback_decision_map_summary.csv"
REPORT_OUT = OUT / "e107_e101_feedback_decision_map_report.md"

MIN_SCENARIOS = 80
NEAREST_SCENARIOS = 240
EPS = 1.0e-12

HYPOTHETICALS = [
    ("strong_win_5e_minus5", -0.000050, 0.0000075),
    ("e95_edge_win", -0.0000153107, 0.0000040),
    ("small_win_5e_minus6", -0.000005, 0.0000030),
    ("tie", 0.0, 0.0000030),
    ("small_loss_1e_minus5", 0.000010, 0.0000050),
    ("large_loss_4e_minus5", 0.000040, 0.0000100),
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


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def build_e104_scan(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    rows, preds, refs, tail_state = e104.build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    scan = e104.attach_flags(scan)
    return scan, preds, refs, tail_state


def build_e106_scan(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray]]:
    rows, preds, refs, tail_state, active = e106.build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    scan = e106.mark_subject_graft_flags(scan)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    prior = e106.hard_label_prior_summary(scan, preds, refs, active)
    scan = e106.attach_e106_flags(scan, prior)
    return scan, preds


def add_candidate(
    *,
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    family: str,
    row: pd.Series,
    pred: np.ndarray,
) -> None:
    key = pred_key(pred)
    if key in seen:
        return
    cand_id = f"c{len(preds):04d}"
    seen[key] = len(preds)
    preds.append(pred)
    selector = "" if pd.isna(row.get("selector", "")) else str(row.get("selector", ""))
    source = "" if pd.isna(row.get("source", "")) else str(row.get("source", ""))
    tag = str(row.get("tag", "")) or e83.stable_tag(pred, f"e107_{family}_")
    if row.get("strategy", "") == "control":
        label = f"{family}_{source}"
    else:
        alpha = row.get("graft_alpha", np.nan)
        alpha_txt = "" if pd.isna(alpha) else f"_a{float(alpha):.3f}"
        label = f"{family}_{selector}{alpha_txt}_{tag[-8:]}"
    rows.append(
        {
            "candidate_id": cand_id,
            "label": label,
            "family": family,
            "source": source,
            "strategy": row.get("strategy", ""),
            "selector": selector,
            "target_scope": row.get("target_scope", ""),
            "graft_alpha": row.get("graft_alpha", np.nan),
            "selected_cells": row.get("selected_cells", np.nan),
            "selected_s3_cells": row.get("selected_s3_cells", np.nan),
            "all_delta_vs_mixmin": float(row["all_delta_vs_mixmin"]),
            "mean_vs_e95_broad_plausible": row.get("mean_vs_e95_broad_plausible", np.nan),
            "p95_vs_e95_broad_plausible": row.get("p95_vs_e95_broad_plausible", np.nan),
            "beat_e95_rate_broad_plausible": row.get("beat_e95_rate_broad_plausible", np.nan),
            "e101_pass": bool(row.get("e101_pass", False)),
            "dominates_e101": bool(row.get("dominates_e101", False)),
            "e106_replaces_e101": bool(row.get("e106_replaces_e101", False)),
            "prior_healthier_than_e101": bool(row.get("prior_healthier_than_e101", False)),
            "tag": tag,
        }
    )


def build_candidate_universe(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    scan104, preds104, refs, tail_state = build_e104_scan(sample)
    scan106, preds106 = build_e106_scan(sample)

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    controls = scan104[scan104["strategy"].eq("control")].copy()
    for _, row in controls.iterrows():
        add_candidate(rows=rows, preds=preds, seen=seen, family="control", row=row, pred=preds104[int(row["pred_index"])])

    e104_keep = scan104[
        scan104["strategy"].eq("e95_q2s3_tail_graft")
        & (
            scan104["e101_pass"].fillna(False).astype(bool)
            | scan104["beats_mean_p95_loses_beat"].fillna(False).astype(bool)
            | scan104["dominates_e101"].fillna(False).astype(bool)
        )
    ].copy()
    for _, row in e104_keep.iterrows():
        add_candidate(rows=rows, preds=preds, seen=seen, family="e104_amp", row=row, pred=preds104[int(row["pred_index"])])

    e106_keep = scan106[
        scan106["e106_interesting_but_not_replacement"].fillna(False).astype(bool)
        | scan106["e106_replaces_e101"].fillna(False).astype(bool)
    ].copy()
    for _, row in e106_keep.iterrows():
        add_candidate(rows=rows, preds=preds, seen=seen, family="e106_subj", row=row, pred=preds106[int(row["pred_index"])])

    cand = pd.DataFrame(rows)
    if not cand["label"].eq("control_e101").any():
        raise RuntimeError("control_e101 missing from E107 candidate universe")
    return cand, preds, refs, tail_state


def build_scenario_predictions(
    cand: pd.DataFrame,
    preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    e72_delta, _, wrong_is_zero, wrong_is_one = tail_state
    n_cells = refs["mixmin"].size
    e72_pos = np.maximum(
        e96mod.adverse_delta_for_e72_direction(refs["failed_e72"], refs["mixmin"], wrong_is_zero, wrong_is_one),
        0.0,
    )
    base_masks = e96mod.build_masks(refs, e72_pos, e72_delta)
    adverse_flat = {
        rec["candidate_id"]: e96mod.adverse_delta_for_e72_direction(
            preds[i], refs["mixmin"], wrong_is_zero, wrong_is_one
        ).reshape(-1)
        for i, rec in cand.reset_index(drop=True).iterrows()
    }
    budget_sum = e96mod.E72_PUBLIC_MISS * n_cells
    meta, long = e96mod.build_scenarios(e72_pos.reshape(-1), base_masks, adverse_flat, budget_sum, n_cells)
    wide = long.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    context_cols = [
        "scenario_id",
        "family",
        "mask_name",
        "order_name",
        "gamma",
        "alpha",
        "lambda",
        "is_broad_plausible",
        "is_tight_plausible",
        "is_near_unit_tail",
    ]
    context = pd.read_csv(e99mod.SCENARIO_OUT)[context_cols]
    detail = context.set_index("scenario_id").join(wide, how="inner").reset_index()
    cand_local = cand.set_index("candidate_id")["all_delta_vs_mixmin"].astype(float)
    for candidate_id, local_delta in cand_local.items():
        detail[f"pred_{candidate_id}"] = (
            detail["alpha"].astype(float) * float(local_delta)
            + detail["lambda"].astype(float) * detail[candidate_id].astype(float)
        )
        detail[f"vs_e95_{candidate_id}"] = detail[f"pred_{candidate_id}"] - e99mod.OBSERVED_PUBLIC_DELTA["e95"]
    return detail, meta


def conditional_summary(cand: pd.DataFrame, detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    broad = detail[detail["is_broad_plausible"].astype(bool)].copy()
    e101_id = cand.loc[cand["label"].eq("control_e101"), "candidate_id"].iloc[0]
    e95_id = cand.loc[cand["label"].eq("control_e95"), "candidate_id"].iloc[0]
    broad["e101_vs_e95"] = broad[f"vs_e95_{e101_id}"]

    scenario_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for outcome, target_delta, tolerance in HYPOTHETICALS:
        distance = np.abs(broad["e101_vs_e95"].to_numpy(dtype=np.float64) - target_delta)
        exact = distance <= tolerance
        if int(exact.sum()) >= MIN_SCENARIOS:
            subset = broad.loc[exact].copy()
            mode = "within_tolerance"
        else:
            take = min(NEAREST_SCENARIOS, len(broad))
            subset = broad.iloc[np.argsort(distance, kind="mergesort")[:take]].copy()
            mode = "nearest"
        e101_values = subset["e101_vs_e95"].astype(float)
        scenario_rows.append(
            {
                "outcome": outcome,
                "target_delta_vs_e95": target_delta,
                "tolerance": tolerance,
                "selection_mode": mode,
                "n_scenarios": len(subset),
                "e101_delta_mean": float(e101_values.mean()),
                "e101_delta_min": float(e101_values.min()),
                "e101_delta_p05": float(e101_values.quantile(0.05)),
                "e101_delta_p50": float(e101_values.quantile(0.50)),
                "e101_delta_p95": float(e101_values.quantile(0.95)),
                "e101_delta_max": float(e101_values.max()),
                "model_tension": mode == "nearest",
            }
        )
        for _, rec in cand.iterrows():
            cid = rec["candidate_id"]
            vs_e95 = subset[f"vs_e95_{cid}"].astype(float)
            vs_e101 = vs_e95 - subset[f"vs_e95_{e101_id}"].astype(float)
            summary_rows.append(
                {
                    "outcome": outcome,
                    "candidate_id": cid,
                    "label": rec["label"],
                    "family": rec["family"],
                    "selector": rec["selector"],
                    "graft_alpha": rec["graft_alpha"],
                    "selected_cells": rec["selected_cells"],
                    "e101_pass": rec["e101_pass"],
                    "prior_healthier_than_e101": rec["prior_healthier_than_e101"],
                    "n_scenarios": len(subset),
                    "mean_vs_e95": float(vs_e95.mean()),
                    "p50_vs_e95": float(vs_e95.quantile(0.50)),
                    "p95_vs_e95": float(vs_e95.quantile(0.95)),
                    "beat_e95_rate": float((vs_e95 < -EPS).mean()),
                    "mean_vs_e101": float(vs_e101.mean()),
                    "p50_vs_e101": float(vs_e101.quantile(0.50)),
                    "p95_vs_e101": float(vs_e101.quantile(0.95)),
                    "beat_e101_rate": float((vs_e101 < -EPS).mean()),
                    "is_e95": cid == e95_id,
                    "is_e101": cid == e101_id,
                }
            )
    summary = pd.DataFrame(summary_rows)
    summary["rank_vs_e95"] = summary.groupby("outcome")["mean_vs_e95"].rank(method="first")
    summary["rank_vs_e101"] = summary.groupby("outcome")["mean_vs_e101"].rank(method="first")
    return pd.DataFrame(scenario_rows), summary


def write_report(cand: pd.DataFrame, scenarios: pd.DataFrame, summary: pd.DataFrame) -> None:
    top_by_outcome = (
        summary.sort_values(["outcome", "rank_vs_e95", "p95_vs_e95"])
        .groupby("outcome", as_index=False)
        .head(8)
    )
    top_followup = (
        summary[~summary["is_e101"].astype(bool)]
        .sort_values(["outcome", "rank_vs_e101", "p95_vs_e101"])
        .groupby("outcome", as_index=False)
        .head(8)
    )
    strict_followup = (
        summary[
            ~summary["is_e101"].astype(bool)
            & summary["e101_pass"].fillna(False).astype(bool)
        ]
        .sort_values(["outcome", "rank_vs_e101", "p95_vs_e101"])
        .groupby("outcome", as_index=False)
        .head(5)
    )
    controls = summary[summary["family"].eq("control")].sort_values(["outcome", "mean_vs_e95"])
    tension = scenarios[scenarios["model_tension"].astype(bool)]
    report = f"""# E107 E101 Feedback Decision Map

## Question

Before E101 public feedback arrives, condition the E99 E95-tail worlds on
hypothetical E101-vs-E95 public deltas. If E101 wins, does the next branch point
toward E104 amplitude variants or E106 subject-prior masks? If E101 loses, is
that still explainable inside the E95-conditioned transfer model?

## Scenario Coverage

{md_table(scenarios, '.9f')}

## Top Candidates By Hypothetical Outcome

{md_table(top_by_outcome[['outcome','label','family','selector','graft_alpha','selected_cells','e101_pass','mean_vs_e95','p95_vs_e95','beat_e95_rate','mean_vs_e101','p95_vs_e101','beat_e101_rate','rank_vs_e95']], '.9f')}

## Top Follow-Ups Versus E101

{md_table(top_followup[['outcome','label','family','selector','graft_alpha','selected_cells','e101_pass','mean_vs_e101','p95_vs_e101','beat_e101_rate','mean_vs_e95','p95_vs_e95','beat_e95_rate','rank_vs_e101']], '.9f')}

## Strict E101-Pass Follow-Ups

{md_table(strict_followup[['outcome','label','family','selector','graft_alpha','selected_cells','mean_vs_e101','p95_vs_e101','beat_e101_rate','mean_vs_e95','p95_vs_e95','beat_e95_rate','rank_vs_e101']], '.9f')}

## Control Behavior

{md_table(controls[['outcome','label','mean_vs_e95','beat_e95_rate','mean_vs_e101','beat_e101_rate']], '.9f')}

## Interpretation

- If an E101 loss requires `nearest` scenario selection, the current E99/E101
  world model has low support for that observation. That would be a model
  falsification, not just a reason to submit a masked E101 variant.
- If E101 wins near the E95 edge, the next follow-up should be chosen by the
  conditional top-follow-up table, not by unconditional E104/E106 averages.
- E106 subject-prior gates are included as post-feedback contrasts, but they
  should not outrank E104 amplitude rows unless they beat E101 inside the
  matched E101 outcome subset.

## Tension Outcomes

{md_table(tension, '.9f')}
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    cand, preds, refs, tail_state = build_candidate_universe(sample)
    detail, _ = build_scenario_predictions(cand, preds, refs, tail_state)
    scenarios, summary = conditional_summary(cand, detail)

    cand.to_csv(CANDIDATES_OUT, index=False)
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(cand, scenarios, summary)

    print(f"wrote {CANDIDATES_OUT}")
    print(f"wrote {SCENARIOS_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")
    print("materialized none")


if __name__ == "__main__":
    main()
