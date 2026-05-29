#!/usr/bin/env python3
"""E89 E86/E72 decontamination scan.

E88 says E86 is locally strong but close to the failed E72 movement manifold.
This experiment asks a sharper question:

Can we reduce E72-contamination proximity while preserving E86's strict
target-pruned stress profile, without training a new model or fitting public LB?
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
from post_mixmin_observation_audit import weighted_corr  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E85_FILE = "submission_e85_inverse_conflict_pruned_58b23ed1.csv"
E86_FILE = "submission_e86_e85_consensus_a3f7c96f.csv"
NOQ2_FILE = "submission_e87_noq2_source_consensus_a85c4e39.csv"
NOOVER_FILE = "submission_e87_q2_nooverstep_consensus_acd7add0.csv"
INVERSE_TOP_FILE = "submission_e87_inverse_top_prior_consensus_5445ec28.csv"

SCAN_OUT = OUT / "e89_e86_e72_decontamination_scan.csv"
SUMMARY_OUT = OUT / "e89_e86_e72_decontamination_summary.csv"
REPORT_OUT = OUT / "e89_e86_e72_decontamination_report.md"

SUBMISSION_PREFIX = "submission_e89_e72decontam"
EPS = 1.0e-6
Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
S2 = TARGETS.index("S2")
S3 = TARGETS.index("S3")
TARGET_PRUNE_IDXS = [Q2, S1, S2, S3]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def load_pred(file_name: str | Path, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)


def high_mask(values: np.ndarray, q: float) -> np.ndarray:
    cut = float(np.quantile(np.asarray(values, dtype=np.float64), q))
    return np.asarray(values, dtype=np.float64) >= cut


def attribution_metrics(delta: np.ndarray, mix_delta: np.ndarray, e72_delta: np.ndarray) -> dict[str, float]:
    abs_cell = np.abs(delta)
    total = float(abs_cell.sum())
    if total <= 0.0:
        return {
            "high_mixmin_cell_mass_frac": 0.0,
            "high_e72_failed_cell_mass_frac": 0.0,
            "e72_failed_overlap_ratio": 0.0,
            "mixmin_reversal_index": 0.0,
            "e72_failed_contamination_index": 0.0,
            "weighted_cell_corr_with_mixmin_move": np.nan,
            "weighted_cell_corr_with_e72_failed_move": np.nan,
            "weighted_row_corr_with_e72_failed_row_move": np.nan,
        }

    high_mix = high_mask(np.abs(mix_delta).ravel(), 0.80).reshape(mix_delta.shape)
    high_e72 = high_mask(np.abs(e72_delta).ravel(), 0.80).reshape(e72_delta.shape)
    e72_abs = np.abs(e72_delta)
    e72_self_mass = float(e72_abs[high_e72].sum() / e72_abs.sum())
    mix_self_mass = float(np.abs(mix_delta)[high_mix].sum() / np.abs(mix_delta).sum())

    row_abs = abs_cell.mean(axis=1)
    e72_row_abs = e72_abs.mean(axis=1)
    high_e72_row = high_mask(e72_row_abs, 0.80)
    e72_row_mass = float(row_abs[high_e72_row].sum() / row_abs.sum()) if row_abs.sum() > 0 else 0.0

    high_mix_mass = float(abs_cell[high_mix].sum() / total)
    high_e72_mass = float(abs_cell[high_e72].sum() / total)
    e72_overlap_ratio = high_e72_mass / e72_self_mass if e72_self_mass > 0 else np.nan
    mix_overlap_ratio = high_mix_mass / mix_self_mass if mix_self_mass > 0 else np.nan
    row_corr = weighted_corr(row_abs, e72_row_abs, row_abs)
    mix_corr = weighted_corr(delta.ravel(), mix_delta.ravel(), abs_cell.ravel())
    e72_corr = weighted_corr(delta.ravel(), e72_delta.ravel(), abs_cell.ravel())
    return {
        "high_mixmin_cell_mass_frac": high_mix_mass,
        "high_e72_failed_cell_mass_frac": high_e72_mass,
        "high_e72_failed_row_mass_frac": e72_row_mass,
        "e72_failed_overlap_ratio": e72_overlap_ratio,
        "mixmin_overlap_ratio": mix_overlap_ratio,
        "mixmin_reversal_index": max(0.0, -mix_corr) * mix_overlap_ratio,
        "e72_failed_contamination_index": 0.5 * (e72_overlap_ratio + max(0.0, row_corr)),
        "weighted_cell_corr_with_mixmin_move": mix_corr,
        "weighted_cell_corr_with_e72_failed_move": e72_corr,
        "weighted_row_corr_with_e72_failed_row_move": row_corr,
    }


def add_candidate(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    mix_logit: np.ndarray,
    delta: np.ndarray,
    rec: dict[str, Any],
) -> None:
    if np.abs(delta).mean() <= 1.0e-14:
        return
    pred = clip_prob(sigmoid(mix_logit + delta))
    tag = e83.stable_tag(pred, f"e89_{rec['strategy']}_")
    if tag in seen:
        pred_index = seen[tag]
    else:
        pred_index = len(preds)
        seen[tag] = pred_index
        preds.append(pred)
    move_abs = np.abs(delta)
    rows.append(
        {
            "pred_index": pred_index,
            "base_index": 0,
            "tag": tag,
            "strategy": rec["strategy"],
            "source": rec.get("source", ""),
            "fallback": rec.get("fallback", ""),
            "row_quantile": rec.get("row_quantile", np.nan),
            "cell_quantile": rec.get("cell_quantile", np.nan),
            "blend_e86_weight": rec.get("blend_e86_weight", np.nan),
            "beta": rec.get("beta", np.nan),
            "projection_scope": rec.get("projection_scope", ""),
            "projection_coeff": rec.get("projection_coeff", np.nan),
            "active_cells": int((move_abs > 1.0e-12).sum()),
            "active_rows": int((move_abs > 1.0e-12).any(axis=1).sum()),
            "mean_abs_logit_move_raw": float(move_abs.mean()),
            "q_group_abs_logit_mean": float(move_abs[:, :3].mean()),
            "s_group_abs_logit_mean": float(move_abs[:, 3:].mean()),
            "q2s3_abs_logit_mean": float(move_abs[:, [Q2, S3]].mean()),
        }
    )


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    mixmin = load_pred(MIXMIN_FILE, sample)
    a2c8 = load_pred(A2C8, sample)
    e72 = load_pred(E72_FILE, sample)
    sources = {
        "e85": load_pred(E85_FILE, sample),
        "e86": load_pred(E86_FILE, sample),
        "noq2": load_pred(NOQ2_FILE, sample),
        "noover": load_pred(NOOVER_FILE, sample),
        "inverse_top": load_pred(INVERSE_TOP_FILE, sample),
    }

    mix_logit = logit(mixmin)
    mix_delta = logit(mixmin) - logit(a2c8)
    e72_delta = logit(e72) - mix_logit
    deltas = {name: logit(pred) - mix_logit for name, pred in sources.items()}
    e72_abs = np.abs(e72_delta)
    e72_row_abs = e72_abs.mean(axis=1)

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {e83.stable_tag(mixmin, "e89_mixmin_"): 0}

    for name in ["e85", "e86", "noq2", "noover", "inverse_top"]:
        add_candidate(rows, preds, seen, mix_logit, deltas[name], {"strategy": "control", "source": name})

    for w in [0.15, 0.25, 0.40, 0.50, 0.60, 0.75, 0.85]:
        delta = w * deltas["e86"] + (1.0 - w) * deltas["noq2"]
        add_candidate(
            rows,
            preds,
            seen,
            mix_logit,
            delta,
            {"strategy": "blend_e86_noq2", "source": "e86+noq2", "blend_e86_weight": w},
        )

    fallback_map = {"noq2": deltas["noq2"], "e85": deltas["e85"], "mixmin": np.zeros_like(deltas["e86"])}
    for q in [0.60, 0.70, 0.80, 0.90]:
        row_mask = high_mask(e72_row_abs, q)[:, None]
        for fallback, fallback_delta in fallback_map.items():
            delta = np.where(row_mask, fallback_delta, deltas["e86"])
            add_candidate(
                rows,
                preds,
                seen,
                mix_logit,
                delta,
                {
                    "strategy": "row_e72_fallback",
                    "source": "e86",
                    "fallback": fallback,
                    "row_quantile": q,
                },
            )
            q2_delta = deltas["e86"].copy()
            q2_delta[:, Q2] = np.where(row_mask[:, 0], 0.0, q2_delta[:, Q2])
            add_candidate(
                rows,
                preds,
                seen,
                mix_logit,
                q2_delta,
                {
                    "strategy": "row_e72_q2_remove",
                    "source": "e86",
                    "fallback": "q2_zero",
                    "row_quantile": q,
                },
            )

    for q in [0.60, 0.70, 0.80, 0.90]:
        cell_mask = high_mask(e72_abs.ravel(), q).reshape(e72_abs.shape)
        for fallback, fallback_delta in fallback_map.items():
            delta = np.where(cell_mask, fallback_delta, deltas["e86"])
            add_candidate(
                rows,
                preds,
                seen,
                mix_logit,
                delta,
                {
                    "strategy": "cell_e72_fallback",
                    "source": "e86",
                    "fallback": fallback,
                    "cell_quantile": q,
                },
            )

    active_e86 = np.abs(deltas["e86"]) > 1.0e-12
    target_pruned_mask = np.zeros_like(deltas["e86"], dtype=bool)
    target_pruned_mask[:, TARGET_PRUNE_IDXS] = True
    for scope_name, scope_mask in [
        ("e86_active", active_e86),
        ("target_pruned", target_pruned_mask),
        ("e86_active_top80cell", active_e86 & high_mask(e72_abs.ravel(), 0.80).reshape(e72_abs.shape)),
        ("target_pruned_top80cell", target_pruned_mask & high_mask(e72_abs.ravel(), 0.80).reshape(e72_abs.shape)),
    ]:
        denom = float(np.sum((e72_delta[scope_mask]) ** 2))
        if denom <= 1.0e-18:
            continue
        coeff = float(np.sum(deltas["e86"][scope_mask] * e72_delta[scope_mask]) / denom)
        for beta in [0.15, 0.25, 0.40, 0.60, 0.80, 1.00]:
            delta = deltas["e86"].copy()
            delta[scope_mask] = delta[scope_mask] - beta * coeff * e72_delta[scope_mask]
            add_candidate(
                rows,
                preds,
                seen,
                mix_logit,
                delta,
                {
                    "strategy": "project_away_e72",
                    "source": "e86",
                    "beta": beta,
                    "projection_scope": scope_name,
                    "projection_coeff": coeff,
                },
            )

    return pd.DataFrame(rows).drop_duplicates("tag").reset_index(drop=True), preds, mixmin, mix_delta, e72_delta


def build_stress_state(sample: pd.DataFrame, mixmin: np.ndarray) -> tuple[np.ndarray, pd.DataFrame, dict[str, np.ndarray], Any]:
    a2c8 = load_pred(A2C8, sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    return labels, worlds, views, state


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["strategy", "source", "fallback", "row_quantile", "cell_quantile", "projection_scope"]
    for keys, group in scan.groupby(group_cols, dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
        best = evaluated.sort_values("all_delta_vs_mixmin").head(1)
        best_row = best.iloc[0] if len(best) else group.sort_values("all_delta_vs_mixmin").iloc[0]
        rows.append(
            {
                **dict(zip(group_cols, keys)),
                "rows": int(len(group)),
                "evaluated": int(len(evaluated)),
                "strict": int(len(strict)),
                "deployable": int(strict["deployable_gate"].sum()) if len(strict) else 0,
                "loose": int(evaluated["loose_gate"].sum()) if len(evaluated) else 0,
                "best_all_delta": float(best_row["all_delta_vs_mixmin"]),
                "best_inverse_top": float(best_row["set_inverse_top_delta_vs_mixmin"]),
                "best_raw05": float(best_row["set_raw05_compatible_delta_vs_mixmin"]),
                "best_all_sign": float(best_row["set_all_sign_delta_vs_mixmin"]),
                "best_hidden_q2s3": float(best_row["hidden_q2s3_mean_minus_base"]),
                "best_world": float(best_row["world_support_minus_base"]),
                "best_block_win": float(best_row["block_q2s3_beats_base_rate"]),
                "best_block_tail": float(best_row["block_q2s3_tail_safe_rate"]),
                "best_e72_contamination_index": float(best_row["e72_failed_contamination_index"]),
                "best_mixmin_reversal_index": float(best_row["mixmin_reversal_index"]),
                "best_tag": str(best_row["tag"]),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "best_e72_contamination_index", "best_all_delta"],
        ascending=[False, False, True, True],
    )


def select_submission(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    if evaluated.empty:
        return None
    e86_ref = scan[scan["source"].eq("e86") & scan["strategy"].eq("control")].iloc[0]
    candidates = evaluated[
        evaluated["strict_gate"].fillna(False).astype(bool)
        & evaluated["all_delta_vs_mixmin"].lt(-1.0e-5)
        & evaluated["set_inverse_top_delta_vs_mixmin"].lt(0.0)
        & evaluated["set_raw05_compatible_delta_vs_mixmin"].lt(0.0)
        & evaluated["set_all_sign_delta_vs_mixmin"].lt(0.0)
        & evaluated["e72_failed_contamination_index"].lt(float(e86_ref["e72_failed_contamination_index"]) - 0.03)
    ].copy()
    if candidates.empty:
        return None
    candidates = candidates.sort_values(
        ["e72_failed_contamination_index", "all_delta_vs_mixmin", "mixmin_reversal_index"],
        ascending=[True, True, True],
    )
    best = candidates.iloc[0]
    out = sample[KEYS].copy()
    out[TARGETS] = preds[int(best["pred_index"])]
    path = OUT / f"{SUBMISSION_PREFIX}_{str(best['tag'])[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, submission_path: Path | None) -> None:
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    cols = [
        "strategy",
        "source",
        "fallback",
        "row_quantile",
        "cell_quantile",
        "blend_e86_weight",
        "beta",
        "projection_scope",
        "all_delta_vs_mixmin",
        "set_inverse_top_delta_vs_mixmin",
        "set_raw05_compatible_delta_vs_mixmin",
        "set_all_sign_delta_vs_mixmin",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "e72_failed_contamination_index",
        "mixmin_reversal_index",
        "strict_gate",
        "tag",
    ]
    best_risk = evaluated.sort_values(["e72_failed_contamination_index", "all_delta_vs_mixmin"]).head(25)
    best_margin = evaluated.sort_values(["all_delta_vs_mixmin", "e72_failed_contamination_index"]).head(25)
    lines = [
        "# E89 E86/E72 Decontamination Scan",
        "",
        "## Observe",
        "",
        "E88 shows E86 is locally strongest but close to the failed E72 movement manifold. This is a decontamination test, not a new model.",
        "",
        "## Wonder",
        "",
        "Can E86 keep strict target-pruned stress while lowering E72 proximity enough to become a cleaner next sensor?",
        "",
        "## Method",
        "",
        "- Use mixmin as base.",
        "- Build controlled logit movements from E86, E85, no-Q2, no-overstep, and inverse-top controls.",
        "- Apply global E86/no-Q2 blends, row/cell fallback on high-E72 movement, rowwise Q2 removal, and projection away from the E72 failed delta.",
        "- Score every candidate with the same combo, hidden/world/block, raw-energy, and tail stress as E86.",
        "- Add E88-style movement attribution metrics to every row.",
        "",
        "## Summary",
        "",
        e56.markdown_table(summary.head(50)),
        "",
        "## Best Strict Rows By E72 Risk",
        "",
        e56.markdown_table(strict.sort_values(["e72_failed_contamination_index", "all_delta_vs_mixmin"])[cols].head(35))
        if len(strict)
        else "None.",
        "",
        "## Best Evaluated Rows By E72 Risk",
        "",
        e56.markdown_table(best_risk[cols]) if len(best_risk) else "None.",
        "",
        "## Best Evaluated Rows By Local Margin",
        "",
        e56.markdown_table(best_margin[cols]) if len(best_margin) else "None.",
        "",
        "## Decision",
        "",
    ]
    if submission_path is None:
        lines += [
            "No E89 decontaminated candidate was materialized.",
            "",
            "This falsifies the cheap repair: simply blending, row/cell fallback, or projecting away from E72 does not produce a strictly better risk-adjusted successor to E86 under the current gate.",
        ]
    else:
        lines += [
            f"Materialized risk-adjusted candidate: `{submission_path.name}`.",
            "",
            "Submit only as a hypothesis test that public prefers lower E72-contamination over maximum E86 local margin.",
        ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, mixmin, mix_delta, e72_delta = build_candidates(sample)
    labels, worlds, views, state = build_stress_state(sample, mixmin)
    scan = e83.score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    attr = []
    for rec in scan.to_dict("records"):
        delta = logit(preds[int(rec["pred_index"])]) - logit(mixmin)
        metrics = attribution_metrics(delta, mix_delta, e72_delta)
        metrics["tag"] = rec["tag"]
        attr.append(metrics)
    scan = scan.merge(pd.DataFrame(attr), on="tag", how="left", validate="one_to_one")
    summary = summarize(scan)
    submission_path = select_submission(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        tag = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(tag)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, submission_path)
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)]
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
    print(
        {
            "rows": int(len(scan)),
            "evaluated": int(len(evaluated)),
            "strict": int(len(strict)),
            "deployable": int(strict["deployable_gate"].sum()) if len(strict) else 0,
            "best_all_delta": float(evaluated["all_delta_vs_mixmin"].min()) if len(evaluated) else None,
            "best_contamination": float(evaluated["e72_failed_contamination_index"].min()) if len(evaluated) else None,
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )


if __name__ == "__main__":
    main()
