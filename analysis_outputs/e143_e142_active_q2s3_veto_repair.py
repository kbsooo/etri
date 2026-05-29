#!/usr/bin/env python3
"""E143: can E142 also satisfy the active/Q2S3 veto?

E142 opened a candidate by clipping high E72-plausible exposure cells from an
E140 relaxed structural movement. Its remaining weakness is specific: the
legacy E128 strict-veto is false because E101-active / Q2S3 weighted movement
is still above the E101 reference, even though E72 budget and post-E101 p95 pass.

This audit asks whether that remaining veto is repairable by rolling back only
E101-active/Q2S3/S3 cells from E142 toward E95. If it is repairable without
killing local reward, the safer E143 file should replace E142. If it is not,
E142 remains the sharper public sensor and the active/Q2S3 veto is treated as a
known risk rather than a hard blocker for this residual branch.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e141_tail_tolerance_transfer_audit as e141  # noqa: E402
import e142_transfer_budget_clipped_decoder_probe as e142  # noqa: E402


E142_FILE = "submission_e142_transferclip_09a92236.csv"

SCAN_OUT = OUT / "e143_e142_active_q2s3_veto_repair_scan.csv"
SUMMARY_OUT = OUT / "e143_e142_active_q2s3_veto_repair_summary.csv"
FRONTIER_OUT = OUT / "e143_e142_active_q2s3_veto_repair_frontier.csv"
TRANSFER_OUT = OUT / "e143_e142_active_q2s3_veto_repair_transfer.csv"
REPORT_OUT = OUT / "e143_e142_active_q2s3_veto_repair_report.md"
SUBMISSION_PREFIX = "submission_e143_activeq2s3repair"

EPS = 1.0e-6
MATERIAL_FLOOR = 1.0e-6
KEEP_FACTORS = [0.0, 0.25, 0.50, 0.75]
TOP_COUNTS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 185]

Q2 = TARGETS.index("Q2")
S3 = TARGETS.index("S3")
Q2S3 = [Q2, S3]
S_ALL = [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"]]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def normalize_weight(values: np.ndarray) -> np.ndarray:
    return e130.normalize_weight(np.asarray(values, dtype=np.float64).reshape(-1)).reshape(values.shape)


def add_candidate(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    key = e138.pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, f"e143_{rec['mask_name']}_"), **rec})


def build_masks(delta: np.ndarray, density: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    active = np.abs(delta) > 1.0e-12
    n_rows, n_targets = delta.shape
    target_q2s3 = np.zeros_like(active)
    target_q2s3[:, Q2S3] = True
    target_s3 = np.zeros_like(active)
    target_s3[:, S3] = True
    e101_active = np.asarray(density["e101_active"], dtype=np.float64) > 0.5
    plausible = np.asarray(density["plausible"], dtype=np.float64)
    tail_equal = np.asarray(density["tail_equal"], dtype=np.float64)

    w_e101 = normalize_weight(e101_active.astype(float))
    w_q2s3 = normalize_weight(target_q2s3.astype(float))
    w_plausible = normalize_weight(plausible)
    w_tail = normalize_weight(tail_equal)
    abs_delta = np.abs(delta)
    tension_score = abs_delta * (w_e101 + w_q2s3 + 0.5 * w_plausible + 0.25 * w_tail)

    base_masks = [
        ("e101_active", active & e101_active),
        ("q2s3", active & target_q2s3),
        ("s3", active & target_s3),
        ("e101_q2s3", active & e101_active & target_q2s3),
        ("e101_or_q2s3", active & (e101_active | target_q2s3)),
        ("s3_non_e101", active & target_s3 & (~e101_active)),
        ("e101_non_q2s3", active & e101_active & (~target_q2s3)),
    ]
    masks: list[dict[str, Any]] = []
    seen: set[bytes] = set()
    for name, mask in base_masks:
        if not mask.any():
            continue
        key = mask.tobytes()
        if key not in seen:
            seen.add(key)
            masks.append({"mask_name": name, "mask": mask, "ranker": "full", "top_n": int(mask.sum())})
    flat_active = np.flatnonzero(active.reshape(-1))
    rankers = {
        "tension": tension_score.reshape(-1),
        "e101_weighted": (abs_delta * w_e101).reshape(-1),
        "q2s3_weighted": (abs_delta * w_q2s3).reshape(-1),
        "s3_abs": (abs_delta * target_s3.astype(float)).reshape(-1),
    }
    for ranker, score in rankers.items():
        valid = flat_active[score[flat_active] > 0.0]
        if len(valid) == 0:
            continue
        order = valid[np.argsort(-score[valid])]
        for top_n in TOP_COUNTS:
            if top_n <= 0 or top_n > len(order):
                continue
            mask = np.zeros((n_rows, n_targets), dtype=bool)
            mask.reshape(-1)[order[:top_n]] = True
            key = mask.tobytes()
            if key in seen:
                continue
            seen.add(key)
            masks.append({"mask_name": f"top_{ranker}_{top_n}", "mask": mask, "ranker": ranker, "top_n": int(top_n)})
    return masks


def build_candidates(sample: pd.DataFrame, refs: dict[str, np.ndarray], density: dict[str, np.ndarray]) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95 = refs["e95"]
    e142_pred = clip_prob(load_sub(E142_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    e95_logit = logit(e95)
    delta = logit(e142_pred) - e95_logit

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [e95, e142_pred]
    seen = {e138.pred_key(e95): 0, e138.pred_key(e142_pred): 1}
    rows.append(
        {
            "pred_index": 1,
            "base_index": 0,
            "tag": "e143_control_e142",
            "strategy": "control_e142",
            "mask_name": "none",
            "ranker": "",
            "top_n": 0,
            "keep_factor": 1.0,
            "rollback_cells": 0,
            "rollback_q2s3_cells": 0,
            "rollback_s_cells": 0,
        }
    )

    for mask_rec in build_masks(delta, density):
        mask = np.asarray(mask_rec["mask"], dtype=bool)
        for keep_factor in KEEP_FACTORS:
            new_delta = delta.copy()
            new_delta[mask] *= float(keep_factor)
            pred = clip_prob(sigmoid(e95_logit + new_delta))
            add_candidate(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "active_q2s3_repair",
                    "mask_name": str(mask_rec["mask_name"]),
                    "ranker": str(mask_rec["ranker"]),
                    "top_n": int(mask_rec["top_n"]),
                    "keep_factor": float(keep_factor),
                    "rollback_cells": int(mask.sum()),
                    "rollback_q2s3_cells": int(mask[:, Q2S3].sum()),
                    "rollback_s_cells": int(mask[:, S_ALL].sum()),
                },
            )
    return pd.DataFrame(rows), preds


def add_decision_flags(scan: pd.DataFrame, threshold: float) -> pd.DataFrame:
    out = e142.add_relaxed_flags(scan, threshold)
    out["original_strict_submit"] = (
        out["strategy"].eq("active_q2s3_repair")
        & out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["gate_strict_actionable"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    out["relaxed_submit"] = (
        out["strategy"].isin(["active_q2s3_repair", "control_e142"])
        & out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["budget_ok"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("active_q2s3_repair")].copy()
    rows: list[dict[str, Any]] = []
    for keys, group in variants.groupby(["mask_name", "keep_factor"], dropna=False):
        mask_name, keep_factor = keys
        relaxed = group[group["relaxed_structural_tol1e12"].fillna(False).astype(bool)]
        strict = group[group["original_strict_submit"].fillna(False).astype(bool)]
        budget = relaxed[relaxed["budget_ok"].fillna(False).astype(bool)]
        post = budget[budget["post101_ok"].fillna(False).astype(bool)]
        rows.append(
            {
                "mask_name": str(mask_name),
                "keep_factor": float(keep_factor),
                "rows": int(len(group)),
                "relaxed": int(len(relaxed)),
                "strict_submit": int(len(strict)),
                "budget_post": int(len(post)),
                "best_all_minus_e95": float(group["all_minus_base"].min()),
                "best_e101_active_l1": float(group["e101_active_delta95_l1"].min()),
                "best_q2s3_l1": float(group["q2s3_delta95_l1"].min()),
                "best_post101_p95": float(group["post101_p95_vs_e95_e101_sensor"].min()),
                "best_e72_gap": float(group["e72_plausible_gap_vs_e95"].min()),
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["strict_submit", "budget_post", "relaxed", "best_all_minus_e95"],
        ascending=[False, False, False, True],
    )


def frontier(scan: pd.DataFrame) -> pd.DataFrame:
    candidates = scan[scan["strategy"].isin(["active_q2s3_repair", "control_e142"])].copy()
    if candidates.empty:
        return candidates
    candidates["survival_score"] = (
        10.0 * candidates["original_strict_submit"].fillna(False).astype(float)
        + 3.0 * candidates["relaxed_submit"].fillna(False).astype(float)
        - candidates["all_minus_base"].clip(upper=0.0)
        - 30.0 * candidates["e72_plausible_gap_vs_e95"].clip(lower=0.0)
        - 30.0 * candidates["post101_p95_vs_e95_e101_sensor"].clip(lower=0.0)
        - 0.5 * (~candidates["gate_active_q2s3_not_more_than_e101"].fillna(False)).astype(float)
    )
    keep = [
        "strategy",
        "mask_name",
        "keep_factor",
        "rollback_cells",
        "rollback_q2s3_cells",
        "rollback_s_cells",
        "all_minus_base",
        "relaxed_structural_tol1e12",
        "gate_active_q2s3_not_more_than_e101",
        "gate_strict_actionable",
        "original_strict_submit",
        "relaxed_submit",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_plausible_gap_vs_e95",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "post101_beat_e95_rate_e101_sensor",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "survival_score",
        "tag",
    ]
    return (
        candidates.sort_values(
            ["original_strict_submit", "relaxed_submit", "survival_score", "all_minus_base"],
            ascending=[False, False, False, True],
        )
        .drop_duplicates("tag", keep="first")[keep]
        .head(80)
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    strict = scan[scan["original_strict_submit"].fillna(False).astype(bool)].copy()
    if strict.empty:
        return None
    chosen = strict.sort_values(
        ["post101_p95_vs_e95_e101_sensor", "all_minus_base", "mean_abs_logit_move_vs_e95"],
        ascending=[True, True, False],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, front: pd.DataFrame, submission_path: Path | None) -> None:
    control = scan[scan["strategy"].eq("control_e142")].head(1)
    variants = scan[scan["strategy"].eq("active_q2s3_repair")].copy()
    strict = variants[variants["original_strict_submit"].fillna(False).astype(bool)]
    relaxed = variants[variants["relaxed_submit"].fillna(False).astype(bool)]
    decision = (
        f"Materialized stricter replacement `{submission_path.name}`."
        if submission_path is not None
        else "No stricter replacement. E142 remains the next public sensor; active/Q2S3 repair either collapses local reward or fails the original strict-veto submit gate."
    )
    lines = [
        "# E143 E142 Active/Q2S3 Veto Repair",
        "",
        "## Question",
        "",
        "E142 passes relaxed structural, E72-budget, and post-E101 p95 gates, but fails the older active/Q2S3 movement veto. E143 asks whether that last risk can be repaired by rolling back only E101-active/Q2S3/S3 cells.",
        "",
        "## Counts",
        "",
        f"- repair variants: `{len(variants)}`",
        f"- relaxed-submit repair variants: `{len(relaxed)}`",
        f"- original-strict-submit repair variants: `{len(strict)}`",
        f"- materialized replacement: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## E142 Control",
        "",
        e138.md_table(
            control[
                [
                    "all_minus_base",
                    "gate_active_q2s3_not_more_than_e101",
                    "e101_active_delta95_l1",
                    "q2s3_delta95_l1",
                    "e72_plausible_gap_vs_e95",
                    "post101_p95_vs_e95_e101_sensor",
                    "relaxed_submit",
                    "tag",
                ]
            ],
            ".12f",
        )
        if len(control)
        else "_empty_",
        "",
        "## Summary",
        "",
        e138.md_table(summary.head(80), ".12f") if not summary.empty else "_empty_",
        "",
        "## Frontier Rows",
        "",
        e138.md_table(front.head(40), ".12f") if not front.empty else "_empty_",
        "",
        "## Interpretation",
        "",
    ]
    if len(variants):
        lines.extend(
            [
                f"- Best repair all-minus-E95: `{float(variants['all_minus_base'].min()):.12f}`.",
                f"- Minimum repair E101-active L1: `{float(variants['e101_active_delta95_l1'].min()):.12f}`.",
                f"- Minimum repair Q2/S3 L1: `{float(variants['q2s3_delta95_l1'].min()):.12f}`.",
                f"- Best repair post-E101 p95: `{float(variants['post101_p95_vs_e95_e101_sensor'].min()):.12f}`.",
            ]
        )
    lines.extend(["", "## Decision", "", decision])
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    _density_masks, density = e130.build_density_masks(sample, refs)
    threshold = e141.e95_plausible_exposure_threshold()
    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])

    rows, preds = build_candidates(sample, refs, density)
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    scan = add_decision_flags(scan, threshold)
    summary = summarize(scan)
    front = frontier(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    front.to_csv(FRONTIER_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, front, submission_path)

    variants = scan[scan["strategy"].eq("active_q2s3_repair")]
    strict = variants[variants["original_strict_submit"].fillna(False).astype(bool)]
    relaxed = variants[variants["relaxed_submit"].fillna(False).astype(bool)]
    control = scan[scan["strategy"].eq("control_e142")].iloc[0]
    print(
        {
            "variants": int(len(variants)),
            "relaxed_submit": int(len(relaxed)),
            "original_strict_submit": int(len(strict)),
            "control_gate_active_q2s3": bool(control["gate_active_q2s3_not_more_than_e101"]),
            "control_all_minus_e95": float(control["all_minus_base"]),
            "best_repair_all_minus_e95": float(variants["all_minus_base"].min()) if len(variants) else None,
            "best_repair_e101_active_l1": float(variants["e101_active_delta95_l1"].min()) if len(variants) else None,
            "best_repair_q2s3_l1": float(variants["q2s3_delta95_l1"].min()) if len(variants) else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(30).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
