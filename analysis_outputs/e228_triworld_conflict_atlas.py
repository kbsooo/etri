#!/usr/bin/env python3
"""E228: conflict atlas for the live E224/E166/E154 worldviews.

This audit creates no submission and trains no model. It answers a narrower
post-E216 question: are the three surviving files independent hidden-world
sensors, or are some of them duplicate movements that should not consume
separate public slots?
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

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E166_FILE = "submission_e166_broadsurv_s0p01_d8bfa94b.csv"
E176_FILE = "submission_e176_abl_q2_to0p75_91e49725.csv"
E216_FILE = "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

LIVE = {
    "e224": E224_FILE,
    "e166": E166_FILE,
    "e154": E154_FILE,
}

REFS = {
    "e176": E176_FILE,
    "e216": E216_FILE,
    "e72": E72_FILE,
    "e101": E101_FILE,
    "mixmin": MIXMIN_FILE,
}

E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E176_PUBLIC = 0.5763118310
E216_PUBLIC = 0.5772865088

SUMMARY_OUT = OUT / "e228_triworld_conflict_atlas_summary.csv"
PAIRWISE_OUT = OUT / "e228_triworld_conflict_atlas_pairwise.csv"
TARGETS_OUT = OUT / "e228_triworld_conflict_atlas_targets.csv"
BLOCKS_OUT = OUT / "e228_triworld_conflict_atlas_blocks.csv"
CELLS_OUT = OUT / "e228_triworld_conflict_atlas_cells.csv"
REPORT_OUT = OUT / "e228_triworld_conflict_atlas_report.md"

EPS = 1.0e-10


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n)
    lines = [
        "| " + " | ".join(str(c) for c in view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for rec in view.to_dict("records"):
        vals: list[str] = []
        for col in view.columns:
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


def prob(file_name: str, sample: pd.DataFrame | None = None) -> np.ndarray:
    df = load_sub(file_name, sample)
    return np.clip(df[TARGETS].to_numpy(dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    den = float(np.linalg.norm(a) * np.linalg.norm(b))
    if den <= EPS:
        return float("nan")
    return float(a @ b / den)


def make_sample_context(sample: pd.DataFrame) -> pd.DataFrame:
    out = sample[KEYS].copy()
    out["row_index"] = np.arange(len(out), dtype=int)
    out = out.sort_values(KEYS).reset_index(drop=True)
    out["row_in_subject"] = out.groupby("subject_id").cumcount()

    block_ids: list[str] = []
    for subject_id, part in out.groupby("subject_id", sort=False):
        current = -1
        last_date = None
        for _, rec in part.iterrows():
            current_date = rec["sleep_date"]
            if last_date is None or (current_date - last_date).days > 1:
                current += 1
            block_ids.append(f"{subject_id}_b{current}")
            last_date = current_date
    out["subject_block"] = block_ids
    return out.sort_values("row_index").reset_index(drop=True)


def top_mask(values: np.ndarray, k: int) -> np.ndarray:
    out = np.zeros(values.shape[0], dtype=bool)
    if k <= 0:
        return out
    use = min(k, values.shape[0])
    idx = np.argpartition(-values, use - 1)[:use]
    out[idx] = True
    return out


def movement_summary(tag: str, move: np.ndarray, refs: dict[str, np.ndarray]) -> dict[str, Any]:
    abs_move = np.abs(move)
    moved = abs_move > EPS
    target_abs = abs_move.sum(axis=0)
    total_abs = float(target_abs.sum())
    swing = np.sort(abs_move.reshape(-1))[::-1]
    rec: dict[str, Any] = {
        "tag": tag,
        "file_name": LIVE[tag],
        "moved_cells_vs_e95": int(moved.sum()),
        "moved_rows_vs_e95": int(moved.any(axis=1).sum()),
        "targets_moved_vs_e95": ",".join([TARGETS[j] for j in np.where(moved.any(axis=0))[0]]),
        "mean_abs_logit_vs_e95": float(abs_move.mean()),
        "max_abs_logit_vs_e95": float(abs_move.max()),
        "l1_logit_vs_e95": total_abs,
        "top1_logit_share_vs_e95": float(swing[:1].sum() / total_abs) if total_abs > EPS else np.nan,
        "top5_logit_share_vs_e95": float(swing[:5].sum() / total_abs) if total_abs > EPS else np.nan,
        "top25_logit_share_vs_e95": float(swing[:25].sum() / total_abs) if total_abs > EPS else np.nan,
    }
    for target_i, target in enumerate(TARGETS):
        rec[f"abs_share_{target}"] = float(target_abs[target_i] / total_abs) if total_abs > EPS else 0.0
    for ref_name, ref_move in refs.items():
        rec[f"cos_vs_{ref_name}"] = cosine(move.reshape(-1), ref_move.reshape(-1))
    return rec


def pairwise_row(left: str, right: str, moves: dict[str, np.ndarray]) -> dict[str, Any]:
    a = moves[left].reshape(-1)
    b = moves[right].reshape(-1)
    aa = np.abs(a)
    bb = np.abs(b)
    active_a = aa > EPS
    active_b = bb > EPS
    union = active_a | active_b
    shared = active_a & active_b
    min_mass = np.minimum(aa, bb)
    sign_same = np.sign(a) == np.sign(b)
    sign_conflict = shared & ~sign_same
    sign_support = shared & sign_same
    shared_min_mass = float(min_mass[shared].sum())
    conflict_min_mass = float(min_mass[sign_conflict].sum())
    support_min_mass = float(min_mass[sign_support].sum())
    left_l1 = float(aa.sum())
    right_l1 = float(bb.sum())
    union_l1 = float(np.maximum(aa, bb)[union].sum())
    top: dict[str, Any] = {}
    for k in (25, 50, 74, 250):
        left_top = top_mask(aa, k)
        right_top = top_mask(bb, k)
        overlap = left_top & right_top
        top[f"top{k}_overlap_cells"] = int(overlap.sum())
        top[f"top{k}_overlap_rate_left"] = float(overlap.sum() / max(1, left_top.sum()))
        top[f"top{k}_overlap_rate_right"] = float(overlap.sum() / max(1, right_top.sum()))

    return {
        "left": left,
        "right": right,
        "cosine": cosine(a, b),
        "active_overlap_cells": int(shared.sum()),
        "active_overlap_rate_left": float(shared.sum() / max(1, active_a.sum())),
        "active_overlap_rate_right": float(shared.sum() / max(1, active_b.sum())),
        "shared_min_mass": shared_min_mass,
        "support_min_mass": support_min_mass,
        "conflict_min_mass": conflict_min_mass,
        "sign_conflict_rate_by_shared_min_mass": float(conflict_min_mass / shared_min_mass)
        if shared_min_mass > EPS
        else np.nan,
        "sign_support_rate_by_shared_min_mass": float(support_min_mass / shared_min_mass)
        if shared_min_mass > EPS
        else np.nan,
        "left_mass_covered_same_sign_by_right": float(support_min_mass / left_l1) if left_l1 > EPS else np.nan,
        "right_mass_covered_same_sign_by_left": float(support_min_mass / right_l1) if right_l1 > EPS else np.nan,
        "left_mass_conflicted_by_right": float(conflict_min_mass / left_l1) if left_l1 > EPS else np.nan,
        "right_mass_conflicted_by_left": float(conflict_min_mass / right_l1) if right_l1 > EPS else np.nan,
        "union_l1_logit": union_l1,
        **top,
    }


def target_rows(moves: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target_i, target in enumerate(TARGETS):
        row: dict[str, Any] = {"target": target}
        for tag in LIVE:
            m = moves[tag][:, target_i]
            row[f"{tag}_l1"] = float(np.abs(m).sum())
            row[f"{tag}_moved_cells"] = int((np.abs(m) > EPS).sum())
            row[f"{tag}_mean_signed"] = float(m.mean())
            row[f"{tag}_max_abs"] = float(np.abs(m).max())
        for left, right in [("e224", "e166"), ("e224", "e154"), ("e166", "e154")]:
            a = moves[left][:, target_i]
            b = moves[right][:, target_i]
            aa = np.abs(a)
            bb = np.abs(b)
            shared = (aa > EPS) & (bb > EPS)
            min_mass = np.minimum(aa, bb)
            conflict = shared & (np.sign(a) != np.sign(b))
            denom = float(min_mass[shared].sum())
            row[f"{left}_{right}_cos"] = cosine(a, b)
            row[f"{left}_{right}_conflict_rate"] = float(min_mass[conflict].sum() / denom) if denom > EPS else np.nan
            row[f"{left}_{right}_shared_min_mass"] = denom
        rows.append(row)
    return pd.DataFrame(rows)


def cell_table(sample: pd.DataFrame, e95_prob: np.ndarray, probs: dict[str, np.ndarray]) -> pd.DataFrame:
    context = make_sample_context(sample)
    base_logit = logit(e95_prob)
    candidate_logits = {tag: logit(value) for tag, value in probs.items()}
    moves = {tag: candidate_logits[tag] - base_logit for tag in probs}
    records: list[dict[str, Any]] = []
    for row_i, base in context.iterrows():
        for target_i, target in enumerate(TARGETS):
            rec: dict[str, Any] = {
                "row_index": int(base["row_index"]),
                "subject_id": base["subject_id"],
                "sleep_date": base["sleep_date"],
                "lifelog_date": base["lifelog_date"],
                "row_in_subject": int(base["row_in_subject"]),
                "subject_block": base["subject_block"],
                "target": target,
                "e95_prob": float(e95_prob[row_i, target_i]),
            }
            for tag in probs:
                dz = float(moves[tag][row_i, target_i])
                rec[f"{tag}_prob"] = float(probs[tag][row_i, target_i])
                rec[f"{tag}_logit_move"] = dz
                rec[f"{tag}_abs_logit_move"] = abs(dz)
                rec[f"{tag}_sign"] = int(np.sign(dz)) if abs(dz) > EPS else 0
            rec["e224_e166_conflict"] = (
                int(rec["e224_sign"] * rec["e166_sign"] < 0)
                if rec["e224_sign"] and rec["e166_sign"]
                else 0
            )
            rec["e224_e154_conflict"] = (
                int(rec["e224_sign"] * rec["e154_sign"] < 0)
                if rec["e224_sign"] and rec["e154_sign"]
                else 0
            )
            rec["e166_e154_conflict"] = (
                int(rec["e166_sign"] * rec["e154_sign"] < 0)
                if rec["e166_sign"] and rec["e154_sign"]
                else 0
            )
            rec["max_abs_live_move"] = max(
                rec["e224_abs_logit_move"], rec["e166_abs_logit_move"], rec["e154_abs_logit_move"]
            )
            records.append(rec)
    cells = pd.DataFrame(records)
    for tag in probs:
        cells[f"{tag}_abs_rank"] = cells[f"{tag}_abs_logit_move"].rank(method="first", ascending=False)
        cells[f"{tag}_top50"] = cells[f"{tag}_abs_rank"].le(50)
        cells[f"{tag}_top74"] = cells[f"{tag}_abs_rank"].le(74)
        cells[f"{tag}_top250"] = cells[f"{tag}_abs_rank"].le(250)
    return cells


def block_rows(cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for level in ["subject_id", "subject_block"]:
        grouped = cells.groupby(level, sort=False)
        out = grouped.agg(
            n_cells=("target", "size"),
            n_rows=("row_index", "nunique"),
            e224_l1=("e224_abs_logit_move", "sum"),
            e166_l1=("e166_abs_logit_move", "sum"),
            e154_l1=("e154_abs_logit_move", "sum"),
            e224_e166_conflicts=("e224_e166_conflict", "sum"),
            e224_e154_conflicts=("e224_e154_conflict", "sum"),
            e166_e154_conflicts=("e166_e154_conflict", "sum"),
            e224_top50=("e224_top50", "sum"),
            e166_top50=("e166_top50", "sum"),
            e154_top50=("e154_top50", "sum"),
        ).reset_index()
        out.insert(0, "level", level)
        out = out.rename(columns={level: "group"})
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


def write_report(
    summary: pd.DataFrame,
    pairwise: pd.DataFrame,
    targets: pd.DataFrame,
    blocks: pd.DataFrame,
    cells: pd.DataFrame,
) -> None:
    e224_e154 = pairwise[(pairwise["left"].eq("e224")) & (pairwise["right"].eq("e154"))].iloc[0]
    e224_e166 = pairwise[(pairwise["left"].eq("e224")) & (pairwise["right"].eq("e166"))].iloc[0]
    e166_e154 = pairwise[(pairwise["left"].eq("e166")) & (pairwise["right"].eq("e154"))].iloc[0]
    top_conflicts = cells[
        cells[["e224_e166_conflict", "e224_e154_conflict", "e166_e154_conflict"]].any(axis=1)
    ].sort_values("max_abs_live_move", ascending=False)
    block_view = blocks.sort_values(["level", "e224_l1", "e166_l1", "e154_l1"], ascending=[True, False, False, False])

    text = f"""# E228 Tri-World Conflict Atlas

## Question

After the E216 public miss, are the remaining E224, E166, and E154 candidates three independent public questions, or should they be combined/tuned as if they were one movement family?

## Main Read

- E224 and E166 are genuinely different movement worlds: cosine `{float(e224_e166['cosine']):.6f}` and only `{float(e224_e166['left_mass_covered_same_sign_by_right']):.6f}` of E224 mass is covered by same-sign E166 movement.
- E166 and E154 are also different: cosine `{float(e166_e154['cosine']):.6f}`.
- E224 and E154 are not independent in the same sense. E224 has cosine `{float(e224_e154['cosine']):.6f}` to E154, and E154 covers `{float(e224_e154['left_mass_covered_same_sign_by_right']):.6f}` of E224 mass / `{float(e224_e154['right_mass_covered_same_sign_by_left']):.6f}` of E154 mass by same-sign shared movement.
- The practical route is therefore not a naive tri-blend. Use E224 for the JEPA capped-Q3/S4 question, E166 for the broad safety-atlas-overconservatism question, and E154 only as the conservative repaired-branch counter-world, especially after attribution says E224 failed on the Q3/S4 residual rather than the inherited body.

## Candidate Movement Summary

{md_table(summary, floatfmt=".9f")}

## Pairwise Conflict Geometry

{md_table(pairwise, floatfmt=".9f")}

## Target-Level Conflict

{md_table(targets, floatfmt=".9f")}

## Largest Sign-Conflict Cells

{md_table(top_conflicts[[
        'row_index',
        'subject_id',
        'sleep_date',
        'lifelog_date',
        'subject_block',
        'target',
        'e224_logit_move',
        'e166_logit_move',
        'e154_logit_move',
        'e224_e166_conflict',
        'e224_e154_conflict',
        'e166_e154_conflict',
        'max_abs_live_move',
    ]], n=40, floatfmt=".9f")}

## Block/Subject Concentration

{md_table(block_view, n=60, floatfmt=".9f")}

## Decision

- Do not create a blind E224/E166/E154 blend before public feedback. The blend would destroy the interpretation: an improvement could come from two orthogonal worlds or from cancellation, while a loss would not identify the failed component.
- E154 is a valid counter-world but not a clean independent alternative to E224, because E224 already inherits part of the E154 repaired body.
- E166 is the cleanest independent non-JEPA sensor. Its public score should be decoded by E227, not by scaling or mixing.
- E224 is still the only live JEPA submission route. Its public score should be decoded by E225, not treated as a reason to tune Q3 by hand.

## Files

- summary: `{SUMMARY_OUT.relative_to(ROOT)}`
- pairwise: `{PAIRWISE_OUT.relative_to(ROOT)}`
- target conflict: `{TARGETS_OUT.relative_to(ROOT)}`
- block/subject concentration: `{BLOCKS_OUT.relative_to(ROOT)}`
- cell atlas: `{CELLS_OUT.relative_to(ROOT)}`
"""
    REPORT_OUT.write_text(text, encoding="utf-8")


def main() -> None:
    sample = load_sub(E95_FILE)
    e95_prob = prob(E95_FILE, sample)
    live_probs = {tag: prob(file_name, sample) for tag, file_name in LIVE.items()}
    ref_probs = {tag: prob(file_name, sample) for tag, file_name in REFS.items()}
    base = logit(e95_prob)
    live_moves = {tag: logit(value) - base for tag, value in live_probs.items()}
    ref_moves = {tag: logit(value) - base for tag, value in ref_probs.items()}
    all_refs = {**live_moves, **ref_moves}

    summary = pd.DataFrame([movement_summary(tag, live_moves[tag], all_refs) for tag in LIVE])
    pairwise = pd.DataFrame(
        [
            pairwise_row("e224", "e166", live_moves),
            pairwise_row("e224", "e154", live_moves),
            pairwise_row("e166", "e154", live_moves),
        ]
    )
    targets = target_rows(live_moves)
    cells = cell_table(sample, e95_prob, live_probs)
    blocks = block_rows(cells)

    summary.to_csv(SUMMARY_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    targets.to_csv(TARGETS_OUT, index=False)
    blocks.to_csv(BLOCKS_OUT, index=False)
    cells.to_csv(CELLS_OUT, index=False)
    write_report(summary, pairwise, targets, blocks, cells)

    print("[E228]")
    print(f"report={REPORT_OUT}")
    print(md_table(pairwise, floatfmt=".9f"))


if __name__ == "__main__":
    main()
