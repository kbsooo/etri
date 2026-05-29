#!/usr/bin/env python3
"""E94 soft-health versus hard-label tail audit.

E92 and E93 showed that two soft representation health checks both reward the
known public-negative E72 movement. This audit asks a sharper LogLoss question:
does that movement create hard-label tail exposure that the soft targets hide?

The audit uses E72 only as a public miss sensor. For each cell, it defines the
hard label that would make the E72 move wrong, then measures how much each live
candidate is exposed to that same adverse label direction.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import TARGETS, KEY, clip, logit  # noqa: E402
from public_anchor_bottleneck_decomposition import locate  # noqa: E402


SCORES_OUT = OUT / "e94_soft_health_hard_tail_scores.csv"
TARGET_DETAIL_OUT = OUT / "e94_soft_health_hard_tail_target_detail.csv"
REPORT_OUT = OUT / "e94_soft_health_hard_tail_report.md"

MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
E72_PUBLIC_MISS = E72_PUBLIC - MIXMIN_PUBLIC

CANDIDATES = [
    ("frontier_mixmin", "submission_mixmin_0c916bb4.csv", MIXMIN_PUBLIC, "known_public"),
    ("failed_e72", "submission_e72_topabs50_q2s3_gate_4e48cba2.csv", E72_PUBLIC, "known_public"),
    ("previous_a2c8", "submission_frontier_cvjepa_refine_a2c8d2c8.csv", 0.5774393210, "known_public"),
    ("raw05", "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", 0.5775263072, "known_public"),
    ("stage2", "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", 0.5779449757, "known_public"),
    ("ordinal_q", "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv", 0.5783033652, "known_public"),
    ("final9", "submission_hybrid_0p578_logit_after_subject_final9_strict.csv", 0.5784273528, "known_public"),
    ("bad_q2_jepa", "submission_jepa_latent_q2_w0p45.csv", 0.5798012862, "known_public"),
    ("bad_lejepa", "submission_lejepa_targetwise_strict_best_scale0p5.csv", 0.5802468192, "known_public"),
    ("bad_residual_jepa", "submission_jepa_latent_residual_probe.csv", 0.5812273278, "known_public"),
    ("conservative_e85", "submission_e85_inverse_conflict_pruned_58b23ed1.csv", None, "live"),
    ("max_upside_e86", "submission_e86_e85_consensus_a3f7c96f.csv", None, "live"),
    ("noq2_contrast", "submission_e87_noq2_source_consensus_a85c4e39.csv", None, "live"),
    ("balanced_e90", "submission_e90_e72pareto_28925de5.csv", None, "live"),
    ("min_contam_e89", "submission_e89_e72decontam_00d7807f.csv", None, "live"),
]


def locate_required(file_name: str) -> Path:
    path = locate(file_name)
    if path is not None:
        return path
    alt = JEPA / file_name
    if alt.exists():
        return alt
    raise FileNotFoundError(file_name)


def read_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    path = locate_required(file_name)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not df[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(df[TARGETS].to_numpy(dtype=np.float64))


def entropy(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))


def hard_loss_deltas(candidate: np.ndarray, base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return candidate-minus-base LogLoss deltas for y=0 and y=1."""
    p = clip(candidate)
    b = clip(base)
    d0 = -np.log(1.0 - p) + np.log(1.0 - b)
    d1 = -np.log(p) + np.log(b)
    return d0, d1


def safe_weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    denom = float(np.sum(weights))
    if denom <= 1.0e-18:
        return 0.0
    return float(np.sum(values * weights) / denom)


def safe_weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    weights = np.asarray(weights, dtype=np.float64).reshape(-1)
    mask = weights > 0
    if not np.any(mask):
        return 0.0
    values = values[mask]
    weights = weights[mask]
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cdf = np.cumsum(weights) / float(np.sum(weights))
    return float(values[min(np.searchsorted(cdf, q, side="left"), len(values) - 1)])


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    rows = []
    for rec in frame.to_dict("records"):
        row = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                row.append("")
            elif isinstance(value, (float, np.floating)):
                row.append(format(float(value), floatfmt))
            else:
                row.append(str(value))
        rows.append(row)
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def merge_soft_health(scores: pd.DataFrame) -> pd.DataFrame:
    e92_path = OUT / "e92_hidden_block_posterior_alignment_scores.csv"
    if e92_path.exists():
        e92 = pd.read_csv(e92_path)
        keep = ["role", "posterior_ce_delta_all_vs_mixmin", "e72_direction_mass_agree"]
        scores = scores.merge(e92[[c for c in keep if c in e92.columns]], on="role", how="left")
    e93_path = OUT / "e93_target_manifold_counterenergy_scores.csv"
    if e93_path.exists():
        e93 = pd.read_csv(e93_path)
        keep = ["role", "target_manifold_delta_mean", "conditional_logit_resid_rms_delta_vs_mixmin"]
        scores = scores.merge(e93[[c for c in keep if c in e93.columns]], on="role", how="left")
    for col in ["posterior_ce_delta_all_vs_mixmin", "target_manifold_delta_mean"]:
        if col not in scores.columns:
            scores[col] = np.nan
    scores["soft_health_gain_sum"] = (
        -np.minimum(scores["posterior_ce_delta_all_vs_mixmin"].fillna(0.0), 0.0)
        - np.minimum(scores["target_manifold_delta_mean"].fillna(0.0), 0.0)
    )
    return scores


def role_row(
    role: str,
    file_name: str,
    family: str,
    public_lb: float | None,
    p: np.ndarray,
    base: np.ndarray,
    e72_delta: np.ndarray,
    e72_weight: np.ndarray,
    e72_wrong_is_zero: np.ndarray,
    e72_wrong_is_one: np.ndarray,
) -> dict[str, Any]:
    d0, d1 = hard_loss_deltas(p, base)
    move = logit(p) - logit(base)
    positive_tail = np.maximum(d0, d1)
    negative_best = np.minimum(d0, d1)
    kl_base = base * d1 + (1.0 - base) * d0
    denom = d0 - d1
    q_break = np.array(base, copy=True)
    np.divide(d0, denom, out=q_break, where=np.abs(denom) > 1.0e-18)
    q_break = np.clip(q_break, 0.0, 1.0)

    e72_adverse = np.where(e72_wrong_is_zero, d0, np.where(e72_wrong_is_one, d1, 0.0))
    e72_adverse_pos = np.maximum(e72_adverse, 0.0)
    e72_adverse_neg = np.minimum(e72_adverse, 0.0)
    active = e72_weight > 0

    return {
        "role": role,
        "file": file_name,
        "family": family,
        "public_lb": public_lb,
        "public_delta_vs_mixmin": None if public_lb is None else public_lb - MIXMIN_PUBLIC,
        "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(move))),
        "moved_cell_frac": float(np.mean(np.abs(move) > 1.0e-6)),
        "entropy_delta_vs_mixmin": float(np.mean(entropy(p) - entropy(base))),
        "confidence_delta_vs_mixmin": float(np.mean(np.abs(p - 0.5) - np.abs(base - 0.5))),
        "kl_if_mixmin_calibrated": float(np.mean(kl_base)),
        "hard_worst_tail_mean": float(np.mean(positive_tail)),
        "hard_worst_tail_p95": float(np.quantile(positive_tail, 0.95)),
        "hard_best_case_mean": float(np.mean(negative_best)),
        "break_even_shift_from_mixmin_mean": float(np.mean(np.abs(q_break - base))),
        "e72_adverse_exposure_all": float(np.mean(e72_adverse)),
        "e72_adverse_positive_exposure_all": float(np.mean(e72_adverse_pos)),
        "e72_adverse_negative_exposure_all": float(np.mean(e72_adverse_neg)),
        "e72_adverse_active_mean": float(np.mean(e72_adverse[active])) if np.any(active) else 0.0,
        "e72_adverse_active_positive_mean": float(np.mean(e72_adverse_pos[active])) if np.any(active) else 0.0,
        "e72_adverse_weighted_mean": safe_weighted_mean(e72_adverse, e72_weight),
        "e72_adverse_weighted_positive_mean": safe_weighted_mean(e72_adverse_pos, e72_weight),
        "e72_adverse_weighted_p90": safe_weighted_quantile(e72_adverse, e72_weight, 0.90),
        "e72_adverse_weighted_p99": safe_weighted_quantile(e72_adverse, e72_weight, 0.99),
        "e72_adverse_positive_weight_frac": safe_weighted_mean((e72_adverse > 0).astype(float), e72_weight),
        "e72_same_direction_weight_frac": safe_weighted_mean(((move * e72_delta) > 0).astype(float), e72_weight),
    }


def target_rows(
    role: str,
    file_name: str,
    p: np.ndarray,
    base: np.ndarray,
    e72_delta: np.ndarray,
    e72_weight: np.ndarray,
    e72_wrong_is_zero: np.ndarray,
    e72_wrong_is_one: np.ndarray,
) -> list[dict[str, Any]]:
    d0, d1 = hard_loss_deltas(p, base)
    move = logit(p) - logit(base)
    e72_adverse = np.where(e72_wrong_is_zero, d0, np.where(e72_wrong_is_one, d1, 0.0))
    rows: list[dict[str, Any]] = []
    for j, target in enumerate(TARGETS):
        w = e72_weight[:, j]
        adv = e72_adverse[:, j]
        rows.append(
            {
                "role": role,
                "file": file_name,
                "target": target,
                "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(move[:, j]))),
                "entropy_delta_vs_mixmin": float(np.mean(entropy(p[:, [j]]) - entropy(base[:, [j]]))),
                "kl_if_mixmin_calibrated": float(np.mean(base[:, j] * d1[:, j] + (1.0 - base[:, j]) * d0[:, j])),
                "e72_adverse_positive_exposure_all": float(np.mean(np.maximum(adv, 0.0))),
                "e72_adverse_weighted_mean": safe_weighted_mean(adv, w),
                "e72_adverse_weighted_positive_mean": safe_weighted_mean(np.maximum(adv, 0.0), w),
                "e72_same_direction_weight_frac": safe_weighted_mean(((move[:, j] * e72_delta[:, j]) > 0).astype(float), w),
            }
        )
    return rows


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = read_pred("submission_mixmin_0c916bb4.csv", sample)
    e72 = read_pred("submission_e72_topabs50_q2s3_gate_4e48cba2.csv", sample)
    e72_delta = logit(e72) - logit(base)
    e72_weight = np.abs(e72_delta)
    e72_active = e72_weight > 1.0e-9
    e72_wrong_is_zero = e72_delta > 1.0e-9
    e72_wrong_is_one = e72_delta < -1.0e-9

    score_rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for role, file_name, public_lb, family in CANDIDATES:
        if locate(file_name) is None and not (JEPA / file_name).exists():
            continue
        pred = read_pred(file_name, sample)
        score_rows.append(
            role_row(
                role,
                file_name,
                family,
                public_lb,
                pred,
                base,
                e72_delta,
                e72_weight,
                e72_wrong_is_zero,
                e72_wrong_is_one,
            )
        )
        detail_rows.extend(
            target_rows(
                role,
                file_name,
                pred,
                base,
                e72_delta,
                e72_weight,
                e72_wrong_is_zero,
                e72_wrong_is_one,
            )
        )

    scores = merge_soft_health(pd.DataFrame(score_rows))
    # Risk is not a score forecast. It summarizes hard-label tail exposure under
    # the single concrete public-negative direction we have after mixmin.
    scores["soft_health_per_e72_tail"] = scores["soft_health_gain_sum"] / (
        scores["e72_adverse_positive_exposure_all"] + 1.0e-12
    )
    scores["e72_tail_required_fraction_of_full_exposure"] = E72_PUBLIC_MISS / (
        scores["e72_adverse_positive_exposure_all"] + 1.0e-12
    )
    scores = scores.sort_values(
        ["e72_adverse_positive_exposure_all", "e72_adverse_weighted_positive_mean", "mean_abs_logit_move_vs_mixmin"],
        ascending=True,
    ).reset_index(drop=True)
    details = pd.DataFrame(detail_rows).sort_values(["role", "e72_adverse_positive_exposure_all"], ascending=[True, False])

    scores.to_csv(SCORES_OUT, index=False)
    details.to_csv(TARGET_DETAIL_OUT, index=False)

    live = scores[scores["family"].eq("live")].copy()
    known = scores[scores["public_lb"].notna()].copy().sort_values("public_lb")
    e72_row = scores[scores["role"].eq("failed_e72")].iloc[0]
    live_risk = live.sort_values("e72_adverse_positive_exposure_all")
    live_soft = live.sort_values("soft_health_gain_sum", ascending=False)

    primary = live[live["role"].isin(["max_upside_e86", "balanced_e90", "min_contam_e89"])].copy()
    primary_risk = primary.sort_values("e72_adverse_positive_exposure_all")
    if primary_risk.iloc[0]["role"] == "min_contam_e89":
        decision = (
            "Hard-label E72-adverse tail exposure supports E89 as the lower-downside "
            "sensor among E86/E90/E89, with E85 as the conservative floor and E86 "
            "as the max-upside soft-health candidate."
        )
    else:
        decision = (
            "Hard-label E72-adverse tail exposure does not uniquely support E89; "
            "keep E86/E90/E89 as separate hypothesis sensors."
        )

    known_corr_rows = []
    if len(known) >= 4:
        for col in [
            "e72_adverse_positive_exposure_all",
            "kl_if_mixmin_calibrated",
            "hard_worst_tail_mean",
            "soft_health_gain_sum",
        ]:
            known_corr_rows.append(
                {
                    "metric": col,
                    "spearman_public_lb": float(known[[col, "public_lb"]].corr(method="spearman").iloc[0, 1]),
                }
            )
    known_corr = pd.DataFrame(known_corr_rows)

    lines = [
        "# E94 Soft-Health / Hard-Label Tail Audit",
        "",
        "## Question",
        "",
        "E92 and E93 both reward the known public-negative E72 file. E94 asks whether these soft health checks hide hard-label LogLoss tail risk.",
        "",
        "## Method",
        "",
        "- Use mixmin as the active frontier.",
        "- For every cell, compute candidate-minus-mixmin LogLoss delta for hard label `0` and hard label `1`.",
        "- Define the E72-adverse hard label as the label that would make E72's move wrong in that cell.",
        "- Measure each candidate's exposure to that same adverse label direction.",
        "- Merge E92 posterior CE and E93 target-manifold health only as context, not as a fitted score.",
        "",
        "## Decision",
        "",
        decision,
        "",
        "## E72 Miss Scale",
        "",
        f"- E72 public miss vs mixmin: `{E72_PUBLIC_MISS:.10f}`.",
        f"- E72 active moved cells: `{int(e72_active.sum())}` / `{e72_active.size}`.",
        f"- If every E72 active cell had the E72-adverse label, E72 positive exposure all-cells is `{float(e72_row['e72_adverse_positive_exposure_all']):.9f}`.",
        f"- The observed public miss is only `{float(e72_row['e72_tail_required_fraction_of_full_exposure']):.6f}` of that full-exposure scale.",
        "",
        "## Live Candidate Tail Risk",
        "",
        md_table(
            live_risk[
                [
                    "role",
                    "e72_adverse_positive_exposure_all",
                    "e72_adverse_weighted_positive_mean",
                    "e72_adverse_positive_weight_frac",
                    "e72_same_direction_weight_frac",
                    "soft_health_gain_sum",
                    "posterior_ce_delta_all_vs_mixmin",
                    "target_manifold_delta_mean",
                ]
            ]
        ),
        "",
        "## Live Candidate Soft-Health Order",
        "",
        md_table(
            live_soft[
                [
                    "role",
                    "soft_health_gain_sum",
                    "e72_adverse_positive_exposure_all",
                    "kl_if_mixmin_calibrated",
                    "hard_worst_tail_mean",
                    "entropy_delta_vs_mixmin",
                ]
            ]
        ),
        "",
        "## Known Public Anchor Snapshot",
        "",
        md_table(
            known[
                [
                    "role",
                    "public_lb",
                    "public_delta_vs_mixmin",
                    "e72_adverse_positive_exposure_all",
                    "kl_if_mixmin_calibrated",
                    "hard_worst_tail_mean",
                    "soft_health_gain_sum",
                ]
            ]
        ),
        "",
        "## Known Public Sanity Correlation",
        "",
        md_table(known_corr, floatfmt=".6f") if not known_corr.empty else "Not enough known anchors.",
        "",
        "## Interpretation",
        "",
        "- E72 can look good under soft posterior/target-manifold objectives while requiring only a small realized hard-label tail to miss public.",
        "- E86 has the largest live soft-health gain and a larger E72-adverse tail than E90/E89, so it remains an upside sensor rather than a low-risk file.",
        "- E89 lowers E72-adverse tail by sacrificing soft-health and hidden/world/block edge; E90 is the row-coherent middle point.",
        "- This audit does not create a public score forecast. It explains why soft JEPA-like health metrics need a hard-label tail check.",
        "",
        "## Outputs",
        "",
        f"- `{SCORES_OUT.name}`",
        f"- `{TARGET_DETAIL_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")

    print(
        {
            "rows": int(len(scores)),
            "e72_active_cells": int(e72_active.sum()),
            "e72_public_miss": E72_PUBLIC_MISS,
            "e72_full_adverse_exposure": float(e72_row["e72_adverse_positive_exposure_all"]),
            "best_live_low_tail": str(live_risk.iloc[0]["role"]),
            "best_live_soft_health": str(live_soft.iloc[0]["role"]),
            "report": str(REPORT_OUT),
        }
    )


if __name__ == "__main__":
    main()
