#!/usr/bin/env python3
"""E139: can combo-set consensus decode the visible block-target state?

E138 showed that E136 block-target state and transfer-safe veto masks can
co-locate, but current E95 gradients still fail all-set tail/world structure.
This probe tests the smallest decoder change: require the three combo-set
gradient views to agree on movement direction before using the block-target
state and veto masks.

No public labels are fitted. A submission is materialized only if a movement is
simultaneously E95-local strict, transfer-veto-actionable, post-E101 favorable,
and material relative to E95.
"""

from __future__ import annotations

from pathlib import Path
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
import e137_blocktarget_state_movement_probe as e137  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


SCAN_OUT = OUT / "e139_blocktarget_set_consensus_decoder_probe_scan.csv"
SUMMARY_OUT = OUT / "e139_blocktarget_set_consensus_decoder_probe_summary.csv"
DECODER_OUT = OUT / "e139_blocktarget_set_consensus_decoder_probe_decoder_summary.csv"
REPORT_OUT = OUT / "e139_blocktarget_set_consensus_decoder_probe_report.md"
TRANSFER_OUT = OUT / "e139_blocktarget_set_consensus_decoder_probe_transfer.csv"
SUBMISSION_PREFIX = "submission_e139_bt_setcons"

EPS = 1.0e-6
MATERIAL_FLOOR = 1.0e-7
COMBO_SETS = ["inverse_top", "raw05_compatible", "all_sign"]
SHAPES = ["raw", "sqrt", "sign"]
SCALES = [0.010, 0.020, 0.040]

Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
S2 = TARGETS.index("S2")
S3 = TARGETS.index("S3")
S4 = TARGETS.index("S4")
Q2S3 = [Q2, S3]
S_ALL = [S1, S2, S3, S4]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def same_sign_mask(stack: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    signs = np.sign(stack)
    positive = np.all(signs > 0, axis=0)
    negative = np.all(signs < 0, axis=0)
    direction = positive.astype(float) - negative.astype(float)
    return positive | negative, direction


def majority_pair_unit(stack: np.ndarray, pair: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    a, b = pair
    pair_stack = stack[[a, b]]
    agree, direction = same_sign_mask(pair_stack)
    magnitude = np.minimum(np.abs(pair_stack[0]), np.abs(pair_stack[1]))
    return agree, direction * magnitude


def build_decoder_units(sample: pd.DataFrame, e95: np.ndarray) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    units = []
    for name in COMBO_SETS:
        units.append(-e132.gradient_for_context(sample, e95, name))
    stack = np.stack(units, axis=0)

    agree3, direction3 = same_sign_mask(stack)
    min3 = direction3 * np.min(np.abs(stack), axis=0)
    mean3 = direction3 * np.mean(np.abs(stack), axis=0)
    decoders: list[dict[str, Any]] = [
        {"decoder": "all3_min", "unit": min3, "agreement_mask": agree3, "source_sets": "all3"},
        {"decoder": "all3_mean", "unit": mean3, "agreement_mask": agree3, "source_sets": "all3"},
    ]
    for a, b in [(0, 1), (0, 2), (1, 2)]:
        agree, unit = majority_pair_unit(stack, (a, b))
        decoders.append(
            {
                "decoder": f"pair_{COMBO_SETS[a]}__{COMBO_SETS[b]}_min",
                "unit": unit,
                "agreement_mask": agree,
                "source_sets": f"{COMBO_SETS[a]},{COMBO_SETS[b]}",
            }
        )

    rows = []
    for rec in decoders:
        unit = np.asarray(rec["unit"], dtype=np.float64)
        agree = np.asarray(rec["agreement_mask"], dtype=bool)
        rows.append(
            {
                "decoder": rec["decoder"],
                "source_sets": rec["source_sets"],
                "agreement_cells": int(agree.sum()),
                "agreement_rows": int(agree.any(axis=1).sum()),
                "agreement_q2s3_cells": int(agree[:, Q2S3].sum()),
                "agreement_s_cells": int(agree[:, S_ALL].sum()),
                "unit_mean_abs": float(np.mean(np.abs(unit))),
                "unit_active_mean_abs": float(np.mean(np.abs(unit[agree]))) if agree.any() else 0.0,
                "unit_max_abs": float(np.max(np.abs(unit))),
            }
        )
    return decoders, pd.DataFrame(rows)


def eligible_rows(scan: pd.DataFrame) -> pd.DataFrame:
    return scan[
        scan["strategy"].eq("blocktarget_set_consensus_decoder")
        & scan["strict_gate"].fillna(False).astype(bool)
        & scan["gate_strict_actionable"].fillna(False).astype(bool)
        & scan["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & scan["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & scan["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & scan["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()


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
        e138.add_pred(
            rows,
            preds,
            seen_pred,
            refs[name],
            {"strategy": "control", "decoder": "", "mask_name": "", "shape": "", "scale": np.nan},
            base_index=base_index,
        )
    e95_index = seen_pred[e138.pred_key(refs["e95"])]

    state_masks = e138.filtered_state_masks(state)
    risk_sign = e132.risk_signs(tail_state)
    risk_weight = 1.0 * state + 0.50 * e130.normalize_nonzero(density["tail_equal"]) + 0.25
    decoders, decoder_summary = build_decoder_units(sample, refs["e95"])

    mask_frames: list[pd.DataFrame] = []
    for dec in decoders:
        unit_seed = np.asarray(dec["unit"], dtype=np.float64)
        safety_masks = e138.filtered_safety_masks(unit_seed, density, risk_sign, risk_weight)
        masks, mask_summary = e138.combined_masks(state, state_masks, safety_masks)
        if not mask_summary.empty:
            mask_summary.insert(0, "decoder", str(dec["decoder"]))
            mask_frames.append(mask_summary)
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
                    e138.add_pred(
                        rows,
                        preds,
                        seen_pred,
                        pred,
                        {
                            "strategy": "blocktarget_set_consensus_decoder",
                            "decoder": str(dec["decoder"]),
                            "source_sets": str(dec["source_sets"]),
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
    return pd.DataFrame(rows), preds, decoder_summary, mask_summary_all


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("blocktarget_set_consensus_decoder")].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["decoder", "state_scope", "safety_scope", "overlap_kind", "shape"]
    for keys, group in variants.groupby(group_cols, dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
        veto = group[group["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        submit = eligible_rows(local_and_veto)
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
    decoder_summary: pd.DataFrame,
    mask_summary: pd.DataFrame,
    transfer: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].eq("blocktarget_set_consensus_decoder")].copy()
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    submit = eligible_rows(scan)
    blockers = {}
    if len(evaluated):
        checks = {
            "all_margin_vs_mixmin": evaluated["all_margin_vs_mixmin"],
            "all_beats_base": evaluated["all_beats_base"],
            "structural_all_sets_beat_base": evaluated["structural_all_sets_beat_base"],
            "structural_all_sets_tail_neutral": evaluated["structural_all_sets_tail_neutral"],
            "structural_hidden_core_beats_base": evaluated["structural_hidden_core_beats_base"],
            "structural_world_nonworse": evaluated["structural_world_nonworse"],
            "structural_raw_energy_nonworse": evaluated["structural_raw_energy_nonworse"],
        }
        blockers = {name: int((~series.fillna(False).astype(bool)).sum()) for name, series in checks.items()}
    row_cols = [
        "decoder",
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
        "raw_energy_q_p90_minus_base",
        "e72_adverse_positive_exposure_all",
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
        else "No submission. Combo-set consensus did not produce a candidate that passes local strict plus transfer-veto plus post-E101 gates."
    )
    lines = [
        "# E139 Block-Target Set-Consensus Decoder Probe",
        "",
        "## Question",
        "",
        "E138 showed state-veto co-location but failed strict all-set/world health. E139 asks whether the missing decoder is just combo-set sign conflict: keep only movements whose combo-set gradients agree before applying the block-target state and veto masks.",
        "",
        "## Counts",
        "",
        f"- candidate rows: `{len(scan)}`",
        f"- set-consensus variants: `{len(variants)}`",
        f"- evaluated variants: `{len(evaluated)}`",
        f"- local strict variants: `{len(strict)}`",
        f"- transfer-veto-actionable variants: `{len(veto)}`",
        f"- local-strict plus transfer-veto-actionable variants: `{len(local_and_veto)}`",
        f"- final submit-gate variants: `{len(submit)}`",
        f"- transfer rows: `{len(transfer)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Decoder Summary",
        "",
        e138.md_table(decoder_summary, ".9f"),
        "",
        "## Gate Blockers Among Evaluated",
        "",
        "\n".join(f"- `{k}`: `{v}/{len(evaluated)}`" for k, v in blockers.items()) if blockers else "_none_",
        "",
        "## Mask Summary",
        "",
        e138.md_table(
            mask_summary.sort_values(["selected_cells", "mean_state"], ascending=[False, False]).head(30),
            ".9f",
        )
        if not mask_summary.empty
        else "_empty_",
        "",
        "## Summary",
        "",
        e138.md_table(summary.head(80), ".9f"),
        "",
        "## Best Local Evaluated Candidates",
        "",
        e138.md_table(evaluated.sort_values(["all_minus_base", "all_delta_vs_mixmin"])[row_cols].head(30), ".9f")
        if len(evaluated)
        else "None.",
        "",
        "## Local Strict Plus Transfer-Veto-Actionable Candidates",
        "",
        e138.md_table(local_and_veto.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(local_and_veto)
        else "None.",
        "",
        "## Submit-Gate Candidates",
        "",
        e138.md_table(submit.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
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
    rows, preds, decoder_summary, mask_summary = build_candidates(sample, refs, state, density, tail_state)

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
    decoder_summary.to_csv(DECODER_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, decoder_summary, mask_summary, transfer, submission_path)

    variants = scan[scan["strategy"].eq("blocktarget_set_consensus_decoder")]
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
