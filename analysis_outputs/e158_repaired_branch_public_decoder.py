#!/usr/bin/env python3
"""E158: pre-register public-feedback interpretation for the repaired branch.

E154/E155/E157/E156/E144 are not independent model families. They are a
collinear sensor stack around the E95 frontier. This script does not create a
submission. It asks whether the current candidate stack is distinguishable at
public-LB scale and records what each score band should kill or keep.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405

E101_DELTA = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA = MIXMIN_PUBLIC - E95_PUBLIC

PUBLIC_READABLE_DELTA = 2.0e-6
PUBLIC_CLEAN_DELTA = 7.0e-6
PUBLIC_BREAKTHROUGH_DELTA = 2.0e-5

CANDIDATES: dict[str, dict[str, str]] = {
    "e95": {
        "file": "submission_e95_hardtail_541e3973.csv",
        "role": "current public frontier",
        "source": "public_anchor",
    },
    "e154": {
        "file": "submission_e154_s3repair_9f2e2e73.csv",
        "role": "full repaired S3 active-boundary body",
        "source": "e154_s3_active_boundary_repair_scan.csv",
    },
    "e155": {
        "file": "submission_e155_bodytemp_d27e7965.csv",
        "role": "25% repaired body amplitude control",
        "source": "e155_e154_branch_body_ablation_scan.csv",
    },
    "e157": {
        "file": "submission_e157_lowbodypareto_bd67930d.csv",
        "role": "Q1+Q3+S2+S4 low-body Pareto control",
        "source": "e157_e156_axis_response_pareto.csv",
    },
    "e156": {
        "file": "submission_e156_targetaxis_757546d2.csv",
        "role": "minimum-body Q1/S2/S4 decomposition control",
        "source": "e156_e154_target_axis_lattice_scan.csv",
    },
    "e144": {
        "file": "submission_e144_activeboundary_d7b4b331.csv",
        "role": "unrepaired residual-branch contrast",
        "source": "e144_e143_active_boundary_refine_frontier.csv",
    },
    "e101": {
        "file": "submission_e101_q2s3tail_177569bc.csv",
        "role": "resolved negative Q2/S3 rollback sensor",
        "source": "public_anchor",
    },
    "mixmin": {
        "file": "submission_mixmin_0c916bb4.csv",
        "role": "previous public frontier",
        "source": "public_anchor",
    },
}

PUBLIC_ANCHORS = {
    "e95": E95_PUBLIC,
    "e101": E101_PUBLIC,
    "mixmin": MIXMIN_PUBLIC,
}

METRIC_COLUMNS = [
    "all_minus_base",
    "post101_p95_vs_e95_e101_sensor",
    "e72_plausible_gap_vs_e95",
    "transfer_shrinkage_risk_index",
    "body_norm_ratio",
    "changed_cells_vs_e95",
    "changed_rows_vs_e95",
    "gate_active_q2s3_not_more_than_e101",
    "gate_e72_not_more_than_e95",
    "all_four",
    "all_four_health",
    "e154_submit",
    "e155_submit",
    "e156_minbody_submit",
]


def logit(x: np.ndarray) -> np.ndarray:
    x = np.clip(x.astype(np.float64), 1e-6, 1.0 - 1e-6)
    return np.log(x / (1.0 - x))


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                if np.isposinf(value):
                    vals.append("inf")
                elif np.isneginf(value):
                    vals.append("-inf")
                else:
                    vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load_submission(tag: str) -> pd.DataFrame:
    path = OUT / CANDIDATES[tag]["file"]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def load_aligned_logits() -> dict[str, np.ndarray]:
    base = load_submission("e95")
    key_cols = ["subject_id", "sleep_date", "lifelog_date"]
    out: dict[str, np.ndarray] = {}
    for tag in CANDIDATES:
        sub = load_submission(tag)
        merged = base[key_cols].merge(sub, on=key_cols, how="left", validate="one_to_one")
        if merged[TARGETS].isna().any().any():
            raise RuntimeError(f"Submission alignment failed for {tag}")
        out[tag] = logit(merged[TARGETS].to_numpy(dtype=np.float64))
    return out


def truthy(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).astype(float).ne(0)
    return series.fillna("").astype(str).str.lower().isin(["true", "1", "yes"])


def select_metric_row(tag: str) -> dict[str, Any]:
    if tag in PUBLIC_ANCHORS:
        return {}

    source = OUT / CANDIDATES[tag]["source"]
    df = pd.read_csv(source, low_memory=False)

    if tag == "e154":
        mask = truthy(df.get("materialized_submission", pd.Series(False, index=df.index)))
        row = df[mask].sort_values("all_minus_base").iloc[0]
    elif tag == "e155":
        mask = truthy(df.get("materialized_submission", pd.Series(False, index=df.index)))
        row = df[mask].sort_values("all_minus_base").iloc[0]
    elif tag == "e157":
        row = df.sort_values(
            ["all_minus_base", "post101_p95_vs_e95_e101_sensor", "e72_plausible_gap_vs_e95"],
            ascending=[True, True, True],
        ).iloc[0]
    elif tag == "e156":
        mask = truthy(df.get("materialized_submission", pd.Series(False, index=df.index)))
        if int(mask.sum()) == 0:
            mask = truthy(df.get("e156_minbody_submit", pd.Series(False, index=df.index)))
        row = df[mask].sort_values(["body_norm_ratio", "all_minus_base"]).iloc[0]
    elif tag == "e144":
        mask = truthy(df.get("materialized_submission", pd.Series(False, index=df.index)))
        if int(mask.sum()) == 0:
            mask = truthy(df.get("e144_submit", pd.Series(False, index=df.index)))
        row = df[mask].sort_values("all_minus_base").iloc[0]
    else:
        raise ValueError(tag)

    selected: dict[str, Any] = {
        "selected_tag": row.get("tag", tag),
        "strategy": row.get("strategy", ""),
        "target_axes": row.get("target_axes", ""),
    }
    for col in METRIC_COLUMNS:
        if col in row.index:
            selected[col] = row[col]
    return selected


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom == 0:
        return np.nan
    return float(np.dot(aa, bb) / denom)


def build_candidate_table() -> pd.DataFrame:
    logits = load_aligned_logits()
    e95 = logits["e95"]
    e144_move = logits["e144"] - e95
    e154_move = logits["e154"] - e95

    rows: list[dict[str, Any]] = []
    for tag, meta in CANDIDATES.items():
        move = logits[tag] - e95
        abs_move = np.abs(move)
        row: dict[str, Any] = {
            "tag": tag,
            "file": meta["file"],
            "role": meta["role"],
            "public_lb": PUBLIC_ANCHORS.get(tag, np.nan),
            "public_delta_vs_e95": PUBLIC_ANCHORS.get(tag, np.nan) - E95_PUBLIC
            if tag in PUBLIC_ANCHORS
            else np.nan,
            "logit_l1_vs_e95": float(abs_move.sum()),
            "logit_l2_vs_e95": float(np.linalg.norm(move.reshape(-1))),
            "mean_abs_logit_vs_e95": float(abs_move.mean()),
            "max_abs_logit_vs_e95": float(abs_move.max()),
            "changed_cells_vs_e95_computed": int((abs_move > 1e-12).sum()),
            "changed_rows_vs_e95_computed": int((abs_move > 1e-12).any(axis=1).sum()),
            "cos_vs_e144": cosine(move, e144_move),
            "cos_vs_e154": cosine(move, e154_move),
            "q_share": float(abs_move[:, :3].sum() / abs_move.sum()) if abs_move.sum() else 0.0,
            "s_share": float(abs_move[:, 3:].sum() / abs_move.sum()) if abs_move.sum() else 0.0,
        }
        row.update(select_metric_row(tag))
        rows.append(row)
    return pd.DataFrame(rows)


def build_pairwise(candidate_table: pd.DataFrame) -> pd.DataFrame:
    tags = ["e154", "e155", "e157", "e156", "e144"]
    logits = load_aligned_logits()
    e95 = logits["e95"]
    local = candidate_table.set_index("tag")
    rows: list[dict[str, Any]] = []
    for left in tags:
        for right in tags:
            if left == right:
                continue
            dl = logits[left] - e95
            dr = logits[right] - e95
            diff = logits[left] - logits[right]
            rows.append(
                {
                    "left": left,
                    "right": right,
                    "cos_left_right_vs_e95": cosine(dl, dr),
                    "logit_l1_left_minus_right": float(np.abs(diff).sum()),
                    "changed_cells_left_minus_right": int((np.abs(diff) > 1e-12).sum()),
                    "changed_rows_left_minus_right": int((np.abs(diff) > 1e-12).any(axis=1).sum()),
                    "local_all_minus_delta_left_minus_right": float(
                        local.loc[left, "all_minus_base"] - local.loc[right, "all_minus_base"]
                    ),
                    "post101_p95_delta_left_minus_right": float(
                        local.loc[left, "post101_p95_vs_e95_e101_sensor"]
                        - local.loc[right, "post101_p95_vs_e95_e101_sensor"]
                    ),
                    "e72_gap_delta_left_minus_right": float(
                        local.loc[left, "e72_plausible_gap_vs_e95"]
                        - local.loc[right, "e72_plausible_gap_vs_e95"]
                    ),
                    "local_delta_readable": bool(
                        abs(
                            float(local.loc[left, "all_minus_base"] - local.loc[right, "all_minus_base"])
                        )
                        >= PUBLIC_READABLE_DELTA
                    ),
                }
            )
    return pd.DataFrame(rows)


def build_score_bands() -> pd.DataFrame:
    rows = [
        {
            "outcome": "breakthrough_win",
            "delta_lo_exclusive": -np.inf,
            "delta_hi_inclusive": -PUBLIC_BREAKTHROUGH_DELTA,
            "world_update": "The repaired branch is larger than the current E95-over-mixmin edge. Add the observed file as a new anchor before testing siblings.",
            "next_action_e154": "Promote E154 and rerun exact-delta audits. Do not spend the next slot on E155/E157/E156 until the new anchor geometry is rebuilt.",
        },
        {
            "outcome": "clean_win",
            "delta_lo_exclusive": -PUBLIC_BREAKTHROUGH_DELTA,
            "delta_hi_inclusive": -PUBLIC_CLEAN_DELTA,
            "world_update": "The branch is public-real at readable frontier scale.",
            "next_action_e154": "Promote E154; use E155 only as a private-risk amplitude audit, not as the next automatic public file.",
        },
        {
            "outcome": "micro_win",
            "delta_lo_exclusive": -PUBLIC_CLEAN_DELTA,
            "delta_hi_inclusive": -PUBLIC_READABLE_DELTA,
            "world_update": "The branch is alive but remains calibration-scale.",
            "next_action_e154": "Promote E154 cautiously; next local work should seek non-collinear representation, not target-axis micro-tuning.",
        },
        {
            "outcome": "tie",
            "delta_lo_exclusive": -PUBLIC_READABLE_DELTA,
            "delta_hi_inclusive": PUBLIC_READABLE_DELTA,
            "world_update": "The public sensor cannot distinguish the branch from E95.",
            "next_action_e154": "Keep E95 practical frontier; E155 is allowed only if deliberately testing lower amplitude, not expected improvement.",
        },
        {
            "outcome": "small_loss",
            "delta_lo_exclusive": PUBLIC_READABLE_DELTA,
            "delta_hi_inclusive": E101_DELTA,
            "world_update": "The branch loses but not worse than the resolved E101 negative sensor.",
            "next_action_e154": "If spending another slot on this branch, E155 is the only clean same-family follow-up; do not jump to E157/E156 before E155.",
        },
        {
            "outcome": "branch_loss",
            "delta_lo_exclusive": E101_DELTA,
            "delta_hi_inclusive": MIXMIN_DELTA,
            "world_update": "The branch is weaker than E101 but still preserves some E95 gain over mixmin.",
            "next_action_e154": "Treat E155 as an explicit overextension test only. If E155 is skipped or loses, use E144 as the unrepaired contrast or close the branch.",
        },
        {
            "outcome": "hard_fail",
            "delta_lo_exclusive": MIXMIN_DELTA,
            "delta_hi_inclusive": np.inf,
            "world_update": "The branch gives back the E95 gain. Nearby repaired controls are suspect.",
            "next_action_e154": "Do not submit E157/E156. E155 is only an information-only amplitude salvage; otherwise fall back to E144 or representation search.",
        },
    ]
    out = pd.DataFrame(rows)
    out["public_lb_lo_exclusive"] = out["delta_lo_exclusive"].map(
        lambda x: E95_PUBLIC + x if np.isfinite(x) else -np.inf
    )
    out["public_lb_hi_inclusive"] = out["delta_hi_inclusive"].map(
        lambda x: E95_PUBLIC + x if np.isfinite(x) else np.inf
    )
    return out


def classify_score(bands: pd.DataFrame, score: float, candidate: str) -> pd.DataFrame:
    delta = float(score) - E95_PUBLIC
    mask = (
        (delta > bands["delta_lo_exclusive"].astype(float))
        & (delta <= bands["delta_hi_inclusive"].astype(float))
    )
    if int(mask.sum()) != 1:
        raise RuntimeError(f"Score {score} maps to {int(mask.sum())} bands")
    row = bands[mask].copy()
    row.insert(0, "candidate", candidate)
    row.insert(1, "observed_public_lb", float(score))
    row.insert(2, "observed_delta_vs_e95", delta)
    row.insert(3, "observed_delta_vs_e101", float(score) - E101_PUBLIC)
    row.insert(4, "observed_delta_vs_mixmin", float(score) - MIXMIN_PUBLIC)
    return row


def write_report(candidates: pd.DataFrame, pairwise: pd.DataFrame, bands: pd.DataFrame) -> None:
    cand_cols = [
        "tag",
        "role",
        "all_minus_base",
        "post101_p95_vs_e95_e101_sensor",
        "e72_plausible_gap_vs_e95",
        "body_norm_ratio",
        "changed_cells_vs_e95_computed",
        "cos_vs_e144",
        "cos_vs_e154",
    ]
    live = candidates[candidates["tag"].isin(["e154", "e155", "e157", "e156", "e144"])][cand_cols]
    pair_focus = pairwise[
        pairwise["left"].isin(["e154", "e155", "e157", "e156"])
        & pairwise["right"].isin(["e155", "e157", "e156", "e144"])
    ].copy()
    pair_focus = pair_focus[
        [
            "left",
            "right",
            "cos_left_right_vs_e95",
            "changed_cells_left_minus_right",
            "local_all_minus_delta_left_minus_right",
            "local_delta_readable",
        ]
    ].head(16)
    band_cols = [
        "outcome",
        "public_lb_lo_exclusive",
        "public_lb_hi_inclusive",
        "world_update",
        "next_action_e154",
    ]

    e155_e157 = pairwise[(pairwise["left"].eq("e157")) & (pairwise["right"].eq("e155"))].iloc[0]
    e154_e155 = pairwise[(pairwise["left"].eq("e154")) & (pairwise["right"].eq("e155"))].iloc[0]
    e156_e155 = pairwise[(pairwise["left"].eq("e156")) & (pairwise["right"].eq("e155"))].iloc[0]

    report = f"""# E158 Repaired Branch Public Decoder

## Question

The current next public file is `submission_e154_s3repair_9f2e2e73.csv`, but
E155/E157/E156/E144 now form a sensor stack around it. The question is not
"which tiny local edge is largest?" It is:

`If public feedback arrives for E154 or its controls, which hidden-world belief
dies, and which follow-up remains justified?`

## Strangest Point

The repaired controls are highly collinear and their local separations are much
smaller than the known public-sensor uncertainty. E157 beats E155 locally by
only `{float(e155_e157['local_all_minus_delta_left_minus_right']):.12f}` when
read as E157-minus-E155, while E154 beats E155 by
`{float(e154_e155['local_all_minus_delta_left_minus_right']):.12f}` and E156
is only `{float(e156_e155['local_all_minus_delta_left_minus_right']):.12f}`
away from E155. These are branch controls, not independent 0.54-path models.

## Live Candidate Geometry

{md_table(live)}

## Pairwise Distinguishability

{md_table(pair_focus)}

## Public Score Bands

{md_table(bands[band_cols])}

## Decision

- Submit order remains `E154 -> E155 -> E157 -> E156 -> E144`.
- E154 is the only first sensor because it asks the full repaired all-four
  question and is readable against unrepaired E144; its separation from E155 is
  not public-readable by the `2e-6` guardrail.
- E155 is the clean amplitude-control if E154 loses or ties.
- E157 and E156 should not be used before E155; their local separation from
  E155 is below the `2e-6` public-readable guardrail.
- If E154 hard-fails above mixmin, do not rescue with target-axis micro-controls.
  Either test E144 as the unrepaired contrast or return to representation search.

## Files

- candidate table: `analysis_outputs/e158_repaired_branch_public_decoder_candidates.csv`
- pairwise table: `analysis_outputs/e158_repaired_branch_public_decoder_pairwise.csv`
- score bands: `analysis_outputs/e158_repaired_branch_public_decoder_bands.csv`
"""
    (OUT / "e158_repaired_branch_public_decoder_report.md").write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", default="e154", choices=sorted(CANDIDATES))
    parser.add_argument("--score", type=float, default=None)
    args = parser.parse_args()

    candidates = build_candidate_table()
    pairwise = build_pairwise(candidates)
    bands = build_score_bands()

    candidates.to_csv(OUT / "e158_repaired_branch_public_decoder_candidates.csv", index=False)
    pairwise.to_csv(OUT / "e158_repaired_branch_public_decoder_pairwise.csv", index=False)
    bands.to_csv(OUT / "e158_repaired_branch_public_decoder_bands.csv", index=False)
    write_report(candidates, pairwise, bands)

    payload: dict[str, Any] = {
        "candidates": str(OUT / "e158_repaired_branch_public_decoder_candidates.csv"),
        "pairwise": str(OUT / "e158_repaired_branch_public_decoder_pairwise.csv"),
        "bands": str(OUT / "e158_repaired_branch_public_decoder_bands.csv"),
        "report": str(OUT / "e158_repaired_branch_public_decoder_report.md"),
    }
    if args.score is not None:
        decision = classify_score(bands, args.score, args.candidate)
        out = OUT / f"e158_{args.candidate}_observed_score_decision.csv"
        decision.to_csv(out, index=False)
        payload["observed_decision"] = str(out)
        payload["outcome"] = str(decision.iloc[0]["outcome"])
        payload["delta_vs_e95"] = float(decision.iloc[0]["observed_delta_vs_e95"])
    print(payload)


if __name__ == "__main__":
    main()
