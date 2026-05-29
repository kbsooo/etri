#!/usr/bin/env python3
"""E88 frontier movement attribution.

This is an observation experiment, not a model run. It asks whether the current
post-mixmin candidates move the same hidden cells/blocks that made mixmin public
positive, or whether they are a separate calibration/target-axis correction.
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

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from post_mixmin_observation_audit import (  # noqa: E402
    calendar_mask_features,
    implied_threshold,
    logloss_delta,
    read_frame,
    subject_prior_features,
    weighted_corr,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
import test_movement_fingerprint_selector as e40  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


EPS = 1.0e-15
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
A2C8_FILE = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05_FILE = ROOT / "jepa" / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

SUMMARY_OUT = OUT / "e88_frontier_movement_attribution_candidate_summary.csv"
TARGET_OUT = OUT / "e88_frontier_movement_attribution_target_summary.csv"
CONTEXT_OUT = OUT / "e88_frontier_movement_attribution_context_summary.csv"
CORR_OUT = OUT / "e88_frontier_movement_attribution_feature_corr.csv"
REPORT_OUT = OUT / "e88_frontier_movement_attribution_report.md"


CANDIDATES = [
    {
        "name": "mixmin_vs_a2c8",
        "file": MIXMIN_FILE,
        "base": A2C8_FILE,
        "role": "public frontier movement",
    },
    {
        "name": "e72_failed_vs_mixmin",
        "file": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
        "base": MIXMIN_FILE,
        "role": "known public-negative combined sparse gate",
    },
    {
        "name": "e85_vs_mixmin",
        "file": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
        "base": MIXMIN_FILE,
        "role": "conservative target-prune candidate",
    },
    {
        "name": "e86_vs_mixmin",
        "file": "submission_e86_e85_consensus_a3f7c96f.csv",
        "base": MIXMIN_FILE,
        "role": "source-consensus target-prune candidate",
    },
    {
        "name": "e87_noq2_vs_mixmin",
        "file": "submission_e87_noq2_source_consensus_a85c4e39.csv",
        "base": MIXMIN_FILE,
        "role": "E86 no-Q2 contrast",
    },
    {
        "name": "e87_nooverstep_vs_mixmin",
        "file": "submission_e87_q2_nooverstep_consensus_acd7add0.csv",
        "base": MIXMIN_FILE,
        "role": "E86 no-overstep contrast",
    },
    {
        "name": "e87_inverse_top_vs_mixmin",
        "file": "submission_e87_inverse_top_prior_consensus_5445ec28.csv",
        "base": MIXMIN_FILE,
        "role": "E86 inverse-top-prior contrast",
    },
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def resolve_sub(file_name: str | Path, sample: pd.DataFrame) -> np.ndarray:
    path = Path(file_name)
    if path.is_absolute() and path.exists():
        return load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return load_sub(str(file_name), sample)[TARGETS].to_numpy(dtype=np.float64)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def make_context(sample: pd.DataFrame) -> pd.DataFrame:
    train = read_frame(DATA / "ch2026_metrics_train.csv")
    priors = subject_prior_features(train, sample[KEYS])
    mask_features, _runs = calendar_mask_features(train, sample[KEYS])
    first_train = train.groupby("subject_id")["sleep_date"].min().rename("train_first_sleep")
    last_train = train.groupby("subject_id")["sleep_date"].max().rename("train_last_sleep")
    context = sample[KEYS].copy()
    context = context.merge(priors, on=KEYS, how="left")
    context = context.merge(
        mask_features[
            KEYS
            + [
                "test_run_length",
                "left_context_type",
                "right_context_type",
                "calendar_context",
            ]
        ],
        on=KEYS,
        how="left",
        validate="one_to_one",
    )
    context = context.merge(first_train, on="subject_id", how="left")
    context = context.merge(last_train, on="subject_id", how="left")
    context["days_after_train"] = (context["sleep_date"] - context["train_last_sleep"]).dt.days.astype(float)
    context["test_day_index"] = context.groupby("subject_id").cumcount().astype(float)
    context["global_test_index"] = np.arange(len(context), dtype=float)
    context["train_span_zone"] = np.select(
        [
            context["sleep_date"].lt(context["train_first_sleep"]),
            context["sleep_date"].gt(context["train_last_sleep"]),
        ],
        ["before_train_start", "after_train_end"],
        default="inside_train_calendar",
    )
    context["test_run_length_bin"] = pd.cut(
        context["test_run_length"].fillna(0).astype(float),
        bins=[-1, 1, 3, 7, 999],
        labels=["len1", "len2_3", "len4_7", "len8_plus"],
    ).astype(str)
    order_quintile = np.empty(len(context), dtype=int)
    for i, idx in enumerate(np.array_split(np.arange(len(context)), 5)):
        order_quintile[idx] = i
    context["global_order_quintile"] = order_quintile

    raw_sample, train_feat, test_feat = e40.load_feature_frames()
    raw_scores = e40.make_raw_scores(train_feat, test_feat)
    score_frame = raw_sample[KEYS].copy()
    for col in ("sleep_date", "lifelog_date"):
        score_frame[col] = pd.to_datetime(score_frame[col])
    score_frame["raw_domain_prob"] = raw_scores["domain_prob"]
    score_frame["raw_density_radius"] = raw_scores["density_radius"]
    score_frame["raw_missing_frac"] = raw_scores["missing_frac"]
    score_frame["raw_cluster"] = raw_scores["cluster"].astype(int).astype(str)
    context = context.merge(score_frame, on=KEYS, how="left", validate="one_to_one")
    if context[["calendar_context", "raw_domain_prob", "raw_density_radius"]].isna().any().any():
        raise RuntimeError("context alignment failed")
    for col, qcol in [
        ("raw_domain_prob", "raw_domain_bin"),
        ("raw_density_radius", "raw_density_bin"),
        ("raw_missing_frac", "raw_missing_bin"),
    ]:
        context[qcol] = pd.qcut(context[col].rank(method="first"), 4, labels=["q1_low", "q2", "q3", "q4_high"]).astype(str)
    return context


def group_mass(abs_row: np.ndarray, idx: np.ndarray) -> float:
    total = float(np.sum(abs_row))
    if total <= 0:
        return 0.0
    return float(np.sum(abs_row[idx]) / total)


def high_mask(values: np.ndarray, q: float = 0.80) -> np.ndarray:
    vals = np.asarray(values, dtype=np.float64)
    cut = float(np.quantile(vals, q))
    return vals >= cut


def ce_proxy_summary(
    context: pd.DataFrame,
    candidate: np.ndarray,
    base: np.ndarray,
    train: pd.DataFrame,
) -> dict[str, float]:
    out: dict[str, float] = {}
    for j, target in enumerate(TARGETS):
        old = base[:, j]
        new = candidate[:, j]
        global_prior = float(train[target].mean())
        subj = context[f"subject_prior_{target}"].to_numpy(dtype=np.float64)
        recent = context[f"subject_recent7_{target}"].to_numpy(dtype=np.float64)
        out[f"ce_train_prior_{target}"] = float(np.mean(logloss_delta(new, old, global_prior)))
        out[f"ce_subject_prior_{target}"] = float(np.mean(logloss_delta(new, old, subj)))
        out[f"ce_recent7_prior_{target}"] = float(np.mean(logloss_delta(new, old, recent)))
    out["ce_train_prior_mean"] = float(np.mean([out[f"ce_train_prior_{t}"] for t in TARGETS]))
    out["ce_subject_prior_mean"] = float(np.mean([out[f"ce_subject_prior_{t}"] for t in TARGETS]))
    out["ce_recent7_prior_mean"] = float(np.mean([out[f"ce_recent7_prior_{t}"] for t in TARGETS]))
    return out


def candidate_summaries(
    sample: pd.DataFrame,
    context: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = read_frame(DATA / "ch2026_metrics_train.csv")
    a2c8 = resolve_sub(A2C8_FILE, sample)
    mixmin = resolve_sub(MIXMIN_FILE, sample)
    raw05 = resolve_sub(RAW05_FILE, sample)
    e72 = resolve_sub("submission_e72_topabs50_q2s3_gate_4e48cba2.csv", sample)

    mix_cell_abs = np.abs(logit(mixmin) - logit(a2c8))
    mix_row_abs = mix_cell_abs.mean(axis=1)
    e72_failed_cell_abs = np.abs(logit(e72) - logit(mixmin))
    e72_failed_row_abs = e72_failed_cell_abs.mean(axis=1)
    raw05_delta_from_mixmin = logit(raw05) - logit(mixmin)
    high_mix_cell = high_mask(mix_cell_abs.ravel()).reshape(mix_cell_abs.shape)
    high_mix_row = high_mask(mix_row_abs)
    high_e72_cell = high_mask(e72_failed_cell_abs.ravel()).reshape(e72_failed_cell_abs.shape)
    high_e72_row = high_mask(e72_failed_row_abs)

    candidate_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    context_rows: list[dict[str, Any]] = []
    corr_rows: list[dict[str, Any]] = []

    group_cols = [
        "calendar_context",
        "train_span_zone",
        "test_run_length_bin",
        "global_order_quintile",
        "raw_domain_bin",
        "raw_density_bin",
        "raw_missing_bin",
        "raw_cluster",
        "subject_id",
    ]
    numeric_context = [
        "days_after_train",
        "test_day_index",
        "global_test_index",
        "raw_domain_prob",
        "raw_density_radius",
        "raw_missing_frac",
    ]

    for spec in CANDIDATES:
        name = str(spec["name"])
        candidate = resolve_sub(str(spec["file"]), sample)
        base = resolve_sub(str(spec["base"]), sample)
        prob_delta = candidate - base
        logit_delta = logit(candidate) - logit(base)
        abs_cell = np.abs(logit_delta)
        abs_row = abs_cell.mean(axis=1)
        signed_row = logit_delta.mean(axis=1)
        active = abs_cell > 1.0e-12
        total_mass = float(abs_cell.sum())
        high_mix_mass = float(abs_cell[high_mix_cell].sum() / total_mass) if total_mass > 0 else 0.0
        high_e72_mass = float(abs_cell[high_e72_cell].sum() / total_mass) if total_mass > 0 else 0.0
        raw_corr = weighted_corr(logit_delta.ravel(), raw05_delta_from_mixmin.ravel(), abs_cell.ravel())
        mix_corr = weighted_corr(logit_delta.ravel(), (logit(mixmin) - logit(a2c8)).ravel(), abs_cell.ravel())
        e72_corr = weighted_corr(logit_delta.ravel(), (logit(e72) - logit(mixmin)).ravel(), abs_cell.ravel())
        row_mix_corr = weighted_corr(abs_row, mix_row_abs, abs_row)
        row_e72_corr = weighted_corr(abs_row, e72_failed_row_abs, abs_row)

        summary = {
            "candidate": name,
            "file": spec["file"],
            "base": spec["base"],
            "role": spec["role"],
            "active_cells": int(active.sum()),
            "active_rows": int(active.any(axis=1).sum()),
            "mean_abs_prob_move": float(np.abs(prob_delta).mean()),
            "mean_abs_logit_move": float(abs_cell.mean()),
            "p90_row_abs_logit_move": float(np.quantile(abs_row, 0.90)),
            "max_row_abs_logit_move": float(abs_row.max()),
            "q_group_abs_logit_mean": float(abs_cell[:, :3].mean()),
            "s_group_abs_logit_mean": float(abs_cell[:, 3:].mean()),
            "q2s3_abs_logit_mean": float(abs_cell[:, [TARGETS.index("Q2"), TARGETS.index("S3")]].mean()),
            "high_mixmin_cell_mass_frac": high_mix_mass,
            "high_mixmin_row_mass_frac": group_mass(abs_row, np.flatnonzero(high_mix_row)),
            "high_e72_failed_cell_mass_frac": high_e72_mass,
            "high_e72_failed_row_mass_frac": group_mass(abs_row, np.flatnonzero(high_e72_row)),
            "weighted_cell_corr_with_mixmin_move": mix_corr,
            "weighted_cell_corr_with_raw05_from_mixmin": raw_corr,
            "weighted_cell_corr_with_e72_failed_move": e72_corr,
            "weighted_row_corr_with_mixmin_row_move": row_mix_corr,
            "weighted_row_corr_with_e72_failed_row_move": row_e72_corr,
            "signed_row_mean": float(signed_row.mean()),
            "signed_row_abs_mean": float(np.abs(signed_row).mean()),
        }
        summary.update(ce_proxy_summary(context, candidate, base, train))
        candidate_rows.append(summary)

        for j, target in enumerate(TARGETS):
            thresh = implied_threshold(candidate[:, j], base[:, j])
            target_abs = abs_cell[:, j]
            target_rows.append(
                {
                    "candidate": name,
                    "target": target,
                    "mean_prob_move": float(prob_delta[:, j].mean()),
                    "mean_abs_prob_move": float(np.abs(prob_delta[:, j]).mean()),
                    "mean_logit_move": float(logit_delta[:, j].mean()),
                    "mean_abs_logit_move": float(target_abs.mean()),
                    "active_rows": int((target_abs > 1.0e-12).sum()),
                    "move_up_rate": float(np.mean(prob_delta[:, j] > 0)),
                    "threshold_for_candidate_to_win_weighted": float(
                        np.average(thresh[np.isfinite(thresh)], weights=target_abs[np.isfinite(thresh)])
                    )
                    if np.isfinite(thresh).any() and target_abs[np.isfinite(thresh)].sum() > 0
                    else np.nan,
                    "high_mixmin_cell_mass_frac": float(target_abs[high_mix_cell[:, j]].sum() / target_abs.sum())
                    if target_abs.sum() > 0
                    else 0.0,
                    "high_e72_failed_cell_mass_frac": float(target_abs[high_e72_cell[:, j]].sum() / target_abs.sum())
                    if target_abs.sum() > 0
                    else 0.0,
                    "ce_train_prior": float(np.mean(logloss_delta(candidate[:, j], base[:, j], float(train[target].mean())))),
                    "ce_subject_prior": float(
                        np.mean(logloss_delta(candidate[:, j], base[:, j], context[f"subject_prior_{target}"].to_numpy()))
                    ),
                    "ce_recent7_prior": float(
                        np.mean(logloss_delta(candidate[:, j], base[:, j], context[f"subject_recent7_{target}"].to_numpy()))
                    ),
                }
            )

        for col in group_cols:
            for value, idx in context.groupby(col, dropna=False).indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                if len(idx_arr) < 3:
                    continue
                context_rows.append(
                    {
                        "candidate": name,
                        "axis": col,
                        "value": str(value),
                        "n_rows": int(len(idx_arr)),
                        "mean_abs_logit_move": float(abs_row[idx_arr].mean()),
                        "movement_mass_frac": group_mass(abs_row, idx_arr),
                        "mean_signed_logit_move": float(signed_row[idx_arr].mean()),
                        "high_mixmin_row_rate": float(high_mix_row[idx_arr].mean()),
                        "high_e72_failed_row_rate": float(high_e72_row[idx_arr].mean()),
                    }
                )

        for col in numeric_context:
            corr_rows.append(
                {
                    "candidate": name,
                    "feature": col,
                    "weighted_corr_abs_row_move": weighted_corr(abs_row, context[col].to_numpy(dtype=float), abs_row),
                }
            )
        corr_rows.extend(
            [
                {
                    "candidate": name,
                    "feature": "mixmin_vs_a2c8_row_abs",
                    "weighted_corr_abs_row_move": row_mix_corr,
                },
                {
                    "candidate": name,
                    "feature": "e72_failed_row_abs",
                    "weighted_corr_abs_row_move": row_e72_corr,
                },
            ]
        )

    candidate_summary = pd.DataFrame(candidate_rows)
    e72_self_mass = float(
        candidate_summary.loc[
            candidate_summary["candidate"].eq("e72_failed_vs_mixmin"),
            "high_e72_failed_cell_mass_frac",
        ].iloc[0]
    )
    mix_self_mass = float(
        candidate_summary.loc[
            candidate_summary["candidate"].eq("mixmin_vs_a2c8"),
            "high_mixmin_cell_mass_frac",
        ].iloc[0]
    )
    candidate_summary["e72_failed_overlap_ratio"] = candidate_summary["high_e72_failed_cell_mass_frac"] / e72_self_mass
    candidate_summary["mixmin_overlap_ratio"] = candidate_summary["high_mixmin_cell_mass_frac"] / mix_self_mass
    candidate_summary["e72_failed_contamination_index"] = 0.5 * (
        candidate_summary["e72_failed_overlap_ratio"]
        + candidate_summary["weighted_row_corr_with_e72_failed_row_move"].clip(lower=0.0)
    )
    candidate_summary["mixmin_reversal_index"] = candidate_summary["mixmin_overlap_ratio"] * (
        -candidate_summary["weighted_cell_corr_with_mixmin_move"]
    ).clip(lower=0.0)

    return (
        candidate_summary,
        pd.DataFrame(target_rows),
        pd.DataFrame(context_rows),
        pd.DataFrame(corr_rows),
    )


def write_report(summary: pd.DataFrame, target: pd.DataFrame, context: pd.DataFrame, corr: pd.DataFrame) -> None:
    def fmt_float(x: float) -> str:
        if pd.isna(x):
            return "nan"
        return f"{x:.6g}"

    main_cols = [
        "candidate",
        "active_cells",
        "active_rows",
        "mean_abs_logit_move",
        "high_mixmin_cell_mass_frac",
        "high_e72_failed_cell_mass_frac",
        "e72_failed_contamination_index",
        "mixmin_reversal_index",
        "weighted_cell_corr_with_mixmin_move",
        "weighted_cell_corr_with_e72_failed_move",
        "ce_subject_prior_mean",
    ]
    lines: list[str] = []
    lines.append("# E88 Frontier Movement Attribution")
    lines.append("")
    lines.append("## Observe")
    lines.append("")
    lines.append("E86/E87 are locally healthy, but public feedback is pending. The unresolved question is whether these moves are aligned with the validated mixmin hidden-world movement or whether they resemble the failed E72 all-target contamination.")
    lines.append("")
    lines.append("## Candidate Movement Table")
    lines.append("")
    lines.append(e56.markdown_table(summary[main_cols]))
    lines.append("")
    lines.append("## Strongest Context Concentrations")
    lines.append("")
    for cand in ["mixmin_vs_a2c8", "e72_failed_vs_mixmin", "e86_vs_mixmin", "e87_inverse_top_vs_mixmin"]:
        top = context[context["candidate"].eq(cand)].sort_values("movement_mass_frac", ascending=False).head(4)
        lines.append(f"### {cand}")
        for _, r in top.iterrows():
            lines.append(
                f"- `{r['axis']}={r['value']}` rows `{int(r['n_rows'])}` mass `{fmt_float(r['movement_mass_frac'])}`, "
                f"mean abs logit `{fmt_float(r['mean_abs_logit_move'])}`, high-mix row rate `{fmt_float(r['high_mixmin_row_rate'])}`, "
                f"high-E72 row rate `{fmt_float(r['high_e72_failed_row_rate'])}`."
            )
        lines.append("")
    lines.append("## Target Axis Notes")
    lines.append("")
    for cand in ["e85_vs_mixmin", "e86_vs_mixmin", "e87_noq2_vs_mixmin", "e87_nooverstep_vs_mixmin", "e87_inverse_top_vs_mixmin"]:
        rows = target[target["candidate"].eq(cand)].sort_values("mean_abs_logit_move", ascending=False).head(4)
        desc = ", ".join(
            f"{r['target']} abs `{fmt_float(r['mean_abs_logit_move'])}` subjCE `{fmt_float(r['ce_subject_prior'])}`"
            for _, r in rows.iterrows()
        )
        lines.append(f"- `{cand}` dominant targets: {desc}.")
    lines.append("")
    lines.append("## Feature Correlation Notes")
    lines.append("")
    for cand in ["e86_vs_mixmin", "e87_noq2_vs_mixmin", "e87_nooverstep_vs_mixmin", "e87_inverse_top_vs_mixmin"]:
        rows = corr[corr["candidate"].eq(cand)].copy()
        rows["abs_corr"] = rows["weighted_corr_abs_row_move"].abs()
        rows = rows.sort_values("abs_corr", ascending=False).head(4)
        desc = ", ".join(
            f"{r['feature']} `{fmt_float(r['weighted_corr_abs_row_move'])}`" for _, r in rows.iterrows()
        )
        lines.append(f"- `{cand}` strongest row-move correlations: {desc}.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    e86 = summary.set_index("candidate").loc["e86_vs_mixmin"]
    e72 = summary.set_index("candidate").loc["e72_failed_vs_mixmin"]
    noq2 = summary.set_index("candidate").loc["e87_noq2_vs_mixmin"]
    noover = summary.set_index("candidate").loc["e87_nooverstep_vs_mixmin"]
    inv = summary.set_index("candidate").loc["e87_inverse_top_vs_mixmin"]
    lines.append(
        "- E86 is not an all-target replay of E72, but it is still E72-contamination-proximate: "
        f"cell overlap ratio `{fmt_float(e86['e72_failed_overlap_ratio'])}` and row correlation "
        f"`{fmt_float(e86['weighted_row_corr_with_e72_failed_row_move'])}` versus E72 self-reference "
        f"`{fmt_float(e72['weighted_row_corr_with_e72_failed_row_move'])}`."
    )
    lines.append(
        "- All E85/E86/E87 variants have negative signed correlation with the original mixmin-vs-a2c8 move, "
        "so this branch is better described as a second-order rollback/refinement of mixmin, not continuation of mixmin's first-order law."
    )
    lines.append(
        f"- The no-Q2 contrast is the cleanest public-risk split among E87 variants: contamination index "
        f"`{fmt_float(noq2['e72_failed_contamination_index'])}` versus E86 "
        f"`{fmt_float(e86['e72_failed_contamination_index'])}`. The no-overstep contrast lowers amplitude but keeps the same moved-cell geometry."
    )
    lines.append(
        f"- The inverse-top-prior contrast has the largest E72 contamination index "
        f"`{fmt_float(inv['e72_failed_contamination_index'])}`, so E88 demotes it from a safety candidate to a high-information diagnostic only."
    )
    lines.append("- Negative subject-prior CE proxies suggest the moves are not ordinary prevalence/prior correction; they are more likely hidden-world or combo-set corrections with public contamination risk.")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("E88 does not create a new submission. It supplies a risk lens for E86/E87 public feedback: compare whether the public winner follows mixmin-overlap, avoids E72-overlap, or concentrates in raw-domain/calendar blocks.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8_FILE).sort_values(KEYS).reset_index(drop=True)[KEYS].copy()
    context = make_context(sample)
    summary, target, context_summary, corr = candidate_summaries(sample, context)
    summary.to_csv(SUMMARY_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    context_summary.to_csv(CONTEXT_OUT, index=False)
    corr.to_csv(CORR_OUT, index=False)
    write_report(summary, target, context_summary, corr)
    print(
        {
            "candidates": int(len(summary)),
            "target_rows": int(len(target)),
            "context_rows": int(len(context_summary)),
            "corr_rows": int(len(corr)),
        }
    )


if __name__ == "__main__":
    main()
