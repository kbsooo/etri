#!/usr/bin/env python3
"""E138: can E136 state and E132 veto-nullspace co-locate?

E136 made the safe remainder visible after block-target compression. E137 then
showed that using that state alone as a gate over current E95 gradients does not
produce a safe movement. This probe asks the next narrower question: does the
visible block-target state become usable when it is intersected with the E132
veto-null / low-adverse transfer-safety masks?

No public labels are fitted. A submission is materialized only if a movement is
simultaneously E95-local strict, transfer-veto-actionable, post-E101 favorable,
and material relative to E95.
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
sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e132_veto_nullspace_gradient_probe as e132  # noqa: E402
import e136_target_compression_visibility_audit as e136  # noqa: E402
import e137_blocktarget_state_movement_probe as e137  # noqa: E402


SCAN_OUT = OUT / "e138_blocktarget_vetonull_overlap_probe_scan.csv"
SUMMARY_OUT = OUT / "e138_blocktarget_vetonull_overlap_probe_summary.csv"
MASK_OUT = OUT / "e138_blocktarget_vetonull_overlap_probe_mask_summary.csv"
TRANSFER_OUT = OUT / "e138_blocktarget_vetonull_overlap_probe_transfer.csv"
REPORT_OUT = OUT / "e138_blocktarget_vetonull_overlap_probe_report.md"
SUBMISSION_PREFIX = "submission_e138_bt_vetonull"

EPS = 1.0e-6
MATERIAL_FLOOR = 1.0e-7

Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
S2 = TARGETS.index("S2")
S3 = TARGETS.index("S3")
S4 = TARGETS.index("S4")
Q2S3 = [Q2, S3]
S_ALL = [S1, S2, S3, S4]

CONTEXTS = ["all", "raw05_compatible"]
STATE_KEEP_FRACS = {0.20, 0.30}
STATE_KEEP_SCOPES = {"all", "non_q2s3", "q1q3_sall"}
SAFETY_KEEP_SCOPES = {
    "veto_null",
    "veto_null_nonactive",
    "veto_null_nonq2s3",
    "low_adverse75",
    "low_adverse75_nonactive",
    "low_adverse75_nonq2s3",
}
SHAPES = ["raw", "sqrt", "sign"]
SCALES = [0.010, 0.020, 0.040]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_key(pred: np.ndarray) -> str:
    return hashlib.sha256(np.round(np.asarray(pred, dtype=np.float64), 12).tobytes()).hexdigest()


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
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen_pred: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
    base_index: int,
) -> None:
    key = pred_key(pred)
    if key in seen_pred:
        pred_index = seen_pred[key]
    else:
        pred_index = len(preds)
        seen_pred[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e138_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def filtered_state_masks(state: np.ndarray) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rec in e137.build_state_masks(state):
        frac = float(rec["state_frac"])
        scope = str(rec["scope"])
        if round(frac, 2) in STATE_KEEP_FRACS and scope in STATE_KEEP_SCOPES and rec["mask_kind"] == "hard":
            out.append(rec)
    return out


def filtered_safety_masks(
    unit: np.ndarray,
    density: dict[str, np.ndarray],
    risk_sign: np.ndarray,
    risk_weight: np.ndarray,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rec in e132.build_masks(unit, density, risk_sign, risk_weight):
        scope = str(rec["scope"])
        if scope in SAFETY_KEEP_SCOPES and float(rec["top_q"]) in {0.50, 0.70}:
            out.append(rec)
    return out


def combined_masks(
    state: np.ndarray,
    state_masks: list[dict[str, Any]],
    safety_masks: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    masks: list[dict[str, Any]] = []
    seen: set[bytes] = set()
    for sm in state_masks:
        state_weight = np.asarray(sm["mask"], dtype=np.float64)
        state_hard = state_weight > 1.0e-12
        for gm in safety_masks:
            safety_hard = np.asarray(gm["mask"], dtype=bool)
            hard = state_hard & safety_hard
            if not hard.any():
                continue
            variants = [
                ("hard", hard.astype(float)),
                ("state_soft", hard.astype(float) * state),
            ]
            for overlap_kind, weight in variants:
                if float(np.abs(weight).mean()) <= 1.0e-15:
                    continue
                key = np.round(weight, 9).tobytes()
                if key in seen:
                    continue
                seen.add(key)
                masks.append(
                    {
                        "mask_name": f"{sm['mask_name']}__{gm['mask_name']}__{overlap_kind}",
                        "mask": weight,
                        "overlap_kind": overlap_kind,
                        "state_mask": sm["mask_name"],
                        "state_kind": sm["mask_kind"],
                        "state_scope": sm["scope"],
                        "state_frac": float(sm["state_frac"]),
                        "safety_mask": gm["mask_name"],
                        "safety_scope": gm["scope"],
                        "safety_top_q": float(gm["top_q"]),
                    }
                )
                rows.append(
                    {
                        "mask_name": f"{sm['mask_name']}__{gm['mask_name']}__{overlap_kind}",
                        "overlap_kind": overlap_kind,
                        "state_mask": sm["mask_name"],
                        "state_kind": sm["mask_kind"],
                        "state_scope": sm["scope"],
                        "state_frac": float(sm["state_frac"]),
                        "safety_mask": gm["mask_name"],
                        "safety_scope": gm["scope"],
                        "safety_top_q": float(gm["top_q"]),
                        "selected_cells": int(hard.sum()),
                        "selected_rows": int(hard.any(axis=1).sum()),
                        "selected_q2s3_cells": int(hard[:, Q2S3].sum()),
                        "selected_s_cells": int(hard[:, S_ALL].sum()),
                        "mean_state": float(state[hard].mean()),
                        "mean_weight": float(weight[hard].mean()),
                    }
                )
    return masks, pd.DataFrame(rows)


def build_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    state: np.ndarray,
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], pd.DataFrame, pd.DataFrame]:
    e95_logit = logit(refs["e95"])
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen_pred: dict[str, int] = {}

    for name in ["mixmin", "e95", "e101", "e85", "e86", "e89", "e90", "noq2"]:
        base_index = 0 if name == "mixmin" else 1
        add_pred(
            rows,
            preds,
            seen_pred,
            refs[name],
            {"strategy": "control", "context": "", "mask_name": "", "shape": "", "scale": np.nan},
            base_index=base_index,
        )
    e95_index = seen_pred[pred_key(refs["e95"])]

    state_masks = filtered_state_masks(state)
    risk_sign = e132.risk_signs(tail_state)
    risk_weight = 1.0 * state + 0.50 * e130.normalize_nonzero(density["tail_equal"]) + 0.25

    diag_rows: list[dict[str, Any]] = []
    mask_frames: list[pd.DataFrame] = []
    for context in CONTEXTS:
        grad = e132.gradient_for_context(sample, refs["e95"], context)
        unit_seed = -grad
        safety_masks = filtered_safety_masks(unit_seed, density, risk_sign, risk_weight)
        masks, mask_summary = combined_masks(state, state_masks, safety_masks)
        if not mask_summary.empty:
            mask_summary.insert(0, "context", context)
            mask_frames.append(mask_summary)
        diag_rows.append(
            {
                "context": context,
                "grad_mean_abs": float(np.mean(np.abs(grad))),
                "grad_max_abs": float(np.max(np.abs(grad))),
                "safety_masks": int(len(safety_masks)),
                "overlap_masks": int(len(masks)),
                "risk_scalar_raw_unit": e132.risk_scalar(unit_seed, risk_sign, risk_weight),
            }
        )

        for mask_rec in masks:
            mask_weight = np.asarray(mask_rec["mask"], dtype=np.float64)
            hard = mask_weight > 1.0e-12
            if not hard.any():
                continue
            for shape in SHAPES:
                shaped = e137.normalize_unit(unit_seed * mask_weight, hard, shape)
                if float(np.abs(shaped).mean()) <= 1.0e-14:
                    continue
                for scale in SCALES:
                    delta = float(scale) * shaped
                    pred = clip_prob(sigmoid(e95_logit + delta))
                    add_pred(
                        rows,
                        preds,
                        seen_pred,
                        pred,
                        {
                            "strategy": "blocktarget_vetonull_overlap",
                            "context": context,
                            "mask_name": mask_rec["mask_name"],
                            "overlap_kind": mask_rec["overlap_kind"],
                            "state_mask": mask_rec["state_mask"],
                            "state_kind": mask_rec["state_kind"],
                            "state_scope": mask_rec["state_scope"],
                            "state_frac": float(mask_rec["state_frac"]),
                            "safety_mask": mask_rec["safety_mask"],
                            "safety_scope": mask_rec["safety_scope"],
                            "safety_top_q": float(mask_rec["safety_top_q"]),
                            "shape": shape,
                            "scale": float(scale),
                            "selected_cells": int(hard.sum()),
                            "selected_rows": int(hard.any(axis=1).sum()),
                            "selected_q2s3_cells": int(hard[:, Q2S3].sum()),
                            "selected_s_cells": int(hard[:, S_ALL].sum()),
                            "unit_mean_abs_logit_active": 1.0,
                            "unit_mean_abs_logit_global": float(np.mean(np.abs(shaped))),
                            "unit_max_abs_logit": float(np.max(np.abs(shaped))),
                            "risk_scalar_unit": e132.risk_scalar(shaped, risk_sign, risk_weight),
                            "risk_scalar_scaled": e132.risk_scalar(delta, risk_sign, risk_weight),
                        },
                        base_index=e95_index,
                    )
    mask_summary_all = pd.concat(mask_frames, ignore_index=True) if mask_frames else pd.DataFrame()
    return pd.DataFrame(rows), preds, pd.DataFrame(diag_rows), mask_summary_all


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("blocktarget_vetonull_overlap")].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["context", "state_scope", "safety_scope", "overlap_kind", "shape"]
    for keys, group in variants.groupby(group_cols, dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
        veto = group[group["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        submit = local_and_veto[
            local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
            & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
            & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
            & local_and_veto["all_minus_base"].lt(-MATERIAL_FLOOR)
        ]
        best_local = evaluated.sort_values("all_minus_base").head(1)
        best_sensor = evaluated.sort_values("post101_mean_vs_e95_e101_sensor").head(1)
        rows.append(
            {
                **dict(zip(group_cols, keys)),
                "rows": int(len(group)),
                "evaluated": int(len(evaluated)),
                "strict": int(len(strict)),
                "veto_actionable": int(len(veto)),
                "local_and_veto": int(len(local_and_veto)),
                "submit_gate": int(len(submit)),
                "best_all_minus_e95": float(best_local["all_minus_base"].iloc[0]) if len(best_local) else np.nan,
                "best_sensor_mean_vs_e95": float(best_sensor["post101_mean_vs_e95_e101_sensor"].iloc[0])
                if len(best_sensor)
                else np.nan,
                "best_sensor_p95_vs_e95": float(best_sensor["post101_p95_vs_e95_e101_sensor"].iloc[0])
                if len(best_sensor)
                else np.nan,
                "best_tail_exposure": float(best_local["e72_adverse_positive_exposure_all"].iloc[0])
                if len(best_local)
                else np.nan,
                "best_changed_cells": int(best_local["changed_cells_vs_e95"].iloc[0]) if len(best_local) else 0,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["submit_gate", "local_and_veto", "strict", "veto_actionable", "best_sensor_mean_vs_e95", "best_all_minus_e95"],
        ascending=[False, False, False, False, True, True],
    )


def eligible_rows(scan: pd.DataFrame) -> pd.DataFrame:
    return scan[
        scan["strategy"].eq("blocktarget_vetonull_overlap")
        & scan["strict_gate"].fillna(False).astype(bool)
        & scan["gate_strict_actionable"].fillna(False).astype(bool)
        & scan["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & scan["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & scan["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & scan["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = eligible_rows(scan)
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        [
            "post101_mean_vs_e95_e101_sensor",
            "post101_p95_vs_e95_e101_sensor",
            "all_minus_base",
            "mean_abs_logit_move_vs_e95",
        ],
        ascending=[True, True, True, False],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(out, index=False)
    return out


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    mask_summary: pd.DataFrame,
    gradient_diag: pd.DataFrame,
    transfer: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].eq("blocktarget_vetonull_overlap")].copy()
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    submit = eligible_rows(scan)
    row_cols = [
        "context",
        "state_mask",
        "safety_mask",
        "overlap_kind",
        "shape",
        "scale",
        "selected_cells",
        "selected_q2s3_cells",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "e72_adverse_positive_exposure_all",
        "mean_abs_logit_move_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "gate_strict_actionable",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "post101_beat_e95_rate_e101_sensor",
        "tag",
    ]
    decision = (
        f"Materialized `{submission_path.name}`."
        if submission_path is not None
        else "No submission. Intersecting E136 block-target state with E132 veto-null/low-adverse masks still did not produce a candidate that passes local strict plus transfer-veto plus post-E101 gates."
    )
    lines = [
        "# E138 Block-Target x Veto-Null Overlap Probe",
        "",
        "## Question",
        "",
        "E137 showed that block-target state alone cannot make the current E95 gradient safe. E138 asks whether the missing piece is simply co-location with the E132 transfer-safe veto-null / low-adverse masks.",
        "",
        "## Counts",
        "",
        f"- candidate rows: `{len(scan)}`",
        f"- overlap variants: `{len(variants)}`",
        f"- evaluated variants: `{len(evaluated)}`",
        f"- local strict variants: `{len(strict)}`",
        f"- transfer-veto-actionable variants: `{len(veto)}`",
        f"- local-strict plus transfer-veto-actionable variants: `{len(local_and_veto)}`",
        f"- final submit-gate variants: `{len(submit)}`",
        f"- transfer rows: `{len(transfer)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Gradient / Mask Diagnostics",
        "",
        md_table(gradient_diag, ".9f"),
        "",
        "## Mask Summary",
        "",
        md_table(
            mask_summary.sort_values(["selected_cells", "mean_state"], ascending=[False, False]).head(30),
            ".9f",
        ),
        "",
        "## Summary",
        "",
        md_table(summary.head(80), ".9f"),
        "",
        "## Best Local Evaluated Candidates",
        "",
        md_table(evaluated.sort_values(["all_minus_base", "all_delta_vs_mixmin"])[row_cols].head(30), ".9f")
        if len(evaluated)
        else "None.",
        "",
        "## Local Strict Plus Transfer-Veto-Actionable Candidates",
        "",
        md_table(local_and_veto.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(local_and_veto)
        else "None.",
        "",
        "## Submit-Gate Candidates",
        "",
        md_table(submit.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(submit)
        else "None.",
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    cell = pd.read_csv(OUT / "e133_local_safety_colocation_atlas_cell_detail.csv")
    _unit, state, _state_summary = e137.load_blocktarget_state(cell)
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    _density_masks, density = e130.build_density_masks(sample, refs)
    rows, preds, gradient_diag, mask_summary = build_candidates(sample, refs, state, density, tail_state)

    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    summary = summarize(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    mask_summary.to_csv(MASK_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, mask_summary, gradient_diag, transfer, submission_path)

    variants = scan[scan["strategy"].eq("blocktarget_vetonull_overlap")]
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)]
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)]
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)]
    submit = eligible_rows(scan)
    print(
        {
            "rows": int(len(scan)),
            "variants": int(len(variants)),
            "evaluated": int(len(evaluated)),
            "strict": int(len(strict)),
            "veto_actionable": int(len(veto)),
            "local_and_veto": int(len(local_and_veto)),
            "submit_gate": int(len(submit)),
            "best_all_minus_e95": float(evaluated["all_minus_base"].min()) if len(evaluated) else None,
            "best_sensor_mean_vs_e95": float(evaluated["post101_mean_vs_e95_e101_sensor"].min())
            if len(evaluated)
            else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(20).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
