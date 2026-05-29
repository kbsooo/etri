#!/usr/bin/env python3
"""E137: can E136 block-target state create an E95-safe movement?

E136 found that the E133 safe-remainder teacher is much more visible after
block-target compression.  This probe asks the next smallest question: if that
compressed state gates the E95 local combo-gradient, do local upside and
transfer/hardtail safety finally overlap?

This is not a new learner and not a direct submission recipe.  It reuses E132's
donor-free gradient movement, replacing top-cell masks with E136 predicted
block-target state masks.
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


SCAN_OUT = OUT / "e137_blocktarget_state_movement_probe_scan.csv"
SUMMARY_OUT = OUT / "e137_blocktarget_state_movement_probe_summary.csv"
STATE_OUT = OUT / "e137_blocktarget_state_movement_probe_state_summary.csv"
TRANSFER_OUT = OUT / "e137_blocktarget_state_movement_probe_transfer.csv"
REPORT_OUT = OUT / "e137_blocktarget_state_movement_probe_report.md"
SUBMISSION_PREFIX = "submission_e137_blocktarget_grad"

EPS = 1.0e-6
MATERIAL_FLOOR = 1.0e-7
Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
S2 = TARGETS.index("S2")
S3 = TARGETS.index("S3")
S4 = TARGETS.index("S4")
Q2S3 = [Q2, S3]
S_ALL = [S1, S2, S3, S4]

CONTEXTS = ["all", "all_sign", "raw05_compatible", "inverse_top", "loo_inverse_top", "loo_raw05_compatible"]
STATE_FRACS = [0.10, 0.15, 0.20, 0.30]
SHAPES = ["raw", "sqrt", "sign"]
SCALES = [0.0025, 0.0050, 0.0100, 0.0200, 0.0400]


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
    tag = e83.stable_tag(pred, f"e137_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def normalize_state(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64).copy()
    finite = np.isfinite(arr)
    if not finite.any():
        return np.zeros_like(arr)
    arr[~finite] = float(np.nanmedian(arr[finite]))
    lo = float(np.min(arr))
    hi = float(np.max(arr))
    if hi <= lo:
        return np.ones_like(arr)
    return (arr - lo) / (hi - lo)


def load_blocktarget_state(cell: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    unit = e136.aggregate_block_target(cell)
    pred_path = OUT / "e136_target_compression_visibility_predictions.csv"
    if not pred_path.exists():
        raise FileNotFoundError(pred_path)
    pred = pd.read_csv(pred_path)
    chosen = pred[
        pred["unit_type"].eq("block_target")
        & pred["feature_set"].eq("all_raw_views_raw_pred")
        & pred["model"].eq("ridge")
    ].copy()
    if len(chosen) != len(unit):
        raise ValueError(f"E136 prediction/unit mismatch: {len(chosen)} vs {len(unit)}")
    unit = unit.reset_index(drop=True).copy()
    unit["state_pred_raw"] = chosen.sort_values("unit_index")["pred"].to_numpy(dtype=np.float64)
    unit["state_pred"] = normalize_state(unit["state_pred_raw"].to_numpy(dtype=np.float64))
    unit["state_teacher_share"] = e136.normalize(unit["teacher"].to_numpy(dtype=np.float64))

    target_to_idx = {target: i for i, target in enumerate(TARGETS)}
    block_target_pred: dict[tuple[str, str], float] = {
        (str(rec["hidden_block_id"]), str(rec["target"])): float(rec["state_pred"])
        for rec in unit.to_dict("records")
    }
    state = np.zeros((int(cell["sub_idx"].max()) + 1, len(TARGETS)), dtype=np.float64)
    for rec in cell[["sub_idx", "hidden_block_id", "target"]].drop_duplicates().to_dict("records"):
        row = int(rec["sub_idx"])
        target = str(rec["target"])
        state[row, target_to_idx[target]] = block_target_pred[(str(rec["hidden_block_id"]), target)]

    rows: list[dict[str, Any]] = []
    for frac in STATE_FRACS:
        k = max(1, int(np.ceil(len(unit) * frac)))
        top = unit.sort_values("state_pred", ascending=False).head(k)
        rows.append(
            {
                "state_frac": frac,
                "state_units": k,
                "teacher_mass": float(top["state_teacher_share"].sum()),
                "q1q3_units": int(top["target"].isin(["Q1", "Q3"]).sum()),
                "q2s3_units": int(top["target"].isin(["Q2", "S3"]).sum()),
                "profile": ",".join(
                    f"{t}:{int(v)}"
                    for t, v in top["target"].value_counts().reindex(TARGETS, fill_value=0).items()
                    if int(v) > 0
                ),
            }
        )
    return unit, state, pd.DataFrame(rows)


def quantile_mask(values: np.ndarray, frac: float) -> np.ndarray:
    flat = np.asarray(values, dtype=np.float64).reshape(-1)
    k = max(1, int(np.ceil(len(flat) * frac)))
    cut = np.partition(flat, len(flat) - k)[len(flat) - k]
    return values >= cut


def target_mask(n_rows: int, idxs: list[int]) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    mask[:, idxs] = True
    return mask


def normalize_unit(unit: np.ndarray, mask: np.ndarray, shape: str) -> np.ndarray:
    selected = np.asarray(mask, dtype=bool) & np.isfinite(unit)
    out = np.zeros_like(unit, dtype=np.float64)
    if not selected.any():
        return out
    raw = np.asarray(unit, dtype=np.float64)
    if shape == "raw":
        shaped = raw
    elif shape == "sqrt":
        shaped = np.sign(raw) * np.sqrt(np.abs(raw))
    elif shape == "sign":
        shaped = np.sign(raw)
    else:
        raise KeyError(shape)
    denom = float(np.mean(np.abs(shaped[selected])))
    if denom <= 1.0e-15:
        return out
    out[selected] = shaped[selected] / denom
    return out


def build_state_masks(state: np.ndarray) -> list[dict[str, Any]]:
    masks: list[dict[str, Any]] = []
    target_masks = {
        "all": np.ones_like(state, dtype=bool),
        "non_q2s3": ~target_mask(state.shape[0], Q2S3),
        "s_all": target_mask(state.shape[0], S_ALL),
        "q1q3_sall": target_mask(state.shape[0], [TARGETS.index("Q1"), TARGETS.index("Q3"), *S_ALL]),
    }
    seen: set[bytes] = set()
    for frac in STATE_FRACS:
        top = quantile_mask(state, frac)
        for scope, scope_mask in target_masks.items():
            hard = top & scope_mask
            if not hard.any():
                continue
            key = hard.tobytes()
            if key not in seen:
                seen.add(key)
                masks.append(
                    {
                        "mask_name": f"state_top{int(frac * 100)}_{scope}_hard",
                        "mask": hard.astype(float),
                        "mask_kind": "hard",
                        "state_frac": frac,
                        "scope": scope,
                    }
                )
            soft = hard.astype(float) * state
            if float(np.abs(soft).mean()) > 1.0e-15:
                key = np.round(soft, 9).tobytes()
                if key not in seen:
                    seen.add(key)
                    masks.append(
                        {
                            "mask_name": f"state_top{int(frac * 100)}_{scope}_soft",
                            "mask": soft,
                            "mask_kind": "soft",
                            "state_frac": frac,
                            "scope": scope,
                        }
                    )
    return masks


def build_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    state: np.ndarray,
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], pd.DataFrame]:
    e95_logit = logit(refs["e95"])
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen_pred: dict[str, int] = {}
    for name in ["mixmin", "e95", "e101", "e85", "e86", "e90"]:
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
    masks = build_state_masks(state)
    risk_sign = e132.risk_signs(tail_state)
    risk_weight = 1.00 * state + 0.25 * np.ones_like(state)
    diag_rows: list[dict[str, Any]] = []
    for context in CONTEXTS:
        grad = e132.gradient_for_context(sample, refs["e95"], context)
        unit_seed = -grad
        diag_rows.append(
            {
                "context": context,
                "grad_mean_abs": float(np.mean(np.abs(grad))),
                "grad_max_abs": float(np.max(np.abs(grad))),
                "risk_scalar_raw_unit": e132.risk_scalar(unit_seed, risk_sign, risk_weight),
            }
        )
        for mask_rec in masks:
            mask_weight = np.asarray(mask_rec["mask"], dtype=np.float64)
            hard = mask_weight > 1.0e-12
            if not hard.any():
                continue
            for shape in SHAPES:
                shaped = normalize_unit(unit_seed * mask_weight, hard, shape)
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
                            "strategy": "blocktarget_gradient",
                            "context": context,
                            "mask_name": mask_rec["mask_name"],
                            "mask_kind": mask_rec["mask_kind"],
                            "scope": mask_rec["scope"],
                            "state_frac": float(mask_rec["state_frac"]),
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
    return pd.DataFrame(rows), preds, pd.DataFrame(diag_rows)


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("blocktarget_gradient")].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["context", "scope", "mask_kind", "state_frac", "shape"]
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
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["submit_gate", "local_and_veto", "strict", "best_sensor_mean_vs_e95", "best_all_minus_e95"],
        ascending=[False, False, False, True, True],
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[
        scan["strategy"].eq("blocktarget_gradient")
        & scan["strict_gate"].fillna(False).astype(bool)
        & scan["gate_strict_actionable"].fillna(False).astype(bool)
        & scan["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & scan["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & scan["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & scan["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()
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
    state_summary: pd.DataFrame,
    gradient_diag: pd.DataFrame,
    transfer: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].eq("blocktarget_gradient")].copy()
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    submit = local_and_veto[
        local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & local_and_veto["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()
    row_cols = [
        "context",
        "mask_name",
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
        else "No submission. E136 block-target state did not create a candidate that is simultaneously local-strict, transfer-veto-actionable, and post-E101 favorable under current E95 gradients."
    )
    lines = [
        "# E137 Block-Target State Movement Probe",
        "",
        "## Question",
        "",
        "E136 made the safe remainder visible after block-target compression. This experiment asks whether that visible state can actually generate an E95-neighborhood probability movement when used as a gate on donor-free E95 combo gradients.",
        "",
        "## Counts",
        "",
        f"- candidate rows: `{len(scan)}`",
        f"- block-target gradient variants: `{len(variants)}`",
        f"- evaluated variants: `{len(evaluated)}`",
        f"- local strict variants: `{len(strict)}`",
        f"- transfer-veto-actionable variants: `{len(veto)}`",
        f"- local-strict plus transfer-veto-actionable variants: `{len(local_and_veto)}`",
        f"- final submit-gate variants: `{len(submit)}`",
        f"- transfer rows: `{len(transfer)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## E136 State Summary",
        "",
        md_table(state_summary, ".9f"),
        "",
        "## Gradient Diagnostics",
        "",
        md_table(gradient_diag, ".9f"),
        "",
        "## Summary",
        "",
        md_table(summary.head(60), ".9f"),
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
    _unit, state, state_summary = load_blocktarget_state(cell)
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    _masks, density = e130.build_density_masks(sample, refs)
    rows, preds, gradient_diag = build_candidates(sample, refs, state, tail_state)
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
    state_summary.to_csv(STATE_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, state_summary, gradient_diag, transfer, submission_path)

    variants = scan[scan["strategy"].eq("blocktarget_gradient")]
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)]
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)]
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)]
    submit = local_and_veto[
        local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & local_and_veto["all_minus_base"].lt(-MATERIAL_FLOOR)
    ]
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
