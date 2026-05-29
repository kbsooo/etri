#!/usr/bin/env python3
"""E164: search the existing submission universe for broad post-E95 edges.

E163 split the world into two regimes:

- mixmin beat a2c8 with a broad signal;
- post-E95 refinements are mostly hard-label-resolution limited.

This probe asks the next small falsifiable question: among all existing
submission CSVs, is there already a mixmin-like broad successor to E95, or do
the broad-looking edges collapse onto known-bad/public-adverse axes?

No submission is generated. This is a selector-resolution and candidate-pool
audit.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402


SUMMARY_OUT = OUT / "e164_universe_broad_edge_screen_summary.csv"
SHORTLIST_OUT = OUT / "e164_universe_broad_edge_screen_shortlist.csv"
KNOWN_OUT = OUT / "e164_universe_broad_edge_screen_known.csv"
FAMILY_OUT = OUT / "e164_universe_broad_edge_screen_family.csv"
REPORT_OUT = OUT / "e164_universe_broad_edge_screen_report.md"

EPS = 1.0e-12
PUBLIC_READABLE_GUARD = 2.0e-6
E95_EDGE_OVER_MIXMIN = 0.0000153107
N_PUBLIC_CELLS = 250 * len(TARGETS)

E95_FILE = "submission_e95_hardtail_541e3973.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"

KNOWN_PUBLIC = {
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv": 0.5774393210,
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": 0.5779449757,
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": 0.5783033652,
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": 0.5784273528,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
    "submission_lejepa_targetwise_strict_best_scale0p5.csv": 0.5802468192,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    MIXMIN_FILE: 0.5763066405,
    E72_FILE: 0.5764077772,
    E95_FILE: 0.5762913298,
    E101_FILE: 0.5763003660,
}


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= 1.0e-15:
        return 0.0
    return float(np.dot(aa, bb) / den)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    keep = [c for c in cols if c in frame.columns]
    return e138.md_table(frame[keep].head(n), floatfmt)


def collect_submission_paths() -> list[Path]:
    paths: set[Path] = set()
    try:
        proc = subprocess.run(
            ["git", "ls-files", "*submission*.csv"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        for raw in proc.stdout.splitlines():
            path = (ROOT / raw).resolve()
            if path.exists() and path.name.startswith("submission") and path.suffix == ".csv":
                paths.add(path)
    except Exception:
        proc = subprocess.run(["rg", "--files"], cwd=ROOT, check=True, text=True, capture_output=True)
        for raw in proc.stdout.splitlines():
            path = (ROOT / raw).resolve()
            if path.exists() and path.name.startswith("submission") and path.suffix == ".csv":
                paths.add(path)
    return sorted(paths)


def load_prob(path: Path, sample: pd.DataFrame) -> np.ndarray | None:
    try:
        frame = pd.read_csv(path, usecols=KEYS + TARGETS).sort_values(KEYS).reset_index(drop=True)
    except Exception:
        return None
    if any(target not in frame.columns for target in TARGETS):
        return None
    if len(frame) != len(sample):
        return None
    if not frame[KEYS].astype(str).reset_index(drop=True).equals(sample[KEYS].astype(str).reset_index(drop=True)):
        return None
    return clip_prob(frame[TARGETS].to_numpy(dtype=np.float64))


def hard_breadth_metrics(p_new: np.ndarray, p_base: np.ndarray, priors: dict[str, np.ndarray]) -> dict[str, Any]:
    moved = np.abs(p_new - p_base) > EPS
    row_idx, target_idx = np.where(moved)
    out: dict[str, Any] = {
        "moved_cells": int(len(row_idx)),
        "moved_rows": int(len(np.unique(row_idx))) if len(row_idx) else 0,
        "targets_moved": ",".join(TARGETS[j] for j in sorted(set(target_idx))) if len(row_idx) else "",
        "expected_delta_focus_mean": 0.0,
        "total_swing": 0.0,
        "top1_swing": 0.0,
        "top5_swing": 0.0,
        "top10_swing": 0.0,
        "top25_swing": 0.0,
        "cells_for_2e6_guard": -1,
        "cells_for_e95_edge": -1,
        "cells_to_flip_expected_focus_mean": -1,
        "top1_over_abs_expected": np.nan,
        "top5_over_abs_expected": np.nan,
        "support_prob_swing_weighted_focus_mean": np.nan,
    }
    if len(row_idx) == 0:
        return out

    dy1, dy0 = e162.hard_loss_deltas(p_new[row_idx, target_idx], p_base[row_idx, target_idx])
    dy1_s = dy1 / N_PUBLIC_CELLS
    dy0_s = dy0 / N_PUBLIC_CELLS
    swing = np.abs(dy1_s - dy0_s)
    top = np.sort(swing)[::-1]
    py = priors["focus_mean"][row_idx, target_idx]
    expected = py * dy1_s + (1.0 - py) * dy0_s
    expected_sum = float(expected.sum())
    support_label = np.where(dy1_s < dy0_s, 1, 0)
    support_prob = np.where(support_label == 1, py, 1.0 - py)
    abs_expected = abs(expected_sum)

    out.update(
        {
            "expected_delta_focus_mean": expected_sum,
            "total_swing": float(swing.sum()),
            "top1_swing": float(top[0]) if len(top) else 0.0,
            "top5_swing": float(top[:5].sum()) if len(top) else 0.0,
            "top10_swing": float(top[:10].sum()) if len(top) else 0.0,
            "top25_swing": float(top[:25].sum()) if len(top) else 0.0,
            "cells_for_2e6_guard": e162.min_cells_for_threshold(swing, PUBLIC_READABLE_GUARD),
            "cells_for_e95_edge": e162.min_cells_for_threshold(swing, E95_EDGE_OVER_MIXMIN),
            "cells_to_flip_expected_focus_mean": e162.min_cells_for_threshold(swing, abs_expected),
            "top1_over_abs_expected": float((top[0] if len(top) else 0.0) / max(abs_expected, 1.0e-15)),
            "top5_over_abs_expected": float((top[:5].sum() if len(top) else 0.0) / max(abs_expected, 1.0e-15)),
            "support_prob_swing_weighted_focus_mean": float(np.average(support_prob, weights=swing))
            if float(swing.sum()) > 0
            else np.nan,
        }
    )
    return out


def prefix_metrics(metrics: dict[str, Any], prefix: str) -> dict[str, Any]:
    return {f"{prefix}_{k}": v for k, v in metrics.items()}


def target_group_share(move: np.ndarray, targets: set[str]) -> float:
    mask = np.array([target in targets for target in TARGETS], dtype=bool)
    vals = np.abs(move[:, mask])
    den = float(np.sum(np.abs(move)))
    if den <= 1.0e-15:
        return 0.0
    return float(np.sum(vals) / den)


def family_name(path: Path) -> str:
    text = path.name.lower()
    if "e154" in text or "e155" in text or "e156" in text or "e157" in text or "e144" in text:
        return "repaired_branch"
    if "e95" in text or "hardtail" in text:
        return "hardtail"
    if "e101" in text or "q2s3tail" in text:
        return "e101_q2s3"
    if "e72" in text or "q2_s3" in text or "q2s3" in text:
        return "q2s3_sparse"
    if "mixmin" in text:
        return "mixmin"
    if "jepa" in text or path.parts[-2] == "jepa":
        return "jepa"
    if "block" in text:
        return "block"
    if "hybrid" in text or "stage" in text:
        return "hybrid"
    return "other"


def screen() -> tuple[pd.DataFrame, dict[str, Any]]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)

    e95 = load_prob(OUT / E95_FILE, sample)
    mixmin = load_prob(OUT / MIXMIN_FILE, sample)
    e72 = load_prob(OUT / E72_FILE, sample)
    e101 = load_prob(OUT / E101_FILE, sample)
    e154 = load_prob(OUT / E154_FILE, sample)
    if e95 is None or mixmin is None or e72 is None or e101 is None or e154 is None:
        raise RuntimeError("missing required reference submissions")

    z_e95 = logit(e95)
    z_mixmin = logit(mixmin)
    axis_e95_from_mixmin = (z_e95 - z_mixmin).reshape(-1)
    axis_e72_from_mixmin = (logit(e72) - z_mixmin).reshape(-1)
    axis_e72_from_e95 = (logit(e72) - z_e95).reshape(-1)
    axis_e101_loss = (logit(e101) - z_e95).reshape(-1)
    axis_e154 = (logit(e154) - z_e95).reshape(-1)

    paths = collect_submission_paths()
    rows: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    skipped = 0
    duplicates = 0
    for idx, path in enumerate(paths, start=1):
        pred = load_prob(path, sample)
        if pred is None:
            skipped += 1
            continue
        key = e138.pred_key(pred)
        if key in seen:
            duplicates += 1
            continue
        seen[key] = str(path.relative_to(ROOT))

        move_e95 = logit(pred) - z_e95
        move_mix = logit(pred) - z_mixmin
        met_e95 = hard_breadth_metrics(pred, e95, priors)
        met_mix = hard_breadth_metrics(pred, mixmin, priors)
        public_lb = KNOWN_PUBLIC.get(path.name, np.nan)
        rec: dict[str, Any] = {
            "path": str(path.relative_to(ROOT)),
            "file": path.name,
            "family": family_name(path),
            "known_public_lb": public_lb,
            "known_delta_vs_e95": float(public_lb - KNOWN_PUBLIC[E95_FILE]) if np.isfinite(public_lb) else np.nan,
            "known_beats_e95": bool(public_lb < KNOWN_PUBLIC[E95_FILE]) if np.isfinite(public_lb) else np.nan,
            "q_share_vs_e95": target_group_share(move_e95, {"Q1", "Q2", "Q3"}),
            "s_share_vs_e95": target_group_share(move_e95, {"S1", "S2", "S3", "S4"}),
            "q2s3_share_vs_e95": target_group_share(move_e95, {"Q2", "S3"}),
            "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move_e95))),
            "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(move_mix))),
            "cos_move_e95_vs_e95_from_mixmin": cosine(move_e95, axis_e95_from_mixmin),
            "cos_move_e95_vs_e72_from_mixmin": cosine(move_e95, axis_e72_from_mixmin),
            "cos_move_e95_vs_e72_from_e95": cosine(move_e95, axis_e72_from_e95),
            "cos_move_e95_vs_e101_loss": cosine(move_e95, axis_e101_loss),
            "cos_move_e95_vs_e154": cosine(move_e95, axis_e154),
        }
        rec.update(prefix_metrics(met_e95, "vs_e95"))
        rec.update(prefix_metrics(met_mix, "vs_mixmin"))
        abs_exp = abs(float(rec["vs_e95_expected_delta_focus_mean"]))
        rec["broad_edge_score"] = float(
            max(0.0, -float(rec["vs_e95_expected_delta_focus_mean"]))
            * np.log1p(max(0.0, float(rec["vs_e95_cells_to_flip_expected_focus_mean"])))
            / (1.0 + max(0.0, float(rec["cos_move_e95_vs_e72_from_e95"])))
        )
        rec["broad_edge_gate"] = bool(
            rec["vs_e95_expected_delta_focus_mean"] < -5.0e-5
            and rec["vs_e95_cells_to_flip_expected_focus_mean"] >= 5
            and rec["vs_e95_top1_over_abs_expected"] < 0.75
            and rec["vs_e95_moved_cells"] >= 100
        )
        rec["low_e72_axis_gate"] = bool(rec["cos_move_e95_vs_e72_from_e95"] < 0.20)
        rec["not_known_public_bad"] = bool(not np.isfinite(public_lb) or public_lb <= KNOWN_PUBLIC[E95_FILE])
        rec["candidate_gate"] = bool(rec["broad_edge_gate"] and rec["low_e72_axis_gate"] and rec["not_known_public_bad"])
        rows.append(rec)

        if idx % 250 == 0:
            print({"seen_paths": idx, "unique_loaded": len(rows), "skipped": skipped, "duplicates": duplicates})

    stats = {
        "raw_paths": len(paths),
        "unique_predictions": len(rows),
        "skipped_load": skipped,
        "duplicates": duplicates,
    }
    return pd.DataFrame(rows), stats


def write_outputs(summary: pd.DataFrame, stats: dict[str, Any]) -> None:
    known = summary[summary["known_public_lb"].notna()].sort_values("known_public_lb").copy()
    shortlist = summary.sort_values(["candidate_gate", "broad_edge_score"], ascending=[False, False]).head(120).copy()
    family = (
        summary.groupby("family", dropna=False)
        .agg(
            rows=("file", "count"),
            broad_edge_gate=("broad_edge_gate", "sum"),
            low_e72_axis_gate=("low_e72_axis_gate", "sum"),
            candidate_gate=("candidate_gate", "sum"),
            best_broad_edge_score=("broad_edge_score", "max"),
            best_expected_delta_vs_e95=("vs_e95_expected_delta_focus_mean", "min"),
            median_e72_axis_cos=("cos_move_e95_vs_e72_from_e95", "median"),
        )
        .reset_index()
        .sort_values(["candidate_gate", "best_broad_edge_score"], ascending=[False, False])
    )

    summary.to_csv(SUMMARY_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    known.to_csv(KNOWN_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)

    candidate_rows = int(summary["candidate_gate"].sum())
    broad_rows = int(summary["broad_edge_gate"].sum())
    low_e72_broad = int((summary["broad_edge_gate"] & summary["low_e72_axis_gate"]).sum())
    known_broad_bad = int(
        (
            known["broad_edge_gate"].fillna(False)
            & known["known_public_lb"].gt(KNOWN_PUBLIC[E95_FILE])
            & ~known["file"].eq(E95_FILE)
        ).sum()
    )

    lines = [
        "# E164 Universe Broad Edge Screen",
        "",
        "## Question",
        "",
        "Does the existing submission universe contain a broad post-E95 successor, or are broad-looking edges still selector-unsafe and aligned with known bad axes?",
        "",
        "## Summary",
        "",
        f"- raw submission paths scanned: `{stats['raw_paths']}`.",
        f"- unique prediction tensors loaded: `{stats['unique_predictions']}`.",
        f"- skipped load/schema failures: `{stats['skipped_load']}`; duplicates: `{stats['duplicates']}`.",
        f"- broad-edge rows versus E95: `{broad_rows}`.",
        f"- broad-edge rows with low E72-axis cosine: `{low_e72_broad}`.",
        f"- final conservative candidate-gate rows: `{candidate_rows}`.",
        f"- known-public worse-than-E95 rows that still pass broad-edge gate: `{known_broad_bad}`.",
        "",
        "## Known-Public Calibration Rows",
        "",
        md_table(
            known,
            [
                "file",
                "known_public_lb",
                "known_delta_vs_e95",
                "broad_edge_gate",
                "candidate_gate",
                "vs_e95_expected_delta_focus_mean",
                "vs_e95_cells_to_flip_expected_focus_mean",
                "vs_e95_top1_over_abs_expected",
                "cos_move_e95_vs_e72_from_e95",
                "q2s3_share_vs_e95",
                "family",
            ],
            30,
        ),
        "",
        "## Top Shortlist By Broad-Edge Score",
        "",
        md_table(
            shortlist,
            [
                "file",
                "family",
                "known_public_lb",
                "candidate_gate",
                "broad_edge_gate",
                "low_e72_axis_gate",
                "broad_edge_score",
                "vs_e95_expected_delta_focus_mean",
                "vs_e95_cells_to_flip_expected_focus_mean",
                "vs_e95_top1_over_abs_expected",
                "cos_move_e95_vs_e72_from_e95",
                "cos_move_e95_vs_e101_loss",
                "q2s3_share_vs_e95",
                "vs_e95_moved_cells",
            ],
            40,
        ),
        "",
        "## Family Summary",
        "",
        md_table(
            family,
            [
                "family",
                "rows",
                "broad_edge_gate",
                "low_e72_axis_gate",
                "candidate_gate",
                "best_broad_edge_score",
                "best_expected_delta_vs_e95",
                "median_e72_axis_cos",
            ],
            40,
        ),
        "",
        "## Decision",
        "",
        "Broadness by itself is not enough. If the conservative gate is empty or dominated by known-bad families, then the existing universe has no pre-feedback broad successor to E95. If it is non-empty, those rows are still only hypothesis candidates until checked against the known-public calibration rows and E72/E101 axes.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary, stats = screen()
    write_outputs(summary, stats)
    print(
        {
            **stats,
            "broad_edge_gate": int(summary["broad_edge_gate"].sum()),
            "low_e72_broad": int((summary["broad_edge_gate"] & summary["low_e72_axis_gate"]).sum()),
            "candidate_gate": int(summary["candidate_gate"].sum()),
        }
    )
    cols = [
        "file",
        "family",
        "known_public_lb",
        "candidate_gate",
        "broad_edge_gate",
        "low_e72_axis_gate",
        "broad_edge_score",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_cells_to_flip_expected_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "cos_move_e95_vs_e72_from_e95",
    ]
    print(summary.sort_values(["candidate_gate", "broad_edge_score"], ascending=[False, False])[cols].head(30).to_string(index=False))


if __name__ == "__main__":
    main()
