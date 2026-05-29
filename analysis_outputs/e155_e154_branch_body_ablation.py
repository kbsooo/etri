#!/usr/bin/env python3
"""E155: is E154's added branch body real signal or tuned overfit?

E154 opened the E152 all-four gate by repairing S3 active-boundary cells, but it
also added 109 E95-relative cells beyond E144. This probe ablates that extra
E144->E154 body without fitting public labels:

1. interpolate from E144 to E154 in logit space;
2. replay the selected E152 source with only the S3 repair keep factor changed;
3. drop or isolate target-wise pieces of the E154 body.

The kill question is narrow: does the all-four health gate survive a meaningful
reduction of the added body, or is E154 an isolated tuned point?
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
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e141_tail_tolerance_transfer_audit as e141  # noqa: E402
import e142_transfer_budget_clipped_decoder_probe as e142  # noqa: E402
import e153_gate_intersection_failure_atlas as e153  # noqa: E402
import e154_s3_active_boundary_repair_probe as e154  # noqa: E402


SCAN_OUT = OUT / "e155_e154_branch_body_ablation_scan.csv"
SUMMARY_OUT = OUT / "e155_e154_branch_body_ablation_summary.csv"
TARGET_OUT = OUT / "e155_e154_branch_body_target_ablation.csv"
REPORT_OUT = OUT / "e155_e154_branch_body_ablation_report.md"
SUBMISSION_PREFIX = "submission_e155_bodytemp"

EPS = 1.0e-6
MATERIAL_FLOOR = 1.0e-6
BODY_ALPHAS = [0.0, 0.10, 0.25, 0.50, 0.65, 0.75, 0.85, 1.0, 1.15, 1.30]
SOURCE_REPAIR_KEEPS = [0.0, 0.10, 0.25, 0.50, 0.75, 1.0]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def bool_col(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(False, index=frame.index)
    raw = frame[col]
    if raw.dtype == bool:
        return raw.fillna(False)
    return raw.astype(str).str.lower().isin({"true", "1", "yes"})


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 1.0e-15:
        return 0.0
    return float(np.dot(aa, bb) / denom)


def add_pred(
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
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, "e155_"), **rec})


def load_aligned(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def selected_e154_source() -> tuple[pd.Series, int]:
    scan = pd.read_csv(e154.SCAN_OUT, low_memory=False)
    selected = scan[scan.get("materialized_submission", False).fillna(False).astype(bool)].copy()
    if selected.empty:
        selected = scan[scan["tag"].astype(str).eq("e154_9f2e2e73")].copy()
    if selected.empty:
        raise RuntimeError("Could not find the materialized E154 row.")
    rec = selected.iloc[0]
    return rec, int(rec["source_pred_index"])


def target_mask(targets: list[str], shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    target_to_idx = {target: idx for idx, target in enumerate(TARGETS)}
    for target in targets:
        mask[:, target_to_idx[target]] = True
    return mask


def body_metrics(pred: np.ndarray, refs: dict[str, np.ndarray], body: np.ndarray, body_norm: float) -> dict[str, Any]:
    move = logit(pred) - logit(refs["e144"])
    e95_move = logit(pred) - logit(refs["e95"])
    active_body = np.abs(body) > 1.0e-10
    active_move = np.abs(move) > 1.0e-10
    target_l1 = np.abs(move).sum(axis=0)
    total_l1 = float(target_l1.sum())
    return {
        "body_norm_ratio": float(np.linalg.norm(move.reshape(-1)) / body_norm) if body_norm > 0 else 0.0,
        "body_cos_e154": cosine(move, body),
        "body_changed_cells": int(active_move.sum()),
        "body_changed_rows": int(active_move.any(axis=1).sum()),
        "body_overlap_cells": int((active_body & active_move).sum()),
        "e95_changed_cells": int((np.abs(e95_move) > 1.0e-10).sum()),
        "target_l1_total": total_l1,
        **{
            f"body_share_{target}": float(target_l1[idx] / total_l1) if total_l1 > 0 else 0.0
            for idx, target in enumerate(TARGETS)
        },
    }


def build_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    source_pred: np.ndarray,
    e154_selected: pd.Series,
) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, Any]]:
    e95_logit = logit(refs["e95"])
    e144_logit = logit(refs["e144"])
    e154_logit = logit(refs["e154"])
    source_logit = logit(source_pred)
    body = e154_logit - e144_logit
    source_delta = source_logit - e95_logit
    selected_delta = e154_logit - e95_logit
    repair_mask = np.abs(source_delta - selected_delta) > 1.0e-10
    body_norm = float(np.linalg.norm(body.reshape(-1)))

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    controls = {
        "control_e95": refs["e95"],
        "control_e144": refs["e144"],
        "control_e154": refs["e154"],
        "control_source_unrepaired": source_pred,
    }
    for strategy, pred in controls.items():
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": strategy,
                "ablation_family": "control",
                "alpha": np.nan,
                "keep_factor": np.nan,
                "target_group": "",
                "source_tag": str(e154_selected.get("source_tag", "")),
                "source_pred_index": int(e154_selected.get("source_pred_index", -1)),
                "repair_cells": int(repair_mask.sum()),
                **body_metrics(pred, refs, body, body_norm),
            },
        )

    for alpha in BODY_ALPHAS:
        pred = clip_prob(sigmoid(e144_logit + float(alpha) * body))
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": "branch_body_alpha",
                "ablation_family": "body_amplitude",
                "alpha": float(alpha),
                "keep_factor": np.nan,
                "target_group": "all",
                "source_tag": str(e154_selected.get("source_tag", "")),
                "source_pred_index": int(e154_selected.get("source_pred_index", -1)),
                "repair_cells": int(repair_mask.sum()),
                **body_metrics(pred, refs, body, body_norm),
            },
        )

    for keep in SOURCE_REPAIR_KEEPS:
        new_delta = source_delta.copy()
        new_delta[repair_mask] *= float(keep)
        pred = clip_prob(sigmoid(e95_logit + new_delta))
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": "source_repair_keep",
                "ablation_family": "source_s3_repair",
                "alpha": np.nan,
                "keep_factor": float(keep),
                "target_group": "repair_mask",
                "source_tag": str(e154_selected.get("source_tag", "")),
                "source_pred_index": int(e154_selected.get("source_pred_index", -1)),
                "repair_cells": int(repair_mask.sum()),
                **body_metrics(pred, refs, body, body_norm),
            },
        )

    groups = {
        **{target: [target] for target in TARGETS},
        "Q_all": ["Q1", "Q2", "Q3"],
        "S_all": ["S1", "S2", "S3", "S4"],
        "Q1_Q3": ["Q1", "Q3"],
        "S2_S3_S4": ["S2", "S3", "S4"],
        "Q3_S3": ["Q3", "S3"],
    }
    for group_name, targets in groups.items():
        mask = target_mask(targets, body.shape)
        drop_body = body.copy()
        drop_body[mask] = 0.0
        pred_drop = clip_prob(sigmoid(e144_logit + drop_body))
        add_pred(
            rows,
            preds,
            seen,
            pred_drop,
            {
                "strategy": "target_drop",
                "ablation_family": "target_drop",
                "alpha": np.nan,
                "keep_factor": np.nan,
                "target_group": group_name,
                "source_tag": str(e154_selected.get("source_tag", "")),
                "source_pred_index": int(e154_selected.get("source_pred_index", -1)),
                "repair_cells": int(repair_mask.sum()),
                **body_metrics(pred_drop, refs, body, body_norm),
            },
        )
        only_body = np.zeros_like(body)
        only_body[mask] = body[mask]
        pred_only = clip_prob(sigmoid(e144_logit + only_body))
        add_pred(
            rows,
            preds,
            seen,
            pred_only,
            {
                "strategy": "target_only",
                "ablation_family": "target_only",
                "alpha": np.nan,
                "keep_factor": np.nan,
                "target_group": group_name,
                "source_tag": str(e154_selected.get("source_tag", "")),
                "source_pred_index": int(e154_selected.get("source_pred_index", -1)),
                "repair_cells": int(repair_mask.sum()),
                **body_metrics(pred_only, refs, body, body_norm),
            },
        )

    meta = {
        "body_norm": body_norm,
        "repair_cells": int(repair_mask.sum()),
        "repair_targets": ",".join(
            sorted({TARGETS[j] for _, j in zip(*np.where(repair_mask), strict=False)})
        ),
        "source_tag": str(e154_selected.get("source_tag", "")),
        "source_pred_index": int(e154_selected.get("source_pred_index", -1)),
    }
    return pd.DataFrame(rows), preds, meta


def add_health_flags(scan: pd.DataFrame, e144_all_minus: float) -> pd.DataFrame:
    threshold = e141.e95_plausible_exposure_threshold()
    out = e142.add_relaxed_flags(scan, threshold)
    out["all_four_health"] = (
        out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
        & out["budget_ok"].fillna(False).astype(bool)
        & out["post101_ok"].fillna(False).astype(bool)
        & out["gate_strict_actionable"].fillna(False).astype(bool)
        & out["local_material"].fillna(False).astype(bool)
    )
    out["beats_e144_local"] = out["all_minus_base"].lt(float(e144_all_minus) - 1.0e-12)
    out["e155_submit"] = (
        ~out["strategy"].astype(str).str.startswith("control_")
        & out["all_four_health"]
        & out["beats_e144_local"]
        & out["all_minus_base"].lt(-1.0e-5)
    )
    out["health_class"] = "other"
    relaxed = out["relaxed_structural_tol1e12"].fillna(False).astype(bool)
    budget = out["budget_ok"].fillna(False).astype(bool)
    post101 = out["post101_ok"].fillna(False).astype(bool)
    action = out["gate_strict_actionable"].fillna(False).astype(bool)
    out.loc[relaxed & budget & post101 & action, "health_class"] = "all_four"
    out.loc[relaxed & budget & post101 & ~action, "health_class"] = "missing_actionable"
    out.loc[budget & post101 & action & ~relaxed, "health_class"] = "missing_relaxed"
    out.loc[relaxed & post101 & action & ~budget, "health_class"] = "missing_budget"
    out.loc[relaxed & budget & action & ~post101, "health_class"] = "missing_post101"
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, group in scan.groupby(["ablation_family", "strategy"], dropna=False):
        family, strategy = keys
        eligible = group[group["e155_submit"].fillna(False).astype(bool)].copy()
        all_four = group[group["all_four_health"].fillna(False).astype(bool)].copy()
        best = group.sort_values(["all_minus_base", "body_norm_ratio"], ascending=[True, True]).head(1)
        best_eligible = eligible.sort_values(["body_norm_ratio", "all_minus_base"], ascending=[True, True]).head(1)
        rows.append(
            {
                "ablation_family": str(family),
                "strategy": str(strategy),
                "rows": int(len(group)),
                "all_four_health": int(len(all_four)),
                "e155_submit": int(len(eligible)),
                "best_all_minus_base": float(best["all_minus_base"].iloc[0]) if len(best) else np.nan,
                "best_body_norm_ratio": float(best["body_norm_ratio"].iloc[0]) if len(best) else np.nan,
                "best_post101_p95": float(best["post101_p95_vs_e95_e101_sensor"].iloc[0]) if len(best) else np.nan,
                "best_e72_gap": float(best["e72_plausible_gap_vs_e95"].iloc[0]) if len(best) else np.nan,
                "lowest_risk_submit_tag": str(best_eligible["tag"].iloc[0]) if len(best_eligible) else "",
                "lowest_risk_submit_body_ratio": float(best_eligible["body_norm_ratio"].iloc[0])
                if len(best_eligible)
                else np.nan,
                "lowest_risk_submit_all_minus": float(best_eligible["all_minus_base"].iloc[0])
                if len(best_eligible)
                else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["e155_submit", "all_four_health", "best_body_norm_ratio", "best_all_minus_base"],
        ascending=[False, False, True, True],
    )


def target_summary(scan: pd.DataFrame) -> pd.DataFrame:
    focus = scan[scan["ablation_family"].isin(["target_drop", "target_only"])].copy()
    if focus.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for keys, group in focus.groupby(["ablation_family", "target_group"], dropna=False):
        family, target_group = keys
        best = group.sort_values("all_minus_base").iloc[0]
        rows.append(
            {
                "ablation_family": str(family),
                "target_group": str(target_group),
                "rows": int(len(group)),
                "all_four_health": int(group["all_four_health"].fillna(False).astype(bool).sum()),
                "e155_submit": int(group["e155_submit"].fillna(False).astype(bool).sum()),
                "best_all_minus_base": float(best["all_minus_base"]),
                "best_body_norm_ratio": float(best["body_norm_ratio"]),
                "best_relaxed": bool(best["relaxed_structural_tol1e12"]),
                "best_budget": bool(best["budget_ok"]),
                "best_post101": bool(best["post101_ok"]),
                "best_actionable": bool(best["gate_strict_actionable"]),
                "best_health_class": str(best["health_class"]),
                "best_tag": str(best["tag"]),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["ablation_family", "all_four_health", "e155_submit", "best_all_minus_base"],
        ascending=[True, False, False, True],
    )


def select_submission(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[
        scan["e155_submit"].fillna(False).astype(bool)
        & scan["body_norm_ratio"].lt(1.0 - 1.0e-12)
        & scan["strategy"].isin(["branch_body_alpha", "target_drop", "source_repair_keep"])
    ].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["body_norm_ratio", "post101_p95_vs_e95_e101_sensor", "all_minus_base"],
        ascending=[True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = str(chosen["tag"]).split("_")[-1]
    path = OUT / f"{SUBMISSION_PREFIX}_{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = clip_prob(pred)
    sub.to_csv(path, index=False)
    return path


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    keep = [col for col in cols if col in frame.columns]
    return e138.md_table(frame[keep].head(n), ".9f")


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    targets: pd.DataFrame,
    meta: dict[str, Any],
    submission_path: Path | None,
) -> None:
    variants = scan[~scan["strategy"].astype(str).str.startswith("control_")].copy()
    submit = variants[variants["e155_submit"].fillna(False).astype(bool)].copy()
    reduced = submit[submit["body_norm_ratio"].lt(1.0 - 1.0e-12)].copy()
    controls = scan[scan["strategy"].astype(str).str.startswith("control_")].copy()
    if submission_path is not None:
        decision = f"Materialized `{submission_path.name}` as a lower-body-ratio all-four E154-family candidate."
    elif len(reduced):
        decision = "Reduced-body all-four rows exist, but no materialized file was selected by the conservative selector."
    elif len(submit):
        decision = "Only full-or-higher E154 body rows beat E144 under all-four health. Keep E154 as the public sensor; do not create a watered-down follow-up."
    else:
        decision = "No E155 submission. Ablations do not produce a lower-risk all-four row that beats E144; E154 remains an exact repaired sensor, not a broad ridge."

    lines = [
        "# E155 E154 Branch-Body Ablation",
        "",
        "## Question",
        "",
        "E154 repaired S3 active-boundary actionability, but also added an E144-plus-orthogonal branch body. E155 asks whether that body can be reduced or target-ablated while keeping the all-four health gate and local edge over E144.",
        "",
        "## Source",
        "",
        f"- selected E154 source tag: `{meta['source_tag']}`.",
        f"- selected E154 source pred index: `{meta['source_pred_index']}`.",
        f"- detected repair cells: `{meta['repair_cells']}`.",
        f"- repair targets: `{meta['repair_targets']}`.",
        f"- E144->E154 body norm: `{meta['body_norm']:.12f}`.",
        "",
        "## Controls",
        "",
        md_table(
            controls.sort_values("all_minus_base"),
            [
                "strategy",
                "all_minus_base",
                "all_four_health",
                "relaxed_structural_tol1e12",
                "budget_ok",
                "post101_ok",
                "gate_strict_actionable",
                "body_norm_ratio",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "tag",
            ],
            20,
        ),
        "",
        "## Summary",
        "",
        md_table(summary, list(summary.columns), 40),
        "",
        "## Target Ablation",
        "",
        md_table(targets, list(targets.columns), 60),
        "",
        "## Frontier Rows",
        "",
        md_table(
            scan.sort_values(
                ["e155_submit", "all_four_health", "body_norm_ratio", "all_minus_base"],
                ascending=[False, False, True, True],
            ),
            [
                "strategy",
                "ablation_family",
                "target_group",
                "alpha",
                "keep_factor",
                "all_minus_base",
                "all_four_health",
                "e155_submit",
                "beats_e144_local",
                "relaxed_structural_tol1e12",
                "budget_ok",
                "post101_ok",
                "gate_strict_actionable",
                "body_norm_ratio",
                "body_cos_e154",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "tag",
            ],
            80,
        ),
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    refs["e144"] = load_aligned("submission_e144_activeboundary_d7b4b331.csv", sample)
    refs["e154"] = load_aligned("submission_e154_s3repair_9f2e2e73.csv", sample)
    _state, density, tail_state = e153.e152.setup_state(sample, refs)
    _sample2, refs2, _branch_axes, e152_preds = e153.rebuild_e152_predictions()
    refs.update(refs2)
    refs["e144"] = load_aligned("submission_e144_activeboundary_d7b4b331.csv", sample)
    refs["e154"] = load_aligned("submission_e154_s3repair_9f2e2e73.csv", sample)

    selected, source_idx = selected_e154_source()
    source_pred = clip_prob(e152_preds[source_idx])
    rows, preds, meta = build_candidates(sample, refs, source_pred, selected)

    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    e144_all = float(scan.loc[scan["strategy"].eq("control_e144"), "all_minus_base"].iloc[0])
    scan = add_health_flags(scan, e144_all)

    summary = summarize(scan)
    targets = target_summary(scan)
    submission_path = select_submission(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    write_report(scan, summary, targets, meta, submission_path)

    variants = scan[~scan["strategy"].astype(str).str.startswith("control_")].copy()
    print(
        {
            "rows": int(len(scan)),
            "variant_rows": int(len(variants)),
            "all_four_variants": int(variants["all_four_health"].fillna(False).astype(bool).sum()),
            "e155_submit": int(variants["e155_submit"].fillna(False).astype(bool).sum()),
            "reduced_body_submit": int(
                (
                    variants["e155_submit"].fillna(False).astype(bool)
                    & variants["body_norm_ratio"].lt(1.0 - 1.0e-12)
                ).sum()
            ),
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )
    print(summary.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
