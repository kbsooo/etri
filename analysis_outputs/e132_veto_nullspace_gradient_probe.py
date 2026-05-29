#!/usr/bin/env python3
"""E132 veto-nullspace gradient probe.

SAUNA question:
E130/E131 showed that old-donor density movements cannot place local upside
inside the post-E101 transfer-shrinkage safety region. This probe removes the
donor constraint. It asks whether the E95 local pseudo-public gradient itself
has a component inside the separated E72/E101 veto nullspace.

The experiment builds small logit movements directly from combo-set gradients
at E95, then masks them by transfer-shrinkage and hard-tail safety fields. No
public labels are fitted. A submission is written only if a donor-free gradient
candidate beats E95 locally, passes separated vetoes, and survives post-E101
sensor stress.
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import q2_s3_tail_gate_independence_probe as e68  # noqa: E402


SCAN_OUT = OUT / "e132_veto_nullspace_gradient_probe_scan.csv"
SUMMARY_OUT = OUT / "e132_veto_nullspace_gradient_probe_summary.csv"
TRANSFER_OUT = OUT / "e132_veto_nullspace_gradient_probe_transfer.csv"
REPORT_OUT = OUT / "e132_veto_nullspace_gradient_probe_report.md"
SUBMISSION_PREFIX = "submission_e132_gradnull"

EPS = 1.0e-6
ACTIVE_SCALES = [0.0025, 0.0050, 0.0100, 0.0200, 0.0400]
TOP_QUANTILES = [0.50, 0.70, 0.85, 0.93]
MATERIAL_FLOOR = 1.0e-7

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
    tag = e83.stable_tag(pred, f"e132_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def normalize_nonzero(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    out = np.zeros_like(arr)
    valid = np.isfinite(arr)
    if not valid.any():
        return out
    lo = float(np.min(arr[valid]))
    hi = float(np.max(arr[valid]))
    if hi <= lo + 1.0e-15:
        out[valid] = 0.0
    else:
        out[valid] = (arr[valid] - lo) / (hi - lo)
    return out


def quantile_mask(values: np.ndarray, q: float, base: np.ndarray | None = None, high: bool = True) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    mask = np.ones_like(arr, dtype=bool) if base is None else np.asarray(base, dtype=bool)
    valid = mask & np.isfinite(arr)
    if not valid.any():
        return np.zeros_like(arr, dtype=bool)
    cut = float(np.quantile(arr[valid], q))
    return valid & (arr >= cut if high else arr <= cut)


def target_mask(n_rows: int, idxs: list[int]) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    mask[:, idxs] = True
    return mask


def risk_signs(tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    _, _, wrong_is_zero, wrong_is_one = tail_state
    return wrong_is_zero.astype(float) - wrong_is_one.astype(float)


def weighted_adverse(delta: np.ndarray, risk_sign: np.ndarray, weight: np.ndarray) -> np.ndarray:
    return np.maximum(np.asarray(delta, dtype=np.float64) * risk_sign, 0.0) * weight


def risk_scalar(delta: np.ndarray, risk_sign: np.ndarray, weight: np.ndarray) -> float:
    adverse = weighted_adverse(delta, risk_sign, weight)
    den = float(np.sum(weight))
    if den <= 0.0:
        return float(np.mean(adverse))
    return float(np.sum(adverse) / den)


def gradient_for_context(sample: pd.DataFrame, base: np.ndarray, context_name: str) -> np.ndarray:
    combo_sets = list(e68.COMBO_TABLES.keys())
    if context_name.startswith("loo_"):
        heldout = context_name.removeprefix("loo_")
        train_sets = [name for name in combo_sets if name != heldout]
    elif context_name == "all":
        train_sets = combo_sets
    else:
        train_sets = [context_name]
    grads, weights = e68.anchor_gradient_for_sets(sample, base, train_sets)
    return np.einsum("i,irt->rt", weights, grads)


def build_masks(
    unit: np.ndarray,
    density: dict[str, np.ndarray],
    risk_sign: np.ndarray,
    risk_weight: np.ndarray,
) -> list[dict[str, Any]]:
    n_rows = unit.shape[0]
    abs_unit = np.abs(unit)
    q2s3 = density["q2s3"].astype(bool)
    e101_active = density["e101_active"].astype(bool)
    null = unit * risk_sign <= 1.0e-15
    non_active = ~e101_active
    non_q2s3 = ~q2s3
    s_all = target_mask(n_rows, S_ALL)
    adverse = weighted_adverse(unit, risk_sign, risk_weight)
    low_adverse75 = quantile_mask(adverse, 0.75, high=False)
    tail_hi = quantile_mask(density["tail_equal"], 0.70)
    low_alpha_hi = quantile_mask(density["low_alpha"], 0.70)
    density_hi = quantile_mask(density["density_score"], 0.70)

    base_masks = {
        "all": np.ones_like(null, dtype=bool),
        "veto_null": null,
        "veto_null_nonactive": null & non_active,
        "veto_null_nonq2s3": null & non_q2s3,
        "veto_null_s_all": null & s_all,
        "veto_null_tail70": null & tail_hi,
        "veto_null_lowalpha70": null & low_alpha_hi,
        "veto_null_density70": null & density_hi,
        "low_adverse75": low_adverse75,
        "low_adverse75_nonactive": low_adverse75 & non_active,
        "low_adverse75_nonq2s3": low_adverse75 & non_q2s3,
    }

    masks: list[dict[str, Any]] = []
    seen: set[bytes] = set()
    for scope, base in base_masks.items():
        for q in TOP_QUANTILES:
            selected = quantile_mask(abs_unit, q, base=base, high=True)
            if int(selected.sum()) == 0:
                continue
            key = selected.tobytes()
            if key in seen:
                continue
            seen.add(key)
            masks.append({"mask_name": f"{scope}_top{int(q * 100)}", "mask": selected, "scope": scope, "top_q": q})
    return masks


def normalize_unit(unit: np.ndarray, mask: np.ndarray, mode: str) -> np.ndarray:
    selected = np.asarray(mask, dtype=bool) & np.isfinite(unit)
    out = np.zeros_like(unit, dtype=np.float64)
    if not selected.any():
        return out
    raw = np.asarray(unit, dtype=np.float64)
    if mode == "raw":
        shaped = raw
    elif mode == "sign":
        shaped = np.sign(raw)
    elif mode == "sqrt":
        shaped = np.sign(raw) * np.sqrt(np.abs(raw))
    else:
        raise KeyError(mode)
    denom = float(np.mean(np.abs(shaped[selected])))
    if denom <= 1.0e-15:
        return out
    out[selected] = shaped[selected] / denom
    return out


def build_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], pd.DataFrame]:
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
    e95_logit = logit(refs["e95"])
    risk_sign = risk_signs(tail_state)
    risk_weight = (
        1.00 * density["plausible"]
        + 0.75 * density["e101_active"]
        + 0.50 * density["q2s3"]
        + 0.25 * density["tail_equal"]
    )

    contexts = ["all", *[f"loo_{name}" for name in e68.COMBO_TABLES.keys()], *list(e68.COMBO_TABLES.keys())]
    diag_rows: list[dict[str, Any]] = []
    for context in contexts:
        grad = gradient_for_context(sample, refs["e95"], context)
        unit_seed = -grad
        context_risk = risk_scalar(unit_seed, risk_sign, risk_weight)
        masks = build_masks(unit_seed, density, risk_sign, risk_weight)
        diag_rows.append(
            {
                "context": context,
                "grad_mean_abs": float(np.mean(np.abs(grad))),
                "grad_max_abs": float(np.max(np.abs(grad))),
                "raw_unit_risk_scalar": context_risk,
                "masks": int(len(masks)),
            }
        )
        for mask_rec in masks:
            mask = np.asarray(mask_rec["mask"], dtype=bool)
            selected = int(mask.sum())
            if selected <= 0:
                continue
            for shape in ["raw", "sqrt", "sign"]:
                shaped = normalize_unit(unit_seed, mask, shape)
                if float(np.abs(shaped).mean()) <= 1.0e-14:
                    continue
                for scale in ACTIVE_SCALES:
                    delta = float(scale) * shaped
                    pred = clip_prob(sigmoid(e95_logit + delta))
                    add_pred(
                        rows,
                        preds,
                        seen_pred,
                        pred,
                        {
                            "strategy": "gradient_nullspace",
                            "context": context,
                            "mask_name": mask_rec["mask_name"],
                            "scope": mask_rec["scope"],
                            "top_q": float(mask_rec["top_q"]),
                            "shape": shape,
                            "scale": float(scale),
                            "selected_cells": selected,
                            "selected_rows": int(mask.any(axis=1).sum()),
                            "selected_q2s3_cells": int(mask[:, Q2S3].sum()),
                            "selected_s_cells": int(mask[:, S_ALL].sum()),
                            "unit_mean_abs_logit_active": 1.0,
                            "unit_mean_abs_logit_global": float(np.mean(np.abs(shaped))),
                            "unit_max_abs_logit": float(np.max(np.abs(shaped))),
                            "risk_scalar_unit": risk_scalar(shaped, risk_sign, risk_weight),
                            "risk_scalar_scaled": risk_scalar(delta, risk_sign, risk_weight),
                        },
                        base_index=e95_index,
                    )
    return pd.DataFrame(rows), preds, pd.DataFrame(diag_rows)


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("gradient_nullspace")].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["context", "scope", "shape"]
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
        scan["strategy"].eq("gradient_nullspace")
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
    gradient_diag: pd.DataFrame,
    transfer: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].eq("gradient_nullspace")].copy()
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
        else "No submission. Donor-free local gradients did not create a candidate that is simultaneously local-strict, transfer-veto-actionable, and post-E101 favorable."
    )
    lines = [
        "# E132 Veto-Nullspace Gradient Probe",
        "",
        "## Question",
        "",
        "After E130/E131 closed old-donor density movement and local+safe correction, does the E95 local combo-set gradient itself contain a transfer-veto-safe component?",
        "",
        "## Method",
        "",
        "- Compute pseudo-public combo-set BCE gradients at E95.",
        "- Recompute gradients for all combo sets, leave-one-combo-set contexts, and single combo-set contexts.",
        "- Keep only top-gradient cells under transfer-shrinkage, E72 hard-tail, E101-active, Q2/S3, and density masks.",
        "- Generate small donor-free logit movements from E95.",
        "- Score candidates against E95-relative local stress, separated E128/E129 vetoes, and post-E101 transfer filters.",
        "",
        "## Counts",
        "",
        f"- candidate rows: `{len(scan)}`",
        f"- gradient candidates: `{len(variants)}`",
        f"- evaluated candidates: `{len(evaluated)}`",
        f"- local strict candidates: `{len(strict)}`",
        f"- veto-actionable candidates: `{len(veto)}`",
        f"- local-strict plus veto-actionable candidates: `{len(local_and_veto)}`",
        f"- final submit-gate candidates: `{len(submit)}`",
        f"- transfer rows: `{len(transfer)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
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
        "## Local Strict Plus Veto-Actionable Candidates",
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
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    _masks, density = e130.build_density_masks(sample, refs)
    rows, preds, gradient_diag = build_candidates(sample, refs, density, tail_state)
    labels, worlds, views, state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, state)
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
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, gradient_diag, transfer, submission_path)

    variants = scan[scan["strategy"].eq("gradient_nullspace")]
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
            "best_sensor_mean_vs_e95": float(
                evaluated["post101_mean_vs_e95_e101_sensor"].min()
            )
            if len(evaluated)
            else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(20).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
