#!/usr/bin/env python3
"""E142: clip E140 relaxed decoder moves against the transfer-tail budget.

E141 showed that E140's exact tail failure was partly a numerical gate artifact:
relaxed structural rows exist at tail tolerance 1e-12. The remaining blocker is
small but concrete: E72-plausible exposure stays about 3.2e-6 above E95 and the
post-E101 p95 remains positive.

This probe asks the smallest constructive question:

Can we start from E140 relaxed structural rows, roll back only the cells that
create excess E72-plausible exposure, and preserve enough local E95-relative
reward to pass the transfer-tail and post-E101 gates?

No public labels are fitted. A submission is materialized only if a clipped row
passes relaxed structural gates, E72-plausible budget, post-E101 p95, and a
minimum E95-relative local reward.
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
import e96_public_miss_budget_tail_scenarios as e96mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e140_tailworld_primitive_decoder_probe as e140  # noqa: E402
import e141_tail_tolerance_transfer_audit as e141  # noqa: E402


E140_SCAN = OUT / "e140_tailworld_primitive_decoder_probe_scan.csv"
E140_MICRO = OUT / "e140_tailworld_primitive_decoder_probe_micro.csv"

SCAN_OUT = OUT / "e142_transfer_budget_clipped_decoder_probe_scan.csv"
SUMMARY_OUT = OUT / "e142_transfer_budget_clipped_decoder_probe_summary.csv"
TRANSFER_OUT = OUT / "e142_transfer_budget_clipped_decoder_probe_transfer.csv"
FRONTIER_OUT = OUT / "e142_transfer_budget_clipped_decoder_probe_frontier.csv"
REPORT_OUT = OUT / "e142_transfer_budget_clipped_decoder_probe_report.md"
SUBMISSION_PREFIX = "submission_e142_transferclip"

EPS = 1.0e-6
TAIL_TOL = 1.0e-12
MATERIAL_FLOOR = 1.0e-6
MAX_PARENTS = 36
ROLLBACK_COUNTS = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
KEEP_FACTORS = [0.0, 0.25, 0.50]
UNIFORM_KEEP = [0.25, 0.50, 0.75, 0.90]

Q2 = TARGETS.index("Q2")
S3 = TARGETS.index("S3")
Q2S3 = [Q2, S3]
S_ALL = [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"]]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def tail_cols(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns if c.startswith("set_") and c.endswith("_worst_minus_base")]


def set_cols(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns if c.startswith("set_") and c.endswith("_minus_base") and "worst" not in c]


def add_relaxed_flags(scan: pd.DataFrame, threshold: float) -> pd.DataFrame:
    out = scan.copy()
    tails = tail_cols(out)
    sets = set_cols(out)
    out["tail_pass_tol1e12"] = out[tails].le(TAIL_TOL).all(axis=1)
    out["all_sets_mean_beat"] = out[sets].lt(0.0).all(axis=1)
    out["relaxed_structural_tol1e12"] = (
        out["all_margin_vs_mixmin"].fillna(False).astype(bool)
        & out["all_beats_base"].fillna(False).astype(bool)
        & out["all_sets_mean_beat"]
        & out["tail_pass_tol1e12"]
        & out["hidden_core_minus_base"].lt(0.0)
        & out["world_support_minus_base"].le(0.0)
        & out["raw_energy_q_p90_minus_base"].le(0.0)
    )
    out["e72_plausible_gap_vs_e95"] = out["e72_adverse_exposure_e101_plausible"] - float(threshold)
    out["post101_ok"] = (
        out["post101_mean_vs_e95_e101_sensor"].lt(0.0)
        & out["post101_p95_vs_e95_e101_sensor"].le(0.0)
        & out["post101_beat_e95_rate_e101_sensor"].ge(0.55)
    )
    out["budget_ok"] = out["e72_plausible_gap_vs_e95"].le(1.0e-12)
    out["local_material"] = out["all_minus_base"].lt(-MATERIAL_FLOOR)
    out["submit_relaxed"] = (
        out["strategy"].eq("transfer_budget_clip")
        & out["relaxed_structural_tol1e12"]
        & out["budget_ok"]
        & out["post101_ok"]
        & out["local_material"]
    )
    return out


def exposure_arrays(
    refs: dict[str, np.ndarray],
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    _e72_delta, _e72_weight, wrong_is_zero, wrong_is_one = tail_state
    e95_adverse = np.maximum(
        e96mod.adverse_delta_for_e72_direction(refs["e95"], refs["mixmin"], wrong_is_zero, wrong_is_one),
        0.0,
    )
    weights = e130.normalize_weight(density["plausible"].reshape(-1)).reshape(refs["e95"].shape)
    return e95_adverse, weights, np.asarray(density["plausible"], dtype=np.float64)


def micro_reward_tables(micro: pd.DataFrame, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    reward = np.zeros(shape, dtype=np.float64)
    penalty = np.zeros(shape, dtype=np.float64)
    for rec in micro.to_dict("records"):
        row_idx = int(rec["row_idx"])
        target_idx = int(rec["target_idx"])
        local = float(rec["all_minus_base"])
        val = max(-local, 0.0)
        # This is only a rollback ranker. Use the best observed single-cell
        # local reward for the cell, independent of the parent direction.
        reward[row_idx, target_idx] = max(reward[row_idx, target_idx], val)
        penalty[row_idx, target_idx] = max(penalty[row_idx, target_idx], max(local, 0.0))
    return reward, penalty


def parent_rows(scan: pd.DataFrame, threshold: float) -> pd.DataFrame:
    flagged = add_relaxed_flags(scan, threshold)
    parents = flagged[
        flagged["strategy"].eq("tailworld_primitive_decoder")
        & flagged["relaxed_structural_tol1e12"]
        & flagged["all_minus_base"].lt(-MATERIAL_FLOOR)
    ].copy()
    if parents.empty:
        return parents
    parents["parent_rank_score"] = (
        -parents["all_minus_base"]
        - 20.0 * parents["e72_plausible_gap_vs_e95"].clip(lower=0.0)
        - 20.0 * parents["post101_p95_vs_e95_e101_sensor"].clip(lower=0.0)
    )
    return (
        parents.sort_values(
            ["e72_plausible_gap_vs_e95", "post101_p95_vs_e95_e101_sensor", "all_minus_base"],
            ascending=[True, True, True],
        )
        .drop_duplicates("pred_index", keep="first")
        .head(MAX_PARENTS)
        .reset_index(drop=True)
    )


def rank_cells(
    method: str,
    delta: np.ndarray,
    excess: np.ndarray,
    reward: np.ndarray,
    density_plausible: np.ndarray,
) -> np.ndarray:
    active = np.abs(delta) > 1.0e-12
    positive = active & (excess > 0.0)
    if not positive.any():
        return np.array([], dtype=int)
    flat_excess = excess.reshape(-1)
    flat_reward = reward.reshape(-1)
    flat_density = density_plausible.reshape(-1)
    flat_delta = np.abs(delta).reshape(-1)
    idx = np.flatnonzero(positive.reshape(-1))
    if method == "excess":
        score = flat_excess[idx]
    elif method == "excess_per_reward":
        score = flat_excess[idx] / (flat_reward[idx] + 1.0e-12)
    elif method == "low_reward_excess":
        score = flat_excess[idx] * (1.0 / (flat_reward[idx] + 1.0e-12))
    elif method == "plausible_density":
        score = flat_density[idx] * flat_delta[idx]
    elif method == "q2s3_excess":
        targets = idx % len(TARGETS)
        score = flat_excess[idx] * np.isin(targets, Q2S3).astype(float)
        if float(score.max()) <= 0.0:
            score = flat_excess[idx]
    else:
        raise KeyError(method)
    return idx[np.argsort(-score)]


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
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, f"e142_{rec['method']}_"), **rec})


def build_clipped_candidates(
    parents: pd.DataFrame,
    combined_preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    density: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    micro: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    e95_logit = logit(refs["e95"])
    e95_adverse, weights, density_plausible = exposure_arrays(refs, density, tail_state)
    reward, _penalty = micro_reward_tables(micro, refs["e95"].shape)
    _e72_delta, _e72_weight, wrong_is_zero, wrong_is_one = tail_state

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [refs["e95"]]
    seen: dict[str, int] = {e138.pred_key(refs["e95"]): 0}

    for pidx, parent in enumerate(parents.to_dict("records")):
        parent_pred = combined_preds[int(parent["pred_index"])]
        parent_logit = logit(parent_pred)
        delta = parent_logit - e95_logit
        parent_adverse = np.maximum(
            e96mod.adverse_delta_for_e72_direction(parent_pred, refs["mixmin"], wrong_is_zero, wrong_is_one),
            0.0,
        )
        excess = np.maximum(parent_adverse - e95_adverse, 0.0) * weights
        active = np.abs(delta) > 1.0e-12
        parent_excess_sum = float(excess[active].sum())

        for keep in UNIFORM_KEEP:
            new_delta = delta * float(keep)
            pred = clip_prob(sigmoid(e95_logit + new_delta))
            add_candidate(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "transfer_budget_clip",
                    "method": "uniform_keep",
                    "parent_rank": int(pidx),
                    "parent_tag": str(parent["tag"]),
                    "parent_pred_index": int(parent["pred_index"]),
                    "parent_all_minus_base": float(parent["all_minus_base"]),
                    "parent_e72_gap": float(parent["e72_plausible_gap_vs_e95"]),
                    "parent_post101_p95": float(parent["post101_p95_vs_e95_e101_sensor"]),
                    "ranker": "",
                    "rollback_cells": int(active.sum()),
                    "rollback_q2s3_cells": int(active[:, Q2S3].sum()),
                    "rollback_s_cells": int(active[:, S_ALL].sum()),
                    "keep_factor": float(keep),
                    "parent_excess_weighted_sum": parent_excess_sum,
                    "estimated_excess_removed": parent_excess_sum * (1.0 - float(keep)),
                },
            )

        for ranker in ["excess", "excess_per_reward", "low_reward_excess", "plausible_density", "q2s3_excess"]:
            order = rank_cells(ranker, delta, excess, reward, density_plausible)
            if len(order) == 0:
                continue
            cumsum = np.cumsum(excess.reshape(-1)[order])
            parent_gap = max(float(parent["e72_plausible_gap_vs_e95"]), 0.0)
            budget_n = int(np.searchsorted(cumsum, parent_gap * 1.05, side="left") + 1) if parent_gap > 0.0 else 0
            counts = sorted(set([n for n in ROLLBACK_COUNTS if n <= len(order)] + [budget_n, budget_n + 1, budget_n + 3]))
            for n in counts:
                if n <= 0:
                    continue
                chosen_flat = order[: min(n, len(order))]
                chosen_mask = np.zeros(delta.size, dtype=bool)
                chosen_mask[chosen_flat] = True
                chosen_mask = chosen_mask.reshape(delta.shape)
                removed = float(excess[chosen_mask].sum())
                for keep_factor in KEEP_FACTORS:
                    new_delta = delta.copy()
                    new_delta[chosen_mask] *= float(keep_factor)
                    pred = clip_prob(sigmoid(e95_logit + new_delta))
                    add_candidate(
                        rows,
                        preds,
                        seen,
                        pred,
                        {
                            "strategy": "transfer_budget_clip",
                            "method": "cell_clip",
                            "parent_rank": int(pidx),
                            "parent_tag": str(parent["tag"]),
                            "parent_pred_index": int(parent["pred_index"]),
                            "parent_all_minus_base": float(parent["all_minus_base"]),
                            "parent_e72_gap": float(parent["e72_plausible_gap_vs_e95"]),
                            "parent_post101_p95": float(parent["post101_p95_vs_e95_e101_sensor"]),
                            "ranker": ranker,
                            "rollback_cells": int(chosen_mask.sum()),
                            "rollback_q2s3_cells": int(chosen_mask[:, Q2S3].sum()),
                            "rollback_s_cells": int(chosen_mask[:, S_ALL].sum()),
                            "keep_factor": float(keep_factor),
                            "parent_excess_weighted_sum": parent_excess_sum,
                            "estimated_excess_removed": removed * (1.0 - float(keep_factor)),
                        },
                    )

    return pd.DataFrame(rows), preds


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("transfer_budget_clip")].copy()
    rows: list[dict[str, Any]] = []
    group_cols = ["method", "ranker", "keep_factor"]
    for keys, group in variants.groupby(group_cols, dropna=False):
        relaxed = group[group["relaxed_structural_tol1e12"].fillna(False).astype(bool)]
        budget = relaxed[relaxed["budget_ok"].fillna(False).astype(bool)]
        post = budget[budget["post101_ok"].fillna(False).astype(bool)]
        submit = post[post["local_material"].fillna(False).astype(bool)]
        best_local = group.sort_values("all_minus_base").head(1)
        best_budget = budget.sort_values("all_minus_base").head(1)
        rows.append(
            {
                **dict(zip(group_cols, keys)),
                "rows": int(len(group)),
                "relaxed": int(len(relaxed)),
                "budget_ok": int(len(budget)),
                "post101_ok_after_budget": int(len(post)),
                "submit_relaxed": int(len(submit)),
                "best_all_minus_e95": float(best_local["all_minus_base"].iloc[0]) if len(best_local) else np.nan,
                "best_e72_gap": float(group["e72_plausible_gap_vs_e95"].min()) if len(group) else np.nan,
                "best_post101_p95": float(group["post101_p95_vs_e95_e101_sensor"].min()) if len(group) else np.nan,
                "best_budget_all_minus_e95": float(best_budget["all_minus_base"].iloc[0]) if len(best_budget) else np.nan,
                "best_budget_post101_p95": float(best_budget["post101_p95_vs_e95_e101_sensor"].min()) if len(best_budget) else np.nan,
            }
        )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(
        ["submit_relaxed", "post101_ok_after_budget", "budget_ok", "relaxed", "best_budget_all_minus_e95", "best_all_minus_e95"],
        ascending=[False, False, False, False, True, True],
    )


def frontier(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("transfer_budget_clip")].copy()
    if variants.empty:
        return variants
    variants["survival_score"] = (
        -variants["all_minus_base"].clip(upper=0.0)
        - 30.0 * variants["e72_plausible_gap_vs_e95"].clip(lower=0.0)
        - 30.0 * variants["post101_p95_vs_e95_e101_sensor"].clip(lower=0.0)
        - 2.0 * (~variants["relaxed_structural_tol1e12"].fillna(False)).astype(float)
    )
    keep_cols = [
        "method",
        "ranker",
        "keep_factor",
        "rollback_cells",
        "rollback_q2s3_cells",
        "rollback_s_cells",
        "parent_tag",
        "parent_all_minus_base",
        "parent_e72_gap",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        "relaxed_structural_tol1e12",
        "e72_adverse_exposure_e101_plausible",
        "e72_plausible_gap_vs_e95",
        "budget_ok",
        "post101_mean_vs_e95_e101_sensor",
        "post101_p95_vs_e95_e101_sensor",
        "post101_beat_e95_rate_e101_sensor",
        "post101_ok",
        "local_material",
        "submit_relaxed",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "mean_abs_logit_move_vs_e95",
        "changed_cells_vs_e95",
        "survival_score",
        "tag",
    ]
    return (
        variants.sort_values(
        ["submit_relaxed", "post101_ok", "budget_ok", "relaxed_structural_tol1e12", "survival_score"],
        ascending=[False, False, False, False, False],
        )
        .drop_duplicates("tag", keep="first")[keep_cols]
        .head(120)
    )


def eligible_rows(scan: pd.DataFrame) -> pd.DataFrame:
    return scan[scan["submit_relaxed"].fillna(False).astype(bool)].copy()


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = eligible_rows(scan)
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["post101_p95_vs_e95_e101_sensor", "e72_plausible_gap_vs_e95", "all_minus_base"],
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
    parents: pd.DataFrame,
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    front: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    variants = scan[scan["strategy"].eq("transfer_budget_clip")].copy()
    relaxed = variants[variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)]
    budget = relaxed[relaxed["budget_ok"].fillna(False).astype(bool)]
    post = budget[budget["post101_ok"].fillna(False).astype(bool)]
    submit = eligible_rows(scan)
    decision = (
        f"Materialized `{submission_path.name}`."
        if submission_path is not None
        else "No submission. Budget clipping can reduce transfer exposure, but did not preserve relaxed structural local reward plus post-E101 safety at material scale."
    )
    lines = [
        "# E142 Transfer-Budget Clipped Decoder Probe",
        "",
        "## Question",
        "",
        "E141 left a narrow blocker: relaxed E140 structural rows are close, but exceed E95's E72-plausible transfer-tail budget and keep post-E101 p95 positive. E142 clips only the cells responsible for that excess exposure.",
        "",
        "## Counts",
        "",
        f"- parent relaxed structural rows used: `{len(parents)}`",
        f"- clipped variants: `{len(variants)}`",
        f"- relaxed structural variants: `{len(relaxed)}`",
        f"- relaxed + E72-budget variants: `{len(budget)}`",
        f"- relaxed + budget + post-E101 variants: `{len(post)}`",
        f"- submit-relaxed variants: `{len(submit)}`",
        f"- materialized submission: `{submission_path.name if submission_path else 'none'}`",
        "",
        "## Summary",
        "",
        e138.md_table(summary.head(80), ".12f") if not summary.empty else "_empty_",
        "",
        "## Frontier Rows",
        "",
        e138.md_table(front.head(40), ".12f") if not front.empty else "_empty_",
        "",
        "## Best Parents",
        "",
        e138.md_table(
            parents[
                [
                    "pool",
                    "top_k",
                    "shape",
                    "scale",
                    "all_minus_base",
                    "e72_plausible_gap_vs_e95",
                    "post101_mean_vs_e95_e101_sensor",
                    "post101_p95_vs_e95_e101_sensor",
                    "tag",
                ]
            ].head(30),
            ".12f",
        )
        if not parents.empty
        else "_empty_",
        "",
        "## Interpretation",
        "",
    ]
    if not variants.empty:
        best_budget = budget.sort_values("all_minus_base").head(1) if len(budget) else pd.DataFrame()
        best_survival = front.head(1)
        lines.extend(
            [
                f"- Best all-minus-E95 among all clipped rows: `{float(variants['all_minus_base'].min()):.12f}`.",
                f"- Best E72 gap among all clipped rows: `{float(variants['e72_plausible_gap_vs_e95'].min()):.12f}`.",
                f"- Best post-E101 p95 among all clipped rows: `{float(variants['post101_p95_vs_e95_e101_sensor'].min()):.12f}`.",
            ]
        )
        if len(best_budget):
            b = best_budget.iloc[0]
            lines.append(
                f"- Best budget-passing row has all-minus-E95 `{float(b['all_minus_base']):.12f}` and post-E101 p95 `{float(b['post101_p95_vs_e95_e101_sensor']):.12f}`."
            )
        if len(best_survival):
            s = best_survival.iloc[0]
            lines.append(
                f"- Best survival row `{s['tag']}`: relaxed `{bool(s['relaxed_structural_tol1e12'])}`, budget `{bool(s['budget_ok'])}`, post101 `{bool(s['post101_ok'])}`, all-minus-E95 `{float(s['all_minus_base']):.12f}`."
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

    e140_scan = pd.read_csv(E140_SCAN)
    micro = pd.read_csv(E140_MICRO)
    parents = parent_rows(e140_scan, threshold)
    _combined_rows, combined_preds = e140.build_combined_candidates(micro, refs)
    if parents.empty:
        scan = pd.DataFrame()
        transfer = pd.DataFrame()
        summary = pd.DataFrame()
        front = pd.DataFrame()
        submission_path = None
    else:
        rows, preds = build_clipped_candidates(parents, combined_preds, refs, density, tail_state, micro)
        scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
        scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
        transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
        scan = e130.merge_transfer(scan, transfer)
        scan = add_relaxed_flags(scan, threshold)
        summary = summarize(scan)
        front = frontier(scan)
        submission_path = materialize(scan, preds, sample)
        scan["materialized_submission"] = False
        if submission_path is not None:
            suffix = submission_path.stem.split("_")[-1]
            scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    front.to_csv(FRONTIER_OUT, index=False)
    write_report(parents, scan, summary, front, submission_path)

    variants = scan[scan["strategy"].eq("transfer_budget_clip")] if not scan.empty else pd.DataFrame()
    relaxed = variants[variants["relaxed_structural_tol1e12"].fillna(False).astype(bool)] if len(variants) else pd.DataFrame()
    budget = relaxed[relaxed["budget_ok"].fillna(False).astype(bool)] if len(relaxed) else pd.DataFrame()
    post = budget[budget["post101_ok"].fillna(False).astype(bool)] if len(budget) else pd.DataFrame()
    submit = eligible_rows(scan) if not scan.empty else pd.DataFrame()
    print(
        {
            "parents": int(len(parents)),
            "variants": int(len(variants)),
            "relaxed": int(len(relaxed)),
            "budget_ok": int(len(budget)),
            "post101_ok_after_budget": int(len(post)),
            "submit_relaxed": int(len(submit)),
            "best_all_minus_e95": float(variants["all_minus_base"].min()) if len(variants) else None,
            "best_e72_gap": float(variants["e72_plausible_gap_vs_e95"].min()) if len(variants) else None,
            "best_post101_p95": float(variants["post101_p95_vs_e95_e101_sensor"].min()) if len(variants) else None,
            "submission": str(submission_path) if submission_path else None,
        }
    )
    print(summary.head(30).to_string(index=False) if not summary.empty else "empty summary")


if __name__ == "__main__":
    main()
