#!/usr/bin/env python3
"""E144: refine the active/Q2S3 repair boundary opened by E143.

E143 showed that E142's remaining active/Q2S3 veto failure is repairable, but
its masks were intentionally coarse: top counts jump from 13 to 21, and keep
factors jump by 0.25. This audit asks a narrower question:

Can we satisfy the original active/Q2S3 strict gate with less rollback than the
E143 selected top-21 full repair, preserving more of E142's residual reward?

If yes, materialize a stricter replacement. If no, E143 remains the best current
sensor and the active/Q2S3 boundary is genuinely cliff-like.
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
import e143_e142_active_q2s3_veto_repair as e143  # noqa: E402


E143_FILE = "submission_e143_activeq2s3repair_68ca656f.csv"

SCAN_OUT = OUT / "e144_e143_active_boundary_refine_scan.csv"
SUMMARY_OUT = OUT / "e144_e143_active_boundary_refine_summary.csv"
FRONTIER_OUT = OUT / "e144_e143_active_boundary_refine_frontier.csv"
TRANSFER_OUT = OUT / "e144_e143_active_boundary_refine_transfer.csv"
REPORT_OUT = OUT / "e144_e143_active_boundary_refine_report.md"
SUBMISSION_PREFIX = "submission_e144_activeboundary"

EPS = 1.0e-6
Q2 = TARGETS.index("Q2")
S3 = TARGETS.index("S3")
Q2S3 = [Q2, S3]
S_ALL = [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"]]

FINE_TOP_COUNTS = list(range(14, 25))
FINE_KEEP_SMALL = [round(x, 2) for x in np.arange(0.00, 0.31, 0.05)]
FINE_KEEP_FULL = [round(x, 2) for x in np.arange(0.50, 0.76, 0.01)]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def ranked_masks(delta: np.ndarray, density: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    active = np.abs(delta) > 1.0e-12
    n_rows, n_targets = delta.shape
    target_q2s3 = np.zeros_like(active)
    target_q2s3[:, Q2S3] = True
    target_s3 = np.zeros_like(active)
    target_s3[:, S3] = True
    e101_active = np.asarray(density["e101_active"], dtype=np.float64) > 0.5
    plausible = np.asarray(density["plausible"], dtype=np.float64)
    tail_equal = np.asarray(density["tail_equal"], dtype=np.float64)

    w_e101 = e143.normalize_weight(e101_active.astype(float))
    w_q2s3 = e143.normalize_weight(target_q2s3.astype(float))
    w_plausible = e143.normalize_weight(plausible)
    w_tail = e143.normalize_weight(tail_equal)
    abs_delta = np.abs(delta)
    tension_score = abs_delta * (w_e101 + w_q2s3 + 0.5 * w_plausible + 0.25 * w_tail)

    masks: list[dict[str, Any]] = [
        {"mask_name": "q2s3", "mask": active & target_q2s3, "ranker": "full", "top_n": int((active & target_q2s3).sum())},
        {
            "mask_name": "s3_non_e101",
            "mask": active & target_s3 & (~e101_active),
            "ranker": "full",
            "top_n": int((active & target_s3 & (~e101_active)).sum()),
        },
    ]
    flat_active = np.flatnonzero(active.reshape(-1))
    rankers = {
        "q2s3_weighted": (abs_delta * w_q2s3).reshape(-1),
        "tension": tension_score.reshape(-1),
        "e101_weighted": (abs_delta * w_e101).reshape(-1),
    }
    seen = {m["mask"].tobytes() for m in masks if np.asarray(m["mask"], dtype=bool).any()}
    for ranker, score in rankers.items():
        valid = flat_active[score[flat_active] > 0.0]
        if len(valid) == 0:
            continue
        order = valid[np.argsort(-score[valid])]
        for top_n in FINE_TOP_COUNTS:
            if top_n > len(order):
                continue
            mask = np.zeros((n_rows, n_targets), dtype=bool)
            mask.reshape(-1)[order[:top_n]] = True
            key = mask.tobytes()
            if key in seen:
                continue
            seen.add(key)
            masks.append({"mask_name": f"top_{ranker}_{top_n}", "mask": mask, "ranker": ranker, "top_n": int(top_n)})
    return [m for m in masks if np.asarray(m["mask"], dtype=bool).any()]


def build_candidates(sample: pd.DataFrame, refs: dict[str, np.ndarray], density: dict[str, np.ndarray]) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95 = refs["e95"]
    e95_logit = logit(e95)
    e142_pred = clip_prob(load_sub(e143.E142_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    e143_pred = clip_prob(load_sub(E143_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    delta = logit(e142_pred) - e95_logit

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [e95, e142_pred, e143_pred]
    seen = {
        e138.pred_key(e95): 0,
        e138.pred_key(e142_pred): 1,
        e138.pred_key(e143_pred): 2,
    }
    controls = [
        ("control_e142", 1),
        ("control_e143", 2),
    ]
    for strategy, pred_index in controls:
        rows.append(
            {
                "pred_index": pred_index,
                "base_index": 0,
                "tag": f"e144_{strategy}",
                "strategy": strategy,
                "mask_name": "none",
                "ranker": "",
                "top_n": 0,
                "keep_factor": 1.0,
                "rollback_cells": 0,
                "rollback_q2s3_cells": 0,
                "rollback_s_cells": 0,
            }
        )

    for mask_rec in ranked_masks(delta, density):
        mask = np.asarray(mask_rec["mask"], dtype=bool)
        keep_factors = FINE_KEEP_FULL if mask_rec["ranker"] == "full" else FINE_KEEP_SMALL
        for keep_factor in keep_factors:
            new_delta = delta.copy()
            new_delta[mask] *= float(keep_factor)
            pred = clip_prob(sigmoid(e95_logit + new_delta))
            e143.add_candidate(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "active_boundary_refine",
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
    out = e143.add_decision_flags(scan, threshold)
    comparable = out["strategy"].isin(["active_boundary_refine", "control_e142", "control_e143"])
    generic_strict = (
        comparable
        & out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["gate_strict_actionable"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    generic_relaxed = (
        comparable
        & out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["budget_ok"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    out.loc[comparable, "original_strict_submit"] = generic_strict.loc[comparable].to_numpy()
    out.loc[comparable, "relaxed_submit"] = generic_relaxed.loc[comparable].to_numpy()
    boundary = out["strategy"].eq("active_boundary_refine")
    e143_row = out[out["strategy"].eq("control_e143")].head(1)
    if len(e143_row):
        e143_all = float(e143_row["all_minus_base"].iloc[0])
        e143_p95 = float(e143_row["post101_p95_vs_e95_e101_sensor"].iloc[0])
    else:
        e143_all = -9.551357769921331e-06
        e143_p95 = -3.368914796177015e-06
    out["beats_e143_local"] = out["all_minus_base"] < e143_all - 1.0e-12
    out["p95_not_worse_than_e143"] = out["post101_p95_vs_e95_e101_sensor"] <= e143_p95 + 1.0e-12
    out["e144_submit"] = (
        out["strategy"].eq("active_boundary_refine")
        & out["original_strict_submit"].fillna(False).astype(bool)
        & out["beats_e143_local"].fillna(False).astype(bool)
        & out["p95_not_worse_than_e143"].fillna(False).astype(bool)
    )
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("active_boundary_refine")].copy()
    rows: list[dict[str, Any]] = []
    for keys, group in variants.groupby(["mask_name"], dropna=False):
        mask_name = keys[0] if isinstance(keys, tuple) else keys
        strict = group[group["original_strict_submit"].fillna(False).astype(bool)]
        submit = group[group["e144_submit"].fillna(False).astype(bool)]
        rows.append(
            {
                "mask_name": str(mask_name),
                "rows": int(len(group)),
                "strict": int(len(strict)),
                "e144_submit": int(len(submit)),
                "best_all_minus_e95": float(group["all_minus_base"].min()),
                "best_strict_all_minus_e95": float(strict["all_minus_base"].min()) if len(strict) else np.nan,
                "best_submit_all_minus_e95": float(submit["all_minus_base"].min()) if len(submit) else np.nan,
                "max_keep_strict": float(strict["keep_factor"].max()) if len(strict) else np.nan,
                "min_q2s3_l1_strict": float(strict["q2s3_delta95_l1"].min()) if len(strict) else np.nan,
                "best_post101_p95": float(group["post101_p95_vs_e95_e101_sensor"].min()),
                "best_strict_post101_p95": float(strict["post101_p95_vs_e95_e101_sensor"].min()) if len(strict) else np.nan,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["e144_submit", "strict", "best_strict_all_minus_e95", "best_all_minus_e95"],
        ascending=[False, False, True, True],
    )


def frontier(scan: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "strategy",
        "mask_name",
        "keep_factor",
        "rollback_cells",
        "rollback_q2s3_cells",
        "rollback_s_cells",
        "all_minus_base",
        "original_strict_submit",
        "e144_submit",
        "beats_e143_local",
        "p95_not_worse_than_e143",
        "gate_active_q2s3_not_more_than_e101",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_plausible_gap_vs_e95",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "tag",
    ]
    candidates = scan[scan["strategy"].isin(["active_boundary_refine", "control_e143", "control_e142"])].copy()
    if candidates.empty:
        return candidates
    return (
        candidates.sort_values(
            ["e144_submit", "original_strict_submit", "all_minus_base", "post101_p95_vs_e95_e101_sensor"],
            ascending=[False, False, True, True],
        )[keep]
        .head(80)
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    submit = scan[scan["e144_submit"].fillna(False).astype(bool)].copy()
    if submit.empty:
        return None
    chosen = submit.sort_values(
        ["all_minus_base", "post101_p95_vs_e95_e101_sensor", "mean_abs_logit_move_vs_e95"],
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
    controls = scan[scan["strategy"].isin(["control_e142", "control_e143"])].copy()
    variants = scan[scan["strategy"].eq("active_boundary_refine")].copy()
    strict = variants[variants["original_strict_submit"].fillna(False).astype(bool)]
    submit = variants[variants["e144_submit"].fillna(False).astype(bool)]
    decision = (
        f"Materialized finer replacement `{submission_path.name}`."
        if submission_path is not None
        else "No finer replacement. E143 remains the current top submission sensor; the active/Q2S3 boundary is cliff-like at this resolution."
    )
    lines = [
        "# E144 E143 Active Boundary Refine",
        "",
        "## Question",
        "",
        "E143 repaired E142 with a coarse top-21 Q2/S3 rollback. E144 asks whether a finer top-count or keep-factor boundary can satisfy strict active/Q2S3 gates while preserving more E142 residual reward than E143.",
        "",
        "## Counts",
        "",
        f"- repair variants: `{len(variants)}`",
        f"- original-strict repair variants: `{len(strict)}`",
        f"- E144-submit variants: `{len(submit)}`",
        f"- materialized replacement: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Controls",
        "",
        e138.md_table(
            controls[
                [
                    "strategy",
                    "all_minus_base",
                    "original_strict_submit",
                    "gate_active_q2s3_not_more_than_e101",
                    "q2s3_delta95_l1",
                    "post101_p95_vs_e95_e101_sensor",
                    "tag",
                ]
            ],
            ".12f",
        ),
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
    if len(strict):
        best_strict = strict.sort_values("all_minus_base").iloc[0]
        lines.extend(
            [
                f"- Best strict repair: `{best_strict['tag']}`.",
                f"- Best strict all-minus-E95: `{float(best_strict['all_minus_base']):.12f}`.",
                f"- Best strict post-E101 p95: `{float(best_strict['post101_p95_vs_e95_e101_sensor']):.12f}`.",
                f"- Best strict Q2/S3 L1: `{float(best_strict['q2s3_delta95_l1']):.12f}`.",
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

    variants = scan[scan["strategy"].eq("active_boundary_refine")]
    strict = variants[variants["original_strict_submit"].fillna(False).astype(bool)]
    submit = variants[variants["e144_submit"].fillna(False).astype(bool)]
    best_strict = strict.sort_values("all_minus_base").head(1)
    print(
        {
            "variants": int(len(variants)),
            "strict": int(len(strict)),
            "e144_submit": int(len(submit)),
            "best_strict_all_minus_e95": float(best_strict["all_minus_base"].iloc[0]) if len(best_strict) else None,
            "best_strict_tag": str(best_strict["tag"].iloc[0]) if len(best_strict) else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(30).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
