#!/usr/bin/env python3
"""E169: materialize and stress-test E168 context/safety masked E166 moves.

E168 found that context-high plus veto/safe-density masks preserve a material
piece of E166's expected edge while improving safety metrics. This script turns
those masks into actual E95-relative prediction tensors and reruns the broad
breadth plus bad-axis geometry checks before any file is promoted.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import e166_broad_survivor_scale_probe as e166  # noqa: E402


E167_CELLS = OUT / "e167_broad_survivor_context_alignment_cells.csv"
E168_SUMMARY = OUT / "e168_e166_safety_context_decoupling_summary.csv"
SUMMARY_OUT = OUT / "e169_e166_context_safety_mask_materializer_summary.csv"
SHORTLIST_OUT = OUT / "e169_e166_context_safety_mask_materializer_shortlist.csv"
REPORT_OUT = OUT / "e169_e166_context_safety_mask_materializer_report.md"

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
EPS = 1.0e-15


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def bool_series(frame: pd.DataFrame, col: str) -> pd.Series:
    return frame[col].fillna(False).astype(bool)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return e166.load_prob_path(OUT / file_name, sample)


def mask_matrix(cells: pd.DataFrame, policy: str) -> np.ndarray:
    edge = bool_series(cells, "edge_like")
    between = cells["context_type"].eq("between_train_runs")
    context = edge | between
    veto = bool_series(cells, "all_veto_null")
    not_e72 = ~bool_series(cells, "e72_active")
    high_safe50 = cells["all_safe_density"].ge(cells["all_safe_density"].median())
    high_safe75 = cells["all_safe_density"].ge(cells["all_safe_density"].quantile(0.75))
    no_q2s3 = ~cells["target"].isin(["Q2", "S3"])
    s_only = cells["target"].isin(["S1", "S2", "S3", "S4"])
    masks = {
        "all_e166": pd.Series(True, index=cells.index),
        "context_high": context,
        "context_high__veto": context & veto,
        "context_high__high_density_p50": context & high_safe50,
        "context_high__high_density_p75": context & high_safe75,
        "context_high__veto_not_e72": context & veto & not_e72,
        "context_high__veto__no_q2s3": context & veto & no_q2s3,
        "context_high__veto__s_only": context & veto & s_only,
        "safety_veto_null": veto,
        "safety_high_density_p50": high_safe50,
        "safety_not_e72_active": not_e72,
    }
    if policy not in masks:
        raise KeyError(policy)
    arr = np.zeros((250, len(TARGETS)), dtype=bool)
    keep = cells[masks[policy]]
    arr[keep["sub_idx"].to_numpy(dtype=int), keep["target_idx"].to_numpy(dtype=int)] = True
    return arr


def score_policy(
    policy: str,
    sample: pd.DataFrame,
    z_e95: np.ndarray,
    z_e166: np.ndarray,
    priors: dict[str, np.ndarray],
    bad_names: list[str],
    bad_basis: np.ndarray,
    axes: dict[str, np.ndarray],
    e168_row: pd.Series | None,
    cells: pd.DataFrame,
) -> tuple[dict[str, Any], np.ndarray]:
    mask = mask_matrix(cells, policy)
    z = z_e95 + mask * (z_e166 - z_e95)
    pred = clip_prob(sigmoid(z))
    move = (z - z_e95).reshape(-1)
    hard = e164.hard_breadth_metrics(pred, sigmoid(z_e95), priors)
    bad_cos = {f"cos_bad_{name}": cosine(move, bad_basis[i]) for i, name in enumerate(bad_names)}
    max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
    max_bad_cos = float(bad_cos[f"cos_bad_{max_bad_name}"])
    bad_energy, bad_resid = e165.span_energy(move, bad_basis)
    entropy_delta = float(np.mean(e165.binary_entropy(pred) - e165.binary_entropy(sigmoid(z_e95))))
    mean_abs_move = float(np.mean(np.abs(move)))
    max_abs_move = float(np.max(np.abs(move)))
    q2s3_share = e164.target_group_share(move.reshape(len(sample), len(TARGETS)), {"Q2", "S3"})
    rec: dict[str, Any] = {
        "policy": policy,
        "expected_delta_focus_mean": float(hard["expected_delta_focus_mean"]),
        "moved_cells": int(hard["moved_cells"]),
        "moved_rows": int(hard["moved_rows"]),
        "targets_moved": str(hard["targets_moved"]),
        "cells_to_flip_expected": int(hard["cells_to_flip_expected_focus_mean"]),
        "top1_over_abs_expected": float(hard["top1_over_abs_expected"]),
        "top5_over_abs_expected": float(hard["top5_over_abs_expected"]),
        "cells_for_2e6_guard": int(hard["cells_for_2e6_guard"]),
        "cells_for_e95_edge": int(hard["cells_for_e95_edge"]),
        "support_prob_swing_weighted": float(hard["support_prob_swing_weighted_focus_mean"]),
        "bad_span_energy": bad_energy,
        "bad_span_residual": bad_resid,
        "max_bad_axis": max_bad_name,
        "max_bad_cos": max_bad_cos,
        "entropy_delta_vs_e95": entropy_delta,
        "mean_abs_logit_move_vs_e95": mean_abs_move,
        "max_abs_logit_move_vs_e95": max_abs_move,
        "q2s3_share_vs_e95": q2s3_share,
        "cos_e154_axis": cosine(move, axes["e154"]),
        "cos_e101_axis": cosine(move, axes["e101"]),
        "cos_mixmin_axis": cosine(move, axes["mixmin"]),
    }
    if e168_row is not None:
        for col in [
            "expected_abs_share_vs_all",
            "benefit_share_vs_all_focus",
            "top_benefit_focus_cells_kept",
            "edge_like_rate",
            "between_train_runs_rate",
            "all_veto_null_rate",
            "all_safe_density_mean",
            "e72_active_rate",
            "decoupling_pass",
        ]:
            rec[f"e168_{col}"] = e168_row.get(col, np.nan)
    rec["stress_gate"] = bool(
        rec["expected_delta_focus_mean"] <= -1.0e-4
        and rec["cells_to_flip_expected"] >= 20
        and rec["top1_over_abs_expected"] <= 0.060
        and rec["bad_span_energy"] < 0.60
        and rec["max_bad_cos"] < 0.50
        and -0.0025 <= rec["entropy_delta_vs_e95"] <= 0.0030
        and rec["mean_abs_logit_move_vs_e95"] <= 0.0030
        and rec["max_abs_logit_move_vs_e95"] <= 0.020
        and rec["q2s3_share_vs_e95"] <= 0.40
        and bool(rec.get("e168_decoupling_pass", False))
    )
    rec.update(bad_cos)
    return rec, pred


def run() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = load_prob(E95_FILE, sample)
    e166_pred = load_prob(E166_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e101 = load_prob(E101_FILE, sample)
    mixmin = load_prob(MIXMIN_FILE, sample)
    z_e95 = logit(e95)
    z_e166 = logit(e166_pred)
    axes = {
        "e154": (logit(e154) - z_e95).reshape(-1),
        "e101": (logit(e101) - z_e95).reshape(-1),
        "mixmin": (logit(mixmin) - z_e95).reshape(-1),
    }
    bad_names, bad_basis = e165.bad_axes(sample, z_e95)
    cells = pd.read_csv(E167_CELLS, low_memory=False)
    cells = cells[cells["pair"].eq("e166_vs_e95")].copy()
    e168_summary = pd.read_csv(E168_SUMMARY)
    e168_by_policy = {row.policy: row for row in e168_summary.itertuples(index=False)}

    policies = [
        "all_e166",
        "context_high",
        "context_high__veto",
        "context_high__high_density_p50",
        "context_high__high_density_p75",
        "context_high__veto_not_e72",
        "context_high__veto__no_q2s3",
        "context_high__veto__s_only",
        "safety_veto_null",
        "safety_high_density_p50",
        "safety_not_e72_active",
    ]
    rows: list[dict[str, Any]] = []
    preds: dict[str, np.ndarray] = {}
    for policy in policies:
        row_obj = e168_by_policy.get(policy)
        row_series = pd.Series(row_obj._asdict()) if row_obj is not None else None
        rec, pred = score_policy(policy, sample, z_e95, z_e166, priors, bad_names, bad_basis, axes, row_series, cells)
        rows.append(rec)
        preds[policy] = pred
    summary = pd.DataFrame(rows).sort_values(
        ["stress_gate", "expected_delta_focus_mean", "bad_span_energy"],
        ascending=[False, True, True],
    )

    shortlist = summary[summary["stress_gate"].fillna(False)].copy()
    if not shortlist.empty:
        shortlist = shortlist.sort_values(["expected_delta_focus_mean", "bad_span_energy"], ascending=[True, True])
        for i, row in enumerate(shortlist.itertuples(index=False), start=1):
            pred = preds[str(row.policy)]
            digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
            safe_name = str(row.policy).replace("__", "_").replace("context_high", "ctx").replace("safety", "safe")
            file_name = f"submission_e169_{safe_name}_{digest}.csv"
            out_path = OUT / file_name
            sub = sample[KEYS].copy()
            sub[TARGETS] = pred
            sub.to_csv(out_path, index=False)
            shortlist.loc[shortlist["policy"].eq(row.policy), "materialized_file"] = file_name
            if i >= 2:
                break
    summary.to_csv(SUMMARY_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)

    selected = shortlist.head(2).copy()
    lines = [
        "# E169 E166 Context/Safety Mask Materializer",
        "",
        "## Question",
        "",
        "Do the E168 context-high safety masks remain healthy after turning them into actual E95-relative prediction tensors and rerunning breadth plus bad-axis geometry?",
        "",
        "## Summary",
        "",
        f"- policies scored: `{len(summary)}`.",
        f"- stress-gate policies: `{int(summary['stress_gate'].sum())}`.",
        f"- materialized files: `{int(shortlist['materialized_file'].notna().sum()) if not shortlist.empty and 'materialized_file' in shortlist else 0}`.",
        "",
        "## Stress Summary",
        "",
        md_table(
            summary,
            [
                "policy",
                "expected_delta_focus_mean",
                "moved_cells",
                "moved_rows",
                "cells_to_flip_expected",
                "top1_over_abs_expected",
                "bad_span_energy",
                "max_bad_axis",
                "max_bad_cos",
                "mean_abs_logit_move_vs_e95",
                "max_abs_logit_move_vs_e95",
                "q2s3_share_vs_e95",
                "cos_e154_axis",
                "cos_e101_axis",
                "e168_decoupling_pass",
                "stress_gate",
            ],
            20,
        ),
        "",
        "## Materialized Shortlist",
        "",
        md_table(
            selected,
            [
                "policy",
                "materialized_file",
                "expected_delta_focus_mean",
                "moved_cells",
                "cells_to_flip_expected",
                "top1_over_abs_expected",
                "bad_span_energy",
                "max_bad_cos",
                "q2s3_share_vs_e95",
                "e168_top_benefit_focus_cells_kept",
                "e168_edge_like_rate",
                "e168_between_train_runs_rate",
                "e168_all_veto_null_rate",
                "e168_all_safe_density_mean",
                "e168_e72_active_rate",
            ],
            10,
        ),
        "",
        "## Decision",
        "",
        "E169 promotes the E168 result from a cell-mask diagnostic to actual candidate tensors. If a masked policy passes, it is not an E166 scale-up: it is a lower-amplitude context/safety repair that keeps only the E166 cells where hidden context and veto-density comfort overlap. It should be treated as a safer broad-branch follow-up than raw E166, but still needs public framing because the broad branch has no positive public anchor yet.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT_OUT)
    print(SUMMARY_OUT)
    print(SHORTLIST_OUT)


if __name__ == "__main__":
    run()
