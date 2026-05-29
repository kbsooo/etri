#!/usr/bin/env python3
"""E140: tail/world-aware primitive decoder for visible block-target state.

E139 rejected combo-set sign consensus as the missing decoder. This probe stops
filtering the E95 gradient and instead asks a smaller primitive question:

Inside the E136 block-target state and E138/E139 safety support, do any
single-cell logit directions directly satisfy local reward, all-set tail
neutrality, world non-worsening, and raw-energy non-worsening? If so, can the
surviving primitives accumulate into a candidate that passes the usual gates?

No public labels are fitted. A submission is materialized only if a combined
primitive movement is E95-local strict, transfer-veto-actionable, post-E101
favorable, and material.
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
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e132_veto_nullspace_gradient_probe as e132  # noqa: E402
import e137_blocktarget_state_movement_probe as e137  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e139_blocktarget_set_consensus_decoder_probe as e139  # noqa: E402


MICRO_OUT = OUT / "e140_tailworld_primitive_decoder_probe_micro.csv"
SCAN_OUT = OUT / "e140_tailworld_primitive_decoder_probe_scan.csv"
SUMMARY_OUT = OUT / "e140_tailworld_primitive_decoder_probe_summary.csv"
SUPPORT_OUT = OUT / "e140_tailworld_primitive_decoder_probe_support_summary.csv"
REPORT_OUT = OUT / "e140_tailworld_primitive_decoder_probe_report.md"
TRANSFER_OUT = OUT / "e140_tailworld_primitive_decoder_probe_transfer.csv"
SUBMISSION_PREFIX = "submission_e140_tailworld"

EPS = 1.0e-6
MICRO_STEP = 0.020
MATERIAL_FLOOR = 1.0e-7
TOP_KS = [10, 20, 40, 80, 120, 180, 240]
SCALES = [0.005, 0.010, 0.020, 0.040]
SHAPES = ["sign", "sqrt"]
TOL = 1.0e-12

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


def score_all_rows(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    stress_state: Any,
) -> pd.DataFrame:
    combo = e70.combo_scores(rows, [mixmin] + preds, sample).reset_index(drop=True)
    combo["row_id"] = np.arange(len(combo), dtype=int)
    base_rows = combo[["row_id", "pred_index", "base_index"]].copy()
    nonanchor = e70.nonanchor_scores(base_rows, preds, mixmin, labels, worlds, views, stress_state)
    metric_cols = [c for c in nonanchor.columns if c not in base_rows.columns and c != "row_id"]
    scan_input = combo.merge(nonanchor[["row_id", *metric_cols]], on="row_id", how="left")
    scan_input["nonanchor_evaluated"] = True
    scan = e70.add_gates(scan_input, preds, mixmin)
    scan = scan.rename(columns={"strict_consensus_gate": "strict_gate", "loose_consensus_gate": "loose_gate"})
    scan["deployable_gate"] = scan["strict_gate"]
    scan["structural_all_sets_tail_neutral"] = scan["sets_tail_neutral"].eq(len(e70.COMBO_TABLES))
    scan["structural_all_sets_beat_base"] = scan["sets_beating_base"].eq(len(e70.COMBO_TABLES))
    scan["structural_hidden_core_beats_base"] = scan["hidden_core_minus_base"].lt(0.0)
    scan["structural_world_nonworse"] = scan["world_support_minus_base"].le(0.0)
    scan["structural_raw_energy_nonworse"] = scan["raw_energy_q_p90_minus_base"].le(0.0)
    scan["structural_strict_gate"] = (
        scan["all_margin_vs_mixmin"]
        & scan["all_beats_base"]
        & scan["structural_all_sets_beat_base"]
        & scan["structural_all_sets_tail_neutral"]
        & scan["structural_hidden_core_beats_base"]
        & scan["structural_world_nonworse"]
        & scan["structural_raw_energy_nonworse"]
    )
    scan["structural_loose_gate"] = (
        scan["all_beats_base"]
        & scan["structural_hidden_core_beats_base"]
        & scan["structural_world_nonworse"]
    )
    return scan.reset_index(drop=True)


def support_cells(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    state: np.ndarray,
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[pd.DataFrame, np.ndarray]:
    state_masks = e138.filtered_state_masks(state)
    risk_sign = e132.risk_signs(tail_state)
    risk_weight = 1.0 * state + 0.50 * e130.normalize_nonzero(density["tail_equal"]) + 0.25
    decoders, decoder_summary = e139.build_decoder_units(sample, refs["e95"])

    support: dict[tuple[int, int], dict[str, Any]] = {}
    for dec in decoders:
        unit = np.asarray(dec["unit"], dtype=np.float64)
        safety_masks = e138.filtered_safety_masks(unit, density, risk_sign, risk_weight)
        masks, _mask_summary = e138.combined_masks(state, state_masks, safety_masks)
        for mask_rec in masks:
            hard = np.asarray(mask_rec["mask"], dtype=np.float64) > 1.0e-12
            for row_idx, target_idx in np.argwhere(hard):
                key = (int(row_idx), int(target_idx))
                rec = support.setdefault(
                    key,
                    {
                        "row_idx": int(row_idx),
                        "target_idx": int(target_idx),
                        "target": TARGETS[int(target_idx)],
                        "support_count": 0,
                        "decoder_count": 0,
                        "mask_count": 0,
                        "state": float(state[row_idx, target_idx]),
                        "density_tail_equal": float(density["tail_equal"][row_idx, target_idx]),
                        "density_low_alpha": float(density["low_alpha"][row_idx, target_idx]),
                        "density_score": float(density["density_score"][row_idx, target_idx]),
                        "e101_active": bool(density["e101_active"][row_idx, target_idx]),
                        "q2s3": bool(target_idx in Q2S3),
                        "s_all": bool(target_idx in S_ALL),
                        "decoder_names": set(),
                        "safety_scopes": set(),
                        "state_scopes": set(),
                        "unit_abs_sum": 0.0,
                    },
                )
                rec["support_count"] += 1
                rec["mask_count"] += 1
                rec["decoder_names"].add(str(dec["decoder"]))
                rec["safety_scopes"].add(str(mask_rec["safety_scope"]))
                rec["state_scopes"].add(str(mask_rec["state_scope"]))
                rec["unit_abs_sum"] += float(abs(unit[row_idx, target_idx]))
    rows: list[dict[str, Any]] = []
    for rec in support.values():
        out = dict(rec)
        out["decoder_count"] = len(rec["decoder_names"])
        out["safety_scope_count"] = len(rec["safety_scopes"])
        out["state_scope_count"] = len(rec["state_scopes"])
        out["decoder_names"] = ",".join(sorted(rec["decoder_names"]))
        out["safety_scopes"] = ",".join(sorted(rec["safety_scopes"]))
        out["state_scopes"] = ",".join(sorted(rec["state_scopes"]))
        rows.append(out)
    support_df = pd.DataFrame(rows).sort_values(["support_count", "state"], ascending=[False, False])
    return support_df.reset_index(drop=True), np.asarray(risk_sign, dtype=np.float64)


def build_micro_candidates(
    support_df: pd.DataFrame,
    refs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95_logit = logit(refs["e95"])
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [refs["e95"]]
    for rec in support_df.to_dict("records"):
        row_idx = int(rec["row_idx"])
        target_idx = int(rec["target_idx"])
        for direction in [-1.0, 1.0]:
            delta = np.zeros_like(refs["e95"], dtype=np.float64)
            delta[row_idx, target_idx] = float(direction) * MICRO_STEP
            pred = clip_prob(sigmoid(e95_logit + delta))
            pred_index = len(preds)
            preds.append(pred)
            rows.append(
                {
                    "pred_index": pred_index,
                    "base_index": 0,
                    "strategy": "primitive_micro",
                    "row_idx": row_idx,
                    "target_idx": target_idx,
                    "target": str(rec["target"]),
                    "direction": float(direction),
                    "support_count": int(rec["support_count"]),
                    "decoder_count": int(rec["decoder_count"]),
                    "state": float(rec["state"]),
                    "density_tail_equal": float(rec["density_tail_equal"]),
                    "density_low_alpha": float(rec["density_low_alpha"]),
                    "density_score": float(rec["density_score"]),
                    "e101_active": bool(rec["e101_active"]),
                    "q2s3": bool(rec["q2s3"]),
                    "s_all": bool(rec["s_all"]),
                    "tag": f"micro_r{row_idx}_t{target_idx}_{'p' if direction > 0 else 'm'}",
                }
            )
    return pd.DataFrame(rows), preds


def annotate_micro(micro: pd.DataFrame) -> pd.DataFrame:
    tail_cols = [f"set_{name}_worst_minus_base" for name in e70.COMBO_TABLES]
    set_cols = [f"set_{name}_minus_base" for name in e70.COMBO_TABLES]
    out = micro.copy()
    out["primitive_all_sets_beat"] = out[set_cols].le(-TOL).all(axis=1)
    out["primitive_tail_neutral"] = out[tail_cols].le(TOL).all(axis=1)
    out["primitive_world_nonworse"] = out["world_support_minus_base"].le(TOL)
    out["primitive_raw_nonworse"] = out["raw_energy_q_p90_minus_base"].le(TOL)
    out["primitive_hidden_core_beats"] = out["hidden_core_minus_base"].lt(-TOL)
    out["primitive_local_reward"] = out["all_minus_base"].lt(-TOL)
    out["primitive_strict"] = (
        out["primitive_local_reward"]
        & out["primitive_all_sets_beat"]
        & out["primitive_tail_neutral"]
        & out["primitive_hidden_core_beats"]
        & out["primitive_world_nonworse"]
        & out["primitive_raw_nonworse"]
    )
    out["primitive_tail_world_local"] = (
        out["primitive_local_reward"]
        & out["primitive_tail_neutral"]
        & out["primitive_world_nonworse"]
        & out["primitive_raw_nonworse"]
    )
    max_tail = out[tail_cols].max(axis=1)
    max_set = out[set_cols].max(axis=1)
    out["max_set_minus_base"] = max_set
    out["max_tail_minus_base"] = max_tail
    out["primitive_score"] = (
        -out["all_minus_base"].clip(upper=0.0)
        - 2.0 * max_set.clip(lower=0.0)
        - 4.0 * max_tail.clip(lower=0.0)
        - 4.0 * out["world_support_minus_base"].clip(lower=0.0)
        - 4.0 * out["raw_energy_q_p90_minus_base"].clip(lower=0.0)
        - 1.0 * out["hidden_core_minus_base"].clip(lower=0.0)
    )
    return out.sort_values(
        [
            "primitive_strict",
            "primitive_tail_world_local",
            "primitive_score",
            "all_minus_base",
        ],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def best_direction_per_cell(micro: pd.DataFrame, predicate: str) -> pd.DataFrame:
    pool = micro[micro[predicate].fillna(False).astype(bool)].copy()
    if pool.empty:
        return pool
    return (
        pool.sort_values(["primitive_score", "all_minus_base"], ascending=[False, True])
        .drop_duplicates(["row_idx", "target_idx"], keep="first")
        .reset_index(drop=True)
    )


def normalize_unit(unit: np.ndarray, selected: np.ndarray, shape: str) -> np.ndarray:
    out = np.zeros_like(unit, dtype=np.float64)
    mask = np.asarray(selected, dtype=bool)
    if not mask.any():
        return out
    if shape == "sign":
        shaped = np.sign(unit)
    elif shape == "sqrt":
        shaped = np.sign(unit) * np.sqrt(np.abs(unit))
    else:
        raise KeyError(shape)
    denom = float(np.mean(np.abs(shaped[mask])))
    if denom <= 1.0e-15:
        return out
    out[mask] = shaped[mask] / denom
    return out


def build_combined_candidates(
    micro: pd.DataFrame,
    refs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95_logit = logit(refs["e95"])
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [refs["e95"]]
    seen: dict[str, int] = {e138.pred_key(refs["e95"]): 0}
    pools = {
        "strict_primitive": best_direction_per_cell(micro, "primitive_strict"),
        "tail_world_local_primitive": best_direction_per_cell(micro, "primitive_tail_world_local"),
        "score_top_local": micro[micro["primitive_local_reward"]].copy(),
    }
    for pool_name, pool in pools.items():
        if pool.empty:
            continue
        pool = (
            pool.sort_values(["primitive_score", "all_minus_base"], ascending=[False, True])
            .drop_duplicates(["row_idx", "target_idx"], keep="first")
            .reset_index(drop=True)
        )
        for top_k in TOP_KS:
            chosen = pool.head(top_k)
            if chosen.empty:
                continue
            unit = np.zeros_like(refs["e95"], dtype=np.float64)
            selected = np.zeros_like(refs["e95"], dtype=bool)
            for rec in chosen.to_dict("records"):
                r = int(rec["row_idx"])
                t = int(rec["target_idx"])
                selected[r, t] = True
                unit[r, t] = float(rec["direction"]) * max(float(rec["primitive_score"]), 1.0e-12)
            for shape in SHAPES:
                shaped = normalize_unit(unit, selected, shape)
                if float(np.abs(shaped).mean()) <= 1.0e-15:
                    continue
                for scale in SCALES:
                    pred = clip_prob(sigmoid(e95_logit + float(scale) * shaped))
                    key = e138.pred_key(pred)
                    if key in seen:
                        pred_index = seen[key]
                    else:
                        pred_index = len(preds)
                        seen[key] = pred_index
                        preds.append(pred)
                    rows.append(
                        {
                            "pred_index": pred_index,
                            "base_index": 0,
                            "strategy": "tailworld_primitive_decoder",
                            "pool": pool_name,
                            "top_k": int(len(chosen)),
                            "shape": shape,
                            "scale": float(scale),
                            "selected_cells": int(selected.sum()),
                            "selected_rows": int(selected.any(axis=1).sum()),
                            "selected_q2s3_cells": int(selected[:, Q2S3].sum()),
                            "selected_s_cells": int(selected[:, S_ALL].sum()),
                            "mean_primitive_score": float(chosen["primitive_score"].mean()),
                            "mean_micro_all_minus_base": float(chosen["all_minus_base"].mean()),
                            "max_micro_tail_minus_base": float(chosen["max_tail_minus_base"].max()),
                            "max_micro_world_minus_base": float(chosen["world_support_minus_base"].max()),
                            "max_micro_raw_minus_base": float(chosen["raw_energy_q_p90_minus_base"].max()),
                            "tag": e83.stable_tag(pred, f"e140_{pool_name}_"),
                        }
                    )
    return pd.DataFrame(rows), preds


def eligible_rows(scan: pd.DataFrame) -> pd.DataFrame:
    return scan[
        scan["strategy"].eq("tailworld_primitive_decoder")
        & scan["strict_gate"].fillna(False).astype(bool)
        & scan["gate_strict_actionable"].fillna(False).astype(bool)
        & scan["post101_mean_vs_e95_e101_sensor"].fillna(np.inf).lt(0.0)
        & scan["post101_p95_vs_e95_e101_sensor"].fillna(np.inf).le(0.0)
        & scan["post101_beat_e95_rate_e101_sensor"].fillna(0.0).ge(0.55)
        & scan["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()


def summarize_micro(micro: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "scope": "support_cells",
            "rows": int(len(support)),
            "targets": ",".join(f"{k}:{v}" for k, v in support["target"].value_counts().sort_index().items()),
            "q2s3_cells": int(support["q2s3"].sum()),
            "e101_active_cells": int(support["e101_active"].sum()),
            "strict_primitives": np.nan,
            "tail_world_local_primitives": np.nan,
            "local_reward_primitives": np.nan,
            "best_all_minus_base": np.nan,
            "best_primitive_score": np.nan,
        }
    ]
    for target, group in [("all", micro), *list(micro.groupby("target", sort=True))]:
        rows.append(
            {
                "scope": str(target),
                "rows": int(len(group)),
                "targets": "",
                "q2s3_cells": int(group["q2s3"].sum()),
                "e101_active_cells": int(group["e101_active"].sum()),
                "strict_primitives": int(group["primitive_strict"].sum()),
                "tail_world_local_primitives": int(group["primitive_tail_world_local"].sum()),
                "local_reward_primitives": int(group["primitive_local_reward"].sum()),
                "best_all_minus_base": float(group["all_minus_base"].min()) if len(group) else np.nan,
                "best_primitive_score": float(group["primitive_score"].max()) if len(group) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def summarize_scan(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("tailworld_primitive_decoder")].copy()
    rows: list[dict[str, Any]] = []
    for keys, group in variants.groupby(["pool", "shape", "scale"], dropna=False):
        pool, shape, scale = keys
        strict = group[group["strict_gate"].fillna(False).astype(bool)].copy()
        veto = group[group["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
        submit = eligible_rows(local_and_veto)
        best_local = group.sort_values("all_minus_base").head(1)
        best_sensor = group.sort_values("post101_mean_vs_e95_e101_sensor").head(1)
        rows.append(
            {
                "pool": str(pool),
                "shape": str(shape),
                "scale": float(scale),
                "rows": int(len(group)),
                "strict": int(len(strict)),
                "veto_actionable": int(len(veto)),
                "local_and_veto": int(len(local_and_veto)),
                "submit_gate": int(len(submit)),
                "best_all_minus_e95": float(best_local["all_minus_base"].iloc[0]) if len(best_local) else np.nan,
                "best_sets_beating_base": int(group["sets_beating_base"].max()) if len(group) else 0,
                "best_sets_tail_neutral": int(group["sets_tail_neutral"].max()) if len(group) else 0,
                "best_world": float(group["world_support_minus_base"].min()) if len(group) else np.nan,
                "best_raw": float(group["raw_energy_q_p90_minus_base"].min()) if len(group) else np.nan,
                "best_sensor_mean_vs_e95": float(best_sensor["post101_mean_vs_e95_e101_sensor"].iloc[0])
                if len(best_sensor)
                else np.nan,
                "best_sensor_p95_vs_e95": float(best_sensor["post101_p95_vs_e95_e101_sensor"].iloc[0])
                if len(best_sensor)
                else np.nan,
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
        ["post101_mean_vs_e95_e101_sensor", "post101_p95_vs_e95_e101_sensor", "all_minus_base"],
        ascending=[True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(out, index=False)
    return out


def write_report(
    support: pd.DataFrame,
    micro: pd.DataFrame,
    micro_summary: pd.DataFrame,
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].eq("tailworld_primitive_decoder")].copy()
    strict = variants[variants["strict_gate"].fillna(False).astype(bool)].copy()
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)].copy()
    submit = eligible_rows(scan)
    blockers = {}
    if len(variants):
        checks = {
            "all_margin_vs_mixmin": variants["all_margin_vs_mixmin"],
            "all_beats_base": variants["all_beats_base"],
            "structural_all_sets_beat_base": variants["structural_all_sets_beat_base"],
            "structural_all_sets_tail_neutral": variants["structural_all_sets_tail_neutral"],
            "structural_hidden_core_beats_base": variants["structural_hidden_core_beats_base"],
            "structural_world_nonworse": variants["structural_world_nonworse"],
            "structural_raw_energy_nonworse": variants["structural_raw_energy_nonworse"],
        }
        blockers = {name: int((~series.fillna(False).astype(bool)).sum()) for name, series in checks.items()}
    row_cols = [
        "pool",
        "top_k",
        "shape",
        "scale",
        "selected_cells",
        "selected_q2s3_cells",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_core_minus_base",
        "world_support_minus_base",
        "raw_energy_q_p90_minus_base",
        "e72_adverse_positive_exposure_all",
        "gate_strict_actionable",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "tag",
    ]
    decision = (
        f"Materialized `{submission_path.name}`."
        if submission_path is not None
        else "No submission. Primitive tail/world-aware cells did not accumulate into a candidate passing local strict plus transfer-veto plus post-E101 gates."
    )
    lines = [
        "# E140 Tail/World Primitive Decoder Probe",
        "",
        "## Question",
        "",
        "After E139, the next smallest decoder test is whether tail-neutral/world/raw nonworsening exists at the single-cell primitive level inside the visible block-target/veto support.",
        "",
        "## Counts",
        "",
        f"- support cells: `{len(support)}`",
        f"- micro rows: `{len(micro)}`",
        f"- strict primitives: `{int(micro['primitive_strict'].sum()) if len(micro) else 0}`",
        f"- tail/world/local primitives: `{int(micro['primitive_tail_world_local'].sum()) if len(micro) else 0}`",
        f"- combined variants: `{len(variants)}`",
        f"- local strict variants: `{len(strict)}`",
        f"- transfer-veto-actionable variants: `{len(veto)}`",
        f"- local-strict plus transfer-veto-actionable variants: `{len(local_and_veto)}`",
        f"- final submit-gate variants: `{len(submit)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Micro Summary",
        "",
        e138.md_table(micro_summary, ".9f"),
        "",
        "## Combined Gate Blockers",
        "",
        "\n".join(f"- `{k}`: `{v}/{len(variants)}`" for k, v in blockers.items()) if blockers else "_none_",
        "",
        "## Combined Summary",
        "",
        e138.md_table(summary.head(80), ".9f"),
        "",
        "## Best Micro Primitives",
        "",
        e138.md_table(
            micro[
                [
                    "row_idx",
                    "target",
                    "direction",
                    "support_count",
                    "state",
                    "q2s3",
                    "e101_active",
                    "all_minus_base",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_core_minus_base",
                    "world_support_minus_base",
                    "raw_energy_q_p90_minus_base",
                    "max_tail_minus_base",
                    "primitive_strict",
                    "primitive_tail_world_local",
                    "primitive_score",
                ]
            ].head(40),
            ".9f",
        )
        if len(micro)
        else "None.",
        "",
        "## Best Combined Candidates",
        "",
        e138.md_table(variants.sort_values(["all_minus_base", "post101_mean_vs_e95_e101_sensor"])[row_cols].head(40), ".9f")
        if len(variants)
        else "None.",
        "",
        "## Local Strict Plus Transfer-Veto-Actionable Candidates",
        "",
        e138.md_table(local_and_veto.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(40), ".9f")
        if len(local_and_veto)
        else "None.",
        "",
        "## Submit-Gate Candidates",
        "",
        e138.md_table(submit.sort_values(["post101_mean_vs_e95_e101_sensor", "all_minus_base"])[row_cols].head(40), ".9f")
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
    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])

    support, _risk_sign = support_cells(sample, refs, state, density, tail_state)
    micro_rows, micro_preds = build_micro_candidates(support, refs)
    micro_scan = score_all_rows(micro_rows, micro_preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    micro = annotate_micro(micro_scan)
    micro_summary = summarize_micro(micro, support)

    combined_rows, combined_preds = build_combined_candidates(micro, refs)
    if combined_rows.empty:
        scan = combined_rows.copy()
        transfer = pd.DataFrame()
        summary = pd.DataFrame()
        submission_path = None
    else:
        scan = e83.score_candidate_rows(combined_rows, combined_preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
        scan = e130.add_tail_and_veto_metrics(scan, combined_preds, refs, density, tail_state)
        transfer = e130.post_e101_transfer_summary(sample, scan, combined_preds, refs, tail_state)
        scan = e130.merge_transfer(scan, transfer)
        summary = summarize_scan(scan)
        submission_path = materialize(scan, combined_preds, sample)
        scan["materialized_submission"] = False
        if submission_path is not None:
            suffix = submission_path.stem.split("_")[-1]
            scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    support.to_csv(SUPPORT_OUT, index=False)
    micro.to_csv(MICRO_OUT, index=False)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(support, micro, micro_summary, scan, summary, submission_path)

    variants = scan[scan["strategy"].eq("tailworld_primitive_decoder")] if not scan.empty else pd.DataFrame()
    strict = variants[variants["strict_gate"].fillna(False).astype(bool)] if not variants.empty else pd.DataFrame()
    veto = variants[variants["gate_strict_actionable"].fillna(False).astype(bool)] if not variants.empty else pd.DataFrame()
    local_and_veto = strict[strict["gate_strict_actionable"].fillna(False).astype(bool)] if not strict.empty else pd.DataFrame()
    submit = eligible_rows(scan) if not scan.empty else pd.DataFrame()
    print(
        {
            "support_cells": int(len(support)),
            "micro_rows": int(len(micro)),
            "strict_primitives": int(micro["primitive_strict"].sum()) if len(micro) else 0,
            "tail_world_local_primitives": int(micro["primitive_tail_world_local"].sum()) if len(micro) else 0,
            "variants": int(len(variants)),
            "strict": int(len(strict)),
            "veto_actionable": int(len(veto)),
            "local_and_veto": int(len(local_and_veto)),
            "submit_gate": int(len(submit)),
            "best_all_minus_e95": float(variants["all_minus_base"].min()) if len(variants) else None,
            "best_sensor_mean_vs_e95": float(variants["post101_mean_vs_e95_e101_sensor"].min())
            if len(variants)
            else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(20).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
