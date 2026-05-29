#!/usr/bin/env python3
"""E130 E95-neighborhood tail-density synthesis probe.

SAUNA question:
E129 closed the documented/local submission universe: separated E128 vetoes do
not reveal a novel old file. The next cheap falsifier is whether the E127
transfer-shrinkage field can synthesize a new E95-neighborhood movement, rather
than merely rank existing files.

No public labels are fitted and no submission is produced unless a non-control
candidate simultaneously beats E95 under local stress, E128/E129-style vetoes,
and post-E101 tail-transfer stress.
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
import e96_public_miss_budget_tail_scenarios as e96mod  # noqa: E402
import e124_e101_conditioned_tail_transfer as e124mod  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


CELL_IN = OUT / "e127_transfer_shrinkage_cell_summary.csv"
SCAN_OUT = OUT / "e130_tail_density_synthesis_probe_scan.csv"
SUMMARY_OUT = OUT / "e130_tail_density_synthesis_probe_summary.csv"
TRANSFER_OUT = OUT / "e130_tail_density_synthesis_probe_transfer.csv"
REPORT_OUT = OUT / "e130_tail_density_synthesis_probe_report.md"
SUBMISSION_PREFIX = "submission_e130_taildensity"

MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E85_FILE = "submission_e85_inverse_conflict_pruned_58b23ed1.csv"
E86_FILE = "submission_e86_e85_consensus_a3f7c96f.csv"
E89_FILE = "submission_e89_e72decontam_00d7807f.csv"
E90_FILE = "submission_e90_e72pareto_28925de5.csv"
NOQ2_FILE = "submission_e87_noq2_source_consensus_a85c4e39.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"

EPS = 1.0e-6
Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
S2 = TARGETS.index("S2")
S3 = TARGETS.index("S3")
Q2S3 = [Q2, S3]
S123 = [S1, S2, S3]
S_ALL = [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"]]

SOURCES = ["e86", "e90", "e89", "e85", "noq2", "mixmin"]
ALPHAS = [0.25, 0.50, 0.75, 1.00]
QUANTILES = [0.70, 0.85]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


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


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def load_refs(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "mixmin": load_pred(MIXMIN_FILE, sample),
        "failed_e72": load_pred(E72_FILE, sample),
        "e85": load_pred(E85_FILE, sample),
        "e86": load_pred(E86_FILE, sample),
        "e89": load_pred(E89_FILE, sample),
        "e90": load_pred(E90_FILE, sample),
        "noq2": load_pred(NOQ2_FILE, sample),
        "e95": load_pred(E95_FILE, sample),
        "e101": load_pred(E101_FILE, sample),
    }


def normalize_nonzero(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    out = np.zeros_like(arr, dtype=np.float64)
    finite = np.isfinite(arr)
    if not finite.any():
        return out
    lo = float(np.nanmin(arr[finite]))
    hi = float(np.nanmax(arr[finite]))
    if hi <= lo + 1.0e-15:
        out[finite] = 0.0
    else:
        out[finite] = (arr[finite] - lo) / (hi - lo)
    return out


def cell_array(cell: pd.DataFrame, col: str, n_rows: int, dtype: Any = float) -> np.ndarray:
    arr = np.zeros((n_rows, len(TARGETS)), dtype=dtype)
    target_to_idx = {target: idx for idx, target in enumerate(TARGETS)}
    for rec in cell[["sub_idx", "target", col]].to_dict("records"):
        arr[int(rec["sub_idx"]), target_to_idx[str(rec["target"])]] = rec[col]
    return arr


def target_mask(n_rows: int, idxs: list[int]) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    mask[:, idxs] = True
    return mask


def quantile_mask(values: np.ndarray, q: float, base_mask: np.ndarray | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    base = np.ones_like(arr, dtype=bool) if base_mask is None else np.asarray(base_mask, dtype=bool)
    valid = base & np.isfinite(arr)
    if int(valid.sum()) == 0:
        return np.zeros_like(arr, dtype=bool)
    cut = float(np.quantile(arr[valid], q))
    return valid & (arr >= cut)


def low_quantile_mask(values: np.ndarray, q: float, base_mask: np.ndarray | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    base = np.ones_like(arr, dtype=bool) if base_mask is None else np.asarray(base_mask, dtype=bool)
    valid = base & np.isfinite(arr)
    if int(valid.sum()) == 0:
        return np.zeros_like(arr, dtype=bool)
    cut = float(np.quantile(arr[valid], q))
    return valid & (arr <= cut)


def build_density_masks(sample: pd.DataFrame, refs: dict[str, np.ndarray]) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    cell = pd.read_csv(CELL_IN)
    n_rows = len(sample)
    if len(cell) != n_rows * len(TARGETS):
        raise ValueError(f"cell table shape mismatch: {len(cell)} rows for sample={n_rows}")

    tail_equal = cell_array(cell, "broad_tail_equal_share", n_rows, float)
    low_alpha = cell_array(cell, "broad_low_alpha_share", n_rows, float)
    plausible = cell_array(cell, "e101_plausible_share", n_rows, float)
    e101_active = cell_array(cell, "e101_active", n_rows, bool)
    q2s3 = cell_array(cell, "target_is_q2s3", n_rows, bool)
    e72_pos = cell_array(cell, "e72_pos", n_rows, float)

    e95_moved = np.abs(logit(refs["e95"]) - logit(refs["mixmin"])) > 1.0e-9
    e95_fallback = np.abs(logit(refs["e95"]) - logit(refs["e86"])) > 1.0e-9

    density_score = (
        normalize_nonzero(tail_equal)
        + normalize_nonzero(low_alpha)
        + 0.75 * normalize_nonzero(plausible)
        - 0.75 * q2s3.astype(float)
        - 0.60 * e101_active.astype(float)
        - 0.25 * normalize_nonzero(e72_pos)
    )

    scopes = {
        "all": np.ones((n_rows, len(TARGETS)), dtype=bool),
        "s_all": target_mask(n_rows, S_ALL),
        "non_q2s3": ~q2s3,
        "e95_moved": e95_moved,
        "e95_fallback": e95_fallback,
    }
    base_fields = {
        "tail_equal": tail_equal,
        "low_alpha": low_alpha,
        "density_score": density_score,
    }

    masks: list[dict[str, Any]] = []
    seen: set[bytes] = set()
    for field_name, values in base_fields.items():
        for scope_name, scope_mask in scopes.items():
            for q in QUANTILES:
                hard = quantile_mask(values, q, scope_mask)
                for modifier_name, modifier in [
                    ("raw", np.ones_like(hard, dtype=bool)),
                    ("nonactive_low_e72", (~e101_active) & low_quantile_mask(e72_pos, 0.70)),
                ]:
                    final = hard & modifier
                    if int(final.sum()) == 0:
                        continue
                    key = final.tobytes()
                    if key in seen:
                        continue
                    seen.add(key)
                    masks.append(
                        {
                            "mask_name": f"{field_name}_{scope_name}_q{q:.2f}_{modifier_name}",
                            "mask": final.astype(float),
                            "mask_kind": "hard",
                            "field": field_name,
                            "scope": scope_name,
                            "quantile": q,
                            "modifier": modifier_name,
                        }
                    )

                soft_base = hard & (~e101_active)
                if int(soft_base.sum()) > 0:
                    soft = normalize_nonzero(np.maximum(values, 0.0)) * soft_base.astype(float)
                    key = np.round(soft, 9).tobytes()
                    if key not in seen and float(np.abs(soft).mean()) > 1.0e-12:
                        seen.add(key)
                        masks.append(
                            {
                                "mask_name": f"{field_name}_{scope_name}_q{q:.2f}_soft_nonactive",
                                "mask": soft,
                                "mask_kind": "soft",
                                "field": field_name,
                                "scope": scope_name,
                                "quantile": q,
                                "modifier": "soft_nonactive",
                            }
                        )

    return masks, {
        "tail_equal": tail_equal,
        "low_alpha": low_alpha,
        "plausible": plausible,
        "e101_active": e101_active.astype(float),
        "q2s3": q2s3.astype(float),
        "e72_pos": e72_pos,
        "density_score": density_score,
    }


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
    tag = e83.stable_tag(pred, f"e130_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def build_candidates(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], list[dict[str, Any]], dict[str, np.ndarray]]:
    masks, density = build_density_masks(sample, refs)
    e95_logit = logit(refs["e95"])

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen_pred: dict[str, int] = {}

    # Stable control indexes. Candidate rows use E95 as base so local stress is
    # directly E95-relative, while E95 itself is kept as a mixmin-reference row.
    for name in ["mixmin", "e95", "e101", "e85", "e86", "e89", "e90", "noq2"]:
        base_index = 0 if name in {"mixmin", "e95"} else 1
        add_pred(
            rows,
            preds,
            seen_pred,
            refs[name],
            {"strategy": "control", "source": name, "mask_name": "", "alpha": np.nan},
            base_index=base_index,
        )
    e95_index = seen_pred[pred_key(refs["e95"])]

    for source in SOURCES:
        direction = logit(refs[source]) - e95_logit
        if float(np.abs(direction).mean()) <= 1.0e-14:
            continue
        for mask_rec in masks:
            mask = np.asarray(mask_rec["mask"], dtype=np.float64)
            unit = direction * mask
            if float(np.abs(unit).mean()) <= 1.0e-14:
                continue
            active = np.abs(unit) > 1.0e-12
            for alpha in ALPHAS:
                pred = clip_prob(sigmoid(e95_logit + float(alpha) * unit))
                add_pred(
                    rows,
                    preds,
                    seen_pred,
                    pred,
                    {
                        "strategy": "density_synth",
                        "source": source,
                        "mask_name": mask_rec["mask_name"],
                        "mask_kind": mask_rec["mask_kind"],
                        "field": mask_rec["field"],
                        "scope": mask_rec["scope"],
                        "quantile": mask_rec["quantile"],
                        "modifier": mask_rec["modifier"],
                        "alpha": float(alpha),
                        "selected_cells": int(np.sum(mask > 1.0e-12)),
                        "selected_rows": int(np.any(mask > 1.0e-12, axis=1).sum()),
                        "active_cells": int(active.sum()),
                        "active_rows": int(active.any(axis=1).sum()),
                        "active_q2s3_cells": int(active[:, Q2S3].sum()),
                        "active_s_cells": int(active[:, S_ALL].sum()),
                        "unit_mean_abs_logit": float(np.abs(unit).mean()),
                        "unit_max_abs_logit": float(np.abs(unit).max()),
                    },
                    base_index=e95_index,
                )

    return pd.DataFrame(rows), preds, masks, density


def normalize_weight(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    arr = np.where(np.isfinite(arr), np.maximum(arr, 0.0), 0.0)
    total = float(arr.sum())
    if total <= 0.0:
        return np.ones_like(arr) / len(arr)
    return arr / total


def weighted_l1(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sum(normalize_weight(weights) * np.abs(np.asarray(values, dtype=np.float64).reshape(-1))))


def weighted_rmse(values: np.ndarray, weights: np.ndarray) -> float:
    flat = np.asarray(values, dtype=np.float64).reshape(-1)
    return float(np.sqrt(np.sum(normalize_weight(weights) * flat * flat)))


def weighted_cosine(a: np.ndarray, b: np.ndarray, weights: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    ww = normalize_weight(weights)
    den = float(np.sqrt(np.sum(ww * aa * aa) * np.sum(ww * bb * bb)))
    if den <= 1.0e-15:
        return 0.0
    return float(np.sum(ww * aa * bb) / den)


def weighted_resid_ratio(a: np.ndarray, b: np.ndarray, weights: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    ww = normalize_weight(weights)
    den = float(np.sqrt(np.sum(ww * bb * bb)))
    if den <= 1.0e-15:
        return np.nan
    return float(np.sqrt(np.sum(ww * (aa - bb) ** 2)) / den)


def add_tail_and_veto_metrics(
    scan: pd.DataFrame,
    preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> pd.DataFrame:
    _, e72_weight, wrong_is_zero, wrong_is_one = tail_state
    mixmin = refs["mixmin"]
    e95 = refs["e95"]
    e101 = refs["e101"]
    law = logit(e95) - logit(mixmin)
    flat_weights = {
        "tail_equal": density["tail_equal"].reshape(-1),
        "e101_plausible": density["plausible"].reshape(-1),
        "q2s3": density["q2s3"].reshape(-1),
        "e101_active": density["e101_active"].reshape(-1),
    }

    e95_tail = e95mod.hard_tail_metrics(e95, mixmin, e72_weight, wrong_is_zero, wrong_is_one)
    e95_adverse = np.maximum(
        e96mod.adverse_delta_for_e72_direction(e95, mixmin, wrong_is_zero, wrong_is_one),
        0.0,
    )
    e95_tail["e72_adverse_exposure_e101_plausible"] = weighted_l1(
        e95_adverse, flat_weights["e101_plausible"]
    )
    threshold_pred_metrics: dict[str, float] = {}
    for ref_name, ref_pred in {"e95": e95, "e101": e101}.items():
        move_mix = logit(ref_pred) - logit(mixmin)
        move_e95 = logit(ref_pred) - logit(e95)
        threshold_pred_metrics[f"{ref_name}_e101_active_delta95_l1"] = weighted_l1(
            move_e95, flat_weights["e101_active"]
        )
        threshold_pred_metrics[f"{ref_name}_q2s3_delta95_l1"] = weighted_l1(move_e95, flat_weights["q2s3"])
        threshold_pred_metrics[f"{ref_name}_mean_abs_logit_move_vs_e95"] = float(np.mean(np.abs(move_e95)))
        threshold_pred_metrics[f"{ref_name}_tail_equal_law_cosine"] = weighted_cosine(
            move_mix, law, flat_weights["tail_equal"]
        )
        threshold_pred_metrics[f"{ref_name}_tail_equal_law_resid_ratio"] = weighted_resid_ratio(
            move_mix, law, flat_weights["tail_equal"]
        )

    rows: list[dict[str, Any]] = []
    for idx, pred in enumerate(preds):
        move_mix = logit(pred) - logit(mixmin)
        move_e95 = logit(pred) - logit(e95)
        move_e101 = logit(pred) - logit(e101)
        tail = e95mod.hard_tail_metrics(pred, mixmin, e72_weight, wrong_is_zero, wrong_is_one)
        adverse = np.maximum(
            e96mod.adverse_delta_for_e72_direction(pred, mixmin, wrong_is_zero, wrong_is_one),
            0.0,
        )
        row: dict[str, Any] = {
            "pred_index": idx,
            **tail,
            "e72_adverse_exposure_e101_plausible": weighted_l1(adverse, flat_weights["e101_plausible"]),
            "e72_adverse_exposure_tail_equal": weighted_l1(adverse, flat_weights["tail_equal"]),
            "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move_e95))),
            "max_abs_logit_move_vs_e95": float(np.max(np.abs(move_e95))),
            "changed_cells_vs_e95": int(np.sum(np.abs(move_e95) > 1.0e-9)),
            "changed_rows_vs_e95": int(np.sum((np.abs(move_e95) > 1.0e-9).any(axis=1))),
            "tail_equal_law_cosine": weighted_cosine(move_mix, law, flat_weights["tail_equal"]),
            "tail_equal_law_resid_ratio": weighted_resid_ratio(move_mix, law, flat_weights["tail_equal"]),
            "tail_equal_delta95_l1": weighted_l1(move_e95, flat_weights["tail_equal"]),
            "tail_equal_delta101_l1": weighted_l1(move_e101, flat_weights["tail_equal"]),
            "e101_active_delta95_l1": weighted_l1(move_e95, flat_weights["e101_active"]),
            "q2s3_delta95_l1": weighted_l1(move_e95, flat_weights["q2s3"]),
            "e101_plausible_delta95_l1": weighted_l1(move_e95, flat_weights["e101_plausible"]),
            "e95rel_rmse_tail_equal": weighted_rmse(move_e95, flat_weights["tail_equal"]),
        }
        row["transfer_shrinkage_risk_index"] = (
            row["e101_active_delta95_l1"]
            + row["q2s3_delta95_l1"]
            + 0.5 * row["e72_adverse_exposure_e101_plausible"]
            - row["tail_equal_law_cosine"]
            if "e72_adverse_exposure_e101_plausible" in row
            else np.nan
        )
        rows.append(row)

    metrics = pd.DataFrame(rows)
    metrics["gate_cos95_resid025"] = (
        metrics["tail_equal_law_cosine"].ge(0.95) & metrics["tail_equal_law_resid_ratio"].le(0.25)
    )
    metrics["gate_active_q2s3_not_more_than_e101"] = (
        metrics["e101_active_delta95_l1"].le(threshold_pred_metrics["e101_e101_active_delta95_l1"] + 1.0e-12)
        & metrics["q2s3_delta95_l1"].le(threshold_pred_metrics["e101_q2s3_delta95_l1"] + 1.0e-12)
    )
    metrics["gate_e72_not_more_than_e95"] = metrics["e72_adverse_exposure_e101_plausible"].le(
        float(e95_tail["e72_adverse_exposure_e101_plausible"]) + 1.0e-12
    )
    metrics["gate_material_vs_e95"] = (
        metrics["mean_abs_logit_move_vs_e95"].ge(
            threshold_pred_metrics["e101_mean_abs_logit_move_vs_e95"] - 1.0e-12
        )
        & metrics["changed_cells_vs_e95"].gt(0)
    )
    metrics["gate_strict_veto"] = (
        metrics["gate_cos95_resid025"]
        & metrics["gate_active_q2s3_not_more_than_e101"]
        & metrics["gate_e72_not_more_than_e95"]
    )
    metrics["gate_strict_actionable"] = metrics["gate_strict_veto"] & metrics["gate_material_vs_e95"]

    duplicate_cols = [c for c in metrics.columns if c != "pred_index" and c in scan.columns]
    return scan.merge(metrics.drop(columns=duplicate_cols), on="pred_index", how="left")


def post_e101_transfer_summary(
    sample: pd.DataFrame,
    scan: pd.DataFrame,
    preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> pd.DataFrame:
    e72_delta, _, wrong_is_zero, wrong_is_one = tail_state
    candidate_indexes = sorted(
        set(
            scan.loc[
                scan["nonanchor_evaluated"].fillna(False).astype(bool)
                | scan["strategy"].eq("control")
                | scan["strict_gate"].fillna(False).astype(bool),
                "pred_index",
            ].astype(int)
        )
    )
    if not candidate_indexes:
        return pd.DataFrame()

    e124 = pd.read_csv(e124mod.SCENARIO_OUT)
    context_cols = [
        "scenario_id",
        "alpha",
        "lambda",
        "is_broad_plausible",
        "is_tight_plausible",
        "e101_order_match",
        "e101_sensor_plausible",
    ]
    context = e124[context_cols].copy()

    adverse = {
        f"p{idx}": e96mod.adverse_delta_for_e72_direction(
            preds[idx], refs["mixmin"], wrong_is_zero, wrong_is_one
        )
        for idx in candidate_indexes
    }
    e72_pos = np.maximum(
        e96mod.adverse_delta_for_e72_direction(refs["failed_e72"], refs["mixmin"], wrong_is_zero, wrong_is_one),
        0.0,
    )
    masks = e96mod.build_masks(
        {
            "mixmin": refs["mixmin"],
            "failed_e72": refs["failed_e72"],
            "e85": refs["e85"],
            "e86": refs["e86"],
            "noq2": refs["noq2"],
            "e90": refs["e90"],
            "e89": refs["e89"],
            "e95": refs["e95"],
        },
        e72_pos,
        e72_delta,
    )
    _, long = e96mod.build_scenarios(
        e72_pos.reshape(-1),
        masks,
        {name: arr.reshape(-1) for name, arr in adverse.items()},
        float(e124mod.OBS_DELTA["failed_e72"] * refs["mixmin"].size),
        int(refs["mixmin"].size),
    )
    wide = long.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    detail = context.set_index("scenario_id").join(wide, how="inner").reset_index()

    local_delta = (
        scan.sort_values(["all_delta_vs_mixmin", "all_minus_base"], ascending=[True, True])
        .drop_duplicates("pred_index")
        .set_index("pred_index")["all_delta_vs_mixmin"]
        .astype(float)
        .to_dict()
    )
    row_meta = scan.drop_duplicates("pred_index").set_index("pred_index")
    filters = {
        "broad": lambda x: x["is_broad_plausible"].astype(bool),
        "tight": lambda x: x["is_tight_plausible"].astype(bool),
        "e101_order": lambda x: x["is_broad_plausible"].astype(bool) & x["e101_order_match"].astype(bool),
        "e101_sensor": lambda x: x["e101_sensor_plausible"].astype(bool),
    }

    rows: list[dict[str, Any]] = []
    for idx in candidate_indexes:
        col = f"p{idx}"
        if col not in detail.columns:
            continue
        meta = row_meta.loc[idx]
        for filter_name, fn in filters.items():
            subset = detail[fn(detail)].copy()
            if subset.empty:
                continue
            pred_delta = subset["alpha"].astype(float) * float(local_delta[idx]) + subset["lambda"].astype(float) * subset[col].astype(float)
            vs_e95 = pred_delta - e124mod.OBS_DELTA["e95"]
            rows.append(
                {
                    "pred_index": idx,
                    "filter": filter_name,
                    "n_scenarios": int(len(subset)),
                    "tag": str(meta.get("tag", "")),
                    "strategy": str(meta.get("strategy", "")),
                    "source": str(meta.get("source", "")),
                    "mask_name": str(meta.get("mask_name", "")),
                    "alpha": float(meta.get("alpha", np.nan)) if pd.notna(meta.get("alpha", np.nan)) else np.nan,
                    "local_delta": float(local_delta[idx]),
                    "mean_pred_delta": float(pred_delta.mean()),
                    "p90_pred_delta": float(pred_delta.quantile(0.90)),
                    "p95_pred_delta": float(pred_delta.quantile(0.95)),
                    "mean_vs_e95": float(vs_e95.mean()),
                    "p90_vs_e95": float(vs_e95.quantile(0.90)),
                    "p95_vs_e95": float(vs_e95.quantile(0.95)),
                    "beat_e95_rate": float((pred_delta < e124mod.OBS_DELTA["e95"] - 1.0e-12).mean()),
                }
            )
    return pd.DataFrame(rows)


def merge_transfer(scan: pd.DataFrame, transfer: pd.DataFrame) -> pd.DataFrame:
    if transfer.empty:
        return scan
    wide = transfer.pivot_table(
        index="pred_index",
        columns="filter",
        values=["mean_vs_e95", "p95_vs_e95", "beat_e95_rate", "n_scenarios"],
        aggfunc="first",
    )
    wide.columns = [f"post101_{metric}_{filter_name}" for metric, filter_name in wide.columns]
    return scan.merge(wide.reset_index(), on="pred_index", how="left")


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("density_synth")].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["source", "field", "scope", "modifier", "mask_kind", "quantile"]
    for keys, group in variants.groupby(group_cols, dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
        actionable = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        post_ok = actionable[
            actionable["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
            & actionable["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
            & actionable["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        ]
        best_local = evaluated.sort_values("all_minus_base").head(1)
        best_post = evaluated.sort_values("post101_mean_vs_e95_e101_sensor").head(1)
        rows.append(
            {
                **dict(zip(group_cols, keys)),
                "rows": int(len(group)),
                "evaluated": int(len(evaluated)),
                "strict": int(len(strict)),
                "strict_actionable": int(len(actionable)),
                "post101_submit_gate": int(len(post_ok)),
                "best_all_minus_e95": float(best_local["all_minus_base"].iloc[0]) if len(best_local) else np.nan,
                "best_all_delta_vs_mixmin": float(best_local["all_delta_vs_mixmin"].iloc[0]) if len(best_local) else np.nan,
                "best_tail": float(best_local["e72_adverse_positive_exposure_all"].iloc[0]) if len(best_local) else np.nan,
                "best_sensor_mean_vs_e95": float(best_post["post101_mean_vs_e95_e101_sensor"].iloc[0]) if len(best_post) else np.nan,
                "best_sensor_p95_vs_e95": float(best_post["post101_p95_vs_e95_e101_sensor"].iloc[0]) if len(best_post) else np.nan,
                "best_sensor_beat": float(best_post["post101_beat_e95_rate_e101_sensor"].iloc[0]) if len(best_post) else np.nan,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["post101_submit_gate", "strict_actionable", "strict", "best_sensor_mean_vs_e95", "best_all_minus_e95"],
        ascending=[False, False, False, True, True],
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[
        scan["strategy"].eq("density_synth")
        & scan["strict_gate"].fillna(False).astype(bool)
        & scan["gate_strict_actionable"].fillna(False).astype(bool)
        & scan["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & scan["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & scan["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
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
    transfer: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    controls = scan[scan["strategy"].eq("control")].copy()
    variants = scan[scan["strategy"].eq("density_synth")].copy()
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    veto_actionable = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    submit_gate = local_and_veto[
        local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
    ].copy()

    control_cols = [
        "source",
        "base_index",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "e72_adverse_positive_exposure_all",
        "mean_abs_logit_move_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "gate_strict_actionable",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "post101_beat_e95_rate_e101_sensor",
    ]
    row_cols = [
        "source",
        "mask_name",
        "alpha",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "e72_adverse_positive_exposure_all",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "gate_strict_actionable",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "post101_beat_e95_rate_e101_sensor",
        "tag",
    ]

    if submit_gate.empty:
        decision = (
            "No submission. The E127 density field can create E95-neighborhood "
            "variants, but none simultaneously beats E95 locally, satisfies the "
            "separated transfer-shrinkage vetoes, and remains favorable under the "
            "post-E101 sensor-world filter."
        )
    else:
        decision = (
            f"Materialized `{submission_path.name if submission_path else 'unknown'}`. "
            "This file should be read as a direct claim that transfer-shrinkage "
            "density creates a genuinely new E95-successor point, not an old-file rank."
        )

    lines = [
        "# E130 Tail-Density Synthesis Probe",
        "",
        "## Question",
        "",
        "After E129 closed the existing-file universe, can the E127 transfer-shrinkage density field synthesize a new E95-neighborhood movement that survives E95-relative local stress, E128/E129 vetoes, and post-E101 public-world stress?",
        "",
        "## Method",
        "",
        "- Start from E95, not mixmin.",
        "- Move partially toward E86/E90/E89/E85/noQ2/mixmin only on cells selected by E127 tail-equal, low-alpha, E101-plausible, or combined density fields.",
        "- Candidate rows use E95 as `base_index`, so strict local stress means the candidate must beat E95, not only mixmin.",
        "- Add E95 hard-tail exposure, E129 separated veto components, and E124 post-E101 transfer filters.",
        "- Materialize only if a candidate clears all three gates.",
        "",
        "## Counts",
        "",
        f"- total rows: `{len(scan)}`",
        f"- variants: `{len(variants)}`",
        f"- evaluated variants: `{len(evaluated)}`",
        f"- strict variants: `{len(strict)}`",
        f"- E129-veto-actionable variants before local strict: `{len(veto_actionable)}`",
        f"- local-strict plus E129-veto-actionable variants: `{len(local_and_veto)}`",
        f"- final submit-gate variants: `{len(submit_gate)}`",
        f"- transfer rows: `{len(transfer)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Controls",
        "",
        md_table(controls[control_cols].sort_values(["source"], na_position="last"), ".9f"),
        "",
        "## Summary",
        "",
        md_table(summary.head(40), ".9f"),
        "",
        "## Best Local Evaluated Variants",
        "",
        md_table(evaluated.sort_values(["all_minus_base", "all_delta_vs_mixmin"])[row_cols].head(30), ".9f")
        if len(evaluated)
        else "None.",
        "",
        "## Strict Actionable Variants",
        "",
        md_table(local_and_veto.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(local_and_veto)
        else "None.",
        "",
        "## Final Submit-Gate Variants",
        "",
        md_table(submit_gate.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(30), ".9f")
        if len(submit_gate)
        else "None.",
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = load_refs(sample)
    tail_state = e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    rows, preds, _masks, density = build_candidates(sample, refs)
    labels, worlds, views, state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, state)
    scan = add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = merge_transfer(scan, transfer)
    summary = summarize(scan)
    submission_path = materialize(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, summary, transfer, submission_path)

    variants = scan[scan["strategy"].eq("density_synth")]
    evaluated = variants[variants["nonanchor_evaluated"].fillna(False).astype(bool)]
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
    veto_actionable = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)]
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)]
    submit_gate = local_and_veto[
        local_and_veto["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & local_and_veto["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & local_and_veto["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
    ]
    print(
        {
            "rows": int(len(scan)),
            "variants": int(len(variants)),
            "evaluated": int(len(evaluated)),
            "strict": int(len(strict)),
            "veto_actionable": int(len(veto_actionable)),
            "local_and_veto": int(len(local_and_veto)),
            "submit_gate": int(len(submit_gate)),
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
