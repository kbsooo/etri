#!/usr/bin/env python3
"""E104 E101 amplitude Pareto-cliff audit.

E103 rejected a direct edge-local replacement for E101, but it also exposed a
more precise question: is E101's 0.25 rollback just a coarse-grid accident, or a
Pareto point where more Q2/S3 rollback improves mean transfer while sacrificing
scenario support?

This script scans a fine alpha grid around E101 on the main active-cell masks.
It does not fit public labels. It reuses the E101 local+E95-conditioned transfer
frame and only materializes a file if a fine-grid row dominates E101 on broad
mean, p95, and beat-rate together.
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
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e103_edge_local_q2s3_amplitude_probe as e103  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402


CELLS_IN = OUT / "e102_e101_active_cell_structure_audit_cells.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
SCAN_OUT = OUT / "e104_e101_amplitude_pareto_cliff_scan.csv"
SUMMARY_OUT = OUT / "e104_e101_amplitude_pareto_cliff_summary.csv"
REPORT_OUT = OUT / "e104_e101_amplitude_pareto_cliff_report.md"
SUBMISSION_PREFIX = "submission_e104_e101amp"

EPS = 1.0e-6
ALPHAS = np.round(np.arange(0.0, 0.5001, 0.005), 3)
SELECTORS = [
    "active_all",
    "active_s3_all",
    "active_topgap40",
    "active_edge",
    "active_interior",
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    key = pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e104_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": tag, **rec})


def selector_masks(cells: pd.DataFrame, n_rows: int) -> dict[str, np.ndarray]:
    all_masks = dict(e103.build_selectors(cells, n_rows))
    missing = [name for name in SELECTORS if name not in all_masks]
    if missing:
        raise KeyError(f"missing selectors: {missing}")
    return {name: all_masks[name] for name in SELECTORS}


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    refs = e101.build_refs(sample)
    refs["e101"] = e101.load_pred(E101_FILE, sample)
    tail_state = e101.e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    cells = pd.read_csv(CELLS_IN)
    masks = selector_masks(cells, len(sample))
    edge_mask = e103.cells_to_mask(cells, cells["edge_distance"].astype(float).le(1.0), len(sample))

    e95_logit = logit(refs["e95"])
    mixmin_logit = logit(refs["mixmin"])
    rollback = mixmin_logit - e95_logit

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    for name in ["mixmin", "e95", "e101", "e89", "e85", "e86", "e90"]:
        add_pred(rows, preds, seen, refs[name], {"strategy": "control", "source": name})

    for selector_name, selector_mask in masks.items():
        effective_mask = selector_mask & (np.abs(rollback) > 1.0e-12)
        move_cells = int(effective_mask.sum())
        if move_cells == 0:
            continue
        move_rows = int(np.any(effective_mask, axis=1).sum())
        edge_cells = int(edge_mask[effective_mask].sum())
        target_scope = "+".join(TARGETS[j] for j in np.where(effective_mask.any(axis=0))[0])
        for alpha in ALPHAS:
            pred = clip_prob(sigmoid(e95_logit + float(alpha) * rollback * selector_mask))
            add_pred(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "e95_q2s3_tail_graft",
                    "source": "e95",
                    "fallback": "mixmin",
                    "selector": selector_name,
                    "target_scope": target_scope,
                    "graft_alpha": float(alpha),
                    "selected_cells": int(selector_mask.sum()),
                    "selected_rows": int(np.any(selector_mask, axis=1).sum()),
                    "move_cells": move_cells,
                    "move_rows": move_rows,
                    "move_edge_cells": edge_cells,
                    "move_edge_rate": edge_cells / max(move_cells, 1),
                },
            )

    return pd.DataFrame(rows), preds, refs, tail_state


def attach_flags(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    e101_ref = (
        out[out["strategy"].eq("control") & out["source"].eq("e101")]
        .sort_values("mean_vs_e95_broad_plausible")
        .iloc[0]
    )
    e101_mean = float(e101_ref["mean_vs_e95_broad_plausible"])
    e101_p95 = float(e101_ref["p95_vs_e95_broad_plausible"])
    e101_beat = float(e101_ref["beat_e95_rate_broad_plausible"])

    is_variant = out["strategy"].eq("e95_q2s3_tail_graft")
    out["mean_gain_vs_e101"] = out["mean_vs_e95_broad_plausible"] - e101_mean
    out["p95_gain_vs_e101"] = out["p95_vs_e95_broad_plausible"] - e101_p95
    out["beat_gap_vs_e101"] = out["beat_e95_rate_broad_plausible"] - e101_beat
    out["dominates_e101"] = (
        is_variant
        & out["e101_pass"].fillna(False).astype(bool)
        & (out["mean_vs_e95_broad_plausible"] <= e101_mean - 1.0e-8)
        & (out["p95_vs_e95_broad_plausible"] <= e101_p95 + 1.0e-10)
        & (out["beat_e95_rate_broad_plausible"] >= e101_beat - 1.0e-12)
    )
    out["beats_mean_p95_loses_beat"] = (
        is_variant
        & (out["mean_vs_e95_broad_plausible"] < e101_mean)
        & (out["p95_vs_e95_broad_plausible"] < e101_p95)
        & (out["beat_e95_rate_broad_plausible"] < e101_beat)
    )
    out["e101_ref_mean_vs_e95"] = e101_mean
    out["e101_ref_p95_vs_e95"] = e101_p95
    out["e101_ref_beat_rate"] = e101_beat
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("e95_q2s3_tail_graft")].copy()
    rows: list[dict[str, Any]] = []
    for selector, group in variants.groupby("selector"):
        e101_like = group.iloc[(group["graft_alpha"].astype(float) - 0.25).abs().argsort()].iloc[0]
        pass_rows = group[group["e101_pass"].fillna(False).astype(bool)]
        dom_rows = group[group["dominates_e101"].fillna(False).astype(bool)]
        mean_better = group[group["mean_gain_vs_e101"] < 0.0]
        mean_p95_better = group[group["beats_mean_p95_loses_beat"].fillna(False).astype(bool)]
        best_mean = group.sort_values("mean_vs_e95_broad_plausible").iloc[0]
        best_pass = pass_rows.sort_values("mean_vs_e95_broad_plausible").iloc[0] if not pass_rows.empty else None
        first_beat_drop = group[(group["graft_alpha"] > 0.25) & (group["beat_gap_vs_e101"] < 0.0)].sort_values("graft_alpha")
        rows.append(
            {
                "selector": selector,
                "rows": len(group),
                "pass_rows": int(len(pass_rows)),
                "dominates_e101": int(len(dom_rows)),
                "mean_better_rows": int(len(mean_better)),
                "mean_p95_better_but_beat_worse_rows": int(len(mean_p95_better)),
                "e101_like_alpha": float(e101_like["graft_alpha"]),
                "e101_like_mean_vs_e95": float(e101_like["mean_vs_e95_broad_plausible"]),
                "e101_like_p95_vs_e95": float(e101_like["p95_vs_e95_broad_plausible"]),
                "e101_like_beat": float(e101_like["beat_e95_rate_broad_plausible"]),
                "best_mean_alpha": float(best_mean["graft_alpha"]),
                "best_mean_vs_e95": float(best_mean["mean_vs_e95_broad_plausible"]),
                "best_mean_p95_vs_e95": float(best_mean["p95_vs_e95_broad_plausible"]),
                "best_mean_beat": float(best_mean["beat_e95_rate_broad_plausible"]),
                "best_pass_alpha": float(best_pass["graft_alpha"]) if best_pass is not None else np.nan,
                "best_pass_mean_vs_e95": float(best_pass["mean_vs_e95_broad_plausible"]) if best_pass is not None else np.nan,
                "best_pass_p95_vs_e95": float(best_pass["p95_vs_e95_broad_plausible"]) if best_pass is not None else np.nan,
                "best_pass_beat": float(best_pass["beat_e95_rate_broad_plausible"]) if best_pass is not None else np.nan,
                "first_alpha_above_0p25_with_beat_drop": (
                    float(first_beat_drop.iloc[0]["graft_alpha"]) if not first_beat_drop.empty else np.nan
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(["dominates_e101", "best_pass_mean_vs_e95"], ascending=[False, True])


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["dominates_e101"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["p95_vs_e95_broad_plausible", "mean_vs_e95_broad_plausible", "active_cells_vs_e95"],
        ascending=[True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    file_tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{file_tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, selected_path: Path | None) -> None:
    variants = scan[scan["strategy"].eq("e95_q2s3_tail_graft")].copy()
    controls = scan[scan["strategy"].eq("control")].copy()
    pass_rows = variants[variants["e101_pass"].fillna(False).astype(bool)].sort_values(
        ["selector", "graft_alpha"]
    )
    near_active = variants[variants["selector"].eq("active_all") & variants["graft_alpha"].between(0.225, 0.300)]
    best_mean = variants.sort_values(["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]).head(12)
    dominated = variants[variants["dominates_e101"].fillna(False).astype(bool)]

    control_cols = [
        "source",
        "all_delta_vs_mixmin",
        "e72_adverse_positive_exposure_all",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
    ]
    row_cols = [
        "tag",
        "selector",
        "graft_alpha",
        "move_cells",
        "move_edge_rate",
        "strict_gate",
        "e101_pass",
        "dominates_e101",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
        "mean_gain_vs_e101",
        "p95_gain_vs_e101",
        "beat_gap_vs_e101",
    ]

    n_dom = int(variants["dominates_e101"].fillna(False).sum())
    n_pass = int(variants["e101_pass"].fillna(False).sum())
    cliff = summary[summary["selector"].eq("active_all")].iloc[0]
    interpretation = (
        "A fine-grid alpha search found no E101-dominating successor. For the main "
        f"active_all mask, the first alpha above 0.25 that loses E101 beat-rate is "
        f"{float(cliff['first_alpha_above_0p25_with_beat_drop']):.3f}. This makes "
        "E101 a local Pareto point: more rollback improves broad mean/p95, but it "
        "immediately sacrifices scenario support."
        if n_dom == 0
        else "At least one fine-grid row dominates E101; inspect the materialized file before submitting."
    )

    report = f"""# E104 E101 Amplitude Pareto-Cliff

## Question

E103 rejected edge-only replacement. This audit asks whether E101's alpha `0.25`
is a coarse-grid accident or a Pareto cliff where additional rollback buys mean
transfer at the cost of E95-conditioned scenario support.

## Result

- fine-grid variant rows: `{len(variants)}`
- E101-pass rows: `{n_pass}`
- E101-dominating rows: `{n_dom}`
- materialized submission: `{selected_path.name if selected_path else 'none'}`

## Controls

{md_table(controls[control_cols].sort_values('all_delta_vs_mixmin'), '.9f')}

## Selector Summary

{md_table(summary, '.9f')}

## Active-All Near E101

{md_table(near_active[row_cols], '.9f')}

## Best Mean Rows

{md_table(best_mean[row_cols], '.9f')}

## Dominating Rows

{md_table(dominated[row_cols], '.9f')}

## Interpretation

{interpretation}
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, refs, tail_state = build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    scan = attach_flags(scan)
    summary = summarize(scan)
    selected_path = materialize(scan, preds, sample)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, selected_path)

    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")
    if selected_path:
        print(f"materialized {selected_path}")
    else:
        print("materialized none")


if __name__ == "__main__":
    main()
