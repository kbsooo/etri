#!/usr/bin/env python3
"""E277: matched-placebo-resistant gate for q-sleep diary candidates.

E276 showed that the old E272/E275 promotion rule is too easy: shuffled E275
placebos often pass. This script turns that failure into a stricter rule.

For every semantic q-sleep candidate, generate matched null candidates that keep
the exact candidate logit-delta distribution but destroy row/state alignment by
shuffling within row, subject, or dateblock groups. A candidate is promoted only
if the real row-aligned tensor beats its own null distribution.

No new public LB is used.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    build_features,
    evaluate_models,
    movement_anatomy,
    score_candidates,
    selected_models,
)
from e276_q_sleep_story_ablation_placebo_audit import (  # noqa: E402
    FEATURE_PATH,
    aligned_meta,
    materialize_variants,
    shuffled_candidate,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 277
N_REPS = 7

SCORES_OUT = OUT / "e277_placebo_resistant_qsleep_gate_scores.csv"
NULLS_OUT = OUT / "e277_placebo_resistant_qsleep_gate_nulls.csv"
SUMMARY_OUT = OUT / "e277_placebo_resistant_qsleep_gate_summary.csv"
ANATOMY_OUT = OUT / "e277_placebo_resistant_qsleep_gate_anatomy.csv"
REPORT_OUT = OUT / "e277_placebo_resistant_qsleep_gate_report.md"


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def candidate_slug(file_name: str) -> str:
    stem = Path(file_name).stem
    stem = stem.replace("submission_e276_", "").replace("submission_e275_", "")
    keep = []
    for char in stem:
        keep.append(char if char.isalnum() else "_")
    return "".join(keep)[:52].strip("_")


def candidate_pool(variants: pd.DataFrame) -> pd.DataFrame:
    actual = variants[~variants["variant_type"].eq("shuffle_placebo")].copy()
    # Keep the inverse control in the audit as a sanity check, but it cannot be
    # promoted because it is not a semantic candidate.
    return actual.reset_index(drop=True)


def generate_matched_nulls(actual: pd.DataFrame) -> pd.DataFrame:
    base = load_sub(CURRENT)
    features = pd.read_parquet(FEATURE_PATH)
    meta = aligned_meta(features, base)
    rows: list[dict[str, object]] = []
    for actual_idx, rec in actual.reset_index(drop=True).iterrows():
        source = str(rec["basename"])
        candidate = load_sub(source)
        slug = candidate_slug(source)
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_REPS):
                seed = RNG_SEED + 1009 * actual_idx + 97 * rep + {"row": 0, "subject": 1, "dateblock": 2}[mode]
                null_id = f"e277null_{slug}_{mode}_r{rep}"
                null_file = shuffled_candidate(base, candidate, meta, null_id, mode, seed)
                rows.append(
                    {
                        "source_basename": source,
                        "null_basename": null_file,
                        "mode": mode,
                        "rep": rep,
                        "seed": seed,
                    }
                )
    nulls = pd.DataFrame(rows)
    nulls.to_csv(NULLS_OUT, index=False)
    return nulls


def audit_files(actual: pd.DataFrame, nulls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    files = [CURRENT]
    files.extend(actual["basename"].astype(str).tolist())
    files.extend(nulls["null_basename"].astype(str).tolist())
    deduped: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        if file_name not in seen:
            seen.add(file_name)
            deduped.append(file_name)

    candidates = build_features(deduped, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, candidates, model_df)
    anatomy = movement_anatomy(deduped, sample)
    scores.to_csv(SCORES_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return scores, anatomy, selected_models(model_df)


def make_summary(scores: pd.DataFrame, actual: pd.DataFrame, nulls: pd.DataFrame) -> pd.DataFrame:
    actual_scores = scores.merge(actual, on="basename", how="inner")
    null_scores = scores.merge(nulls, left_on="basename", right_on="null_basename", how="inner")
    rows: list[dict[str, object]] = []
    for _, rec in actual_scores.iterrows():
        base_name = str(rec["basename"])
        matched = null_scores[null_scores["source_basename"].eq(base_name)].copy()
        if matched.empty:
            continue
        actual_p90 = float(rec["pred_delta_vs_current_p90"])
        actual_mean = float(rec["pred_delta_vs_current_mean"])
        null_p90 = matched["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        null_mean = matched["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        strict_null = matched["strict_promote_gate"].astype(bool).to_numpy()
        p90_dominance = float(np.mean(actual_p90 < null_p90))
        mean_dominance = float(np.mean(actual_mean < null_mean))
        mode_dominance = {}
        mode_strict = {}
        mode_best_p90 = {}
        for mode, group in matched.groupby("mode"):
            g_p90 = group["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_dominance[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < g_p90))
            mode_strict[f"{mode}_null_strict_rate"] = float(group["strict_promote_gate"].astype(bool).mean())
            mode_best_p90[f"{mode}_best_null_p90"] = float(np.min(g_p90))

        null_p90_q20 = float(np.quantile(null_p90, 0.20))
        null_p90_median = float(np.median(null_p90))
        null_mean_q20 = float(np.quantile(null_mean, 0.20))
        null_strict_rate = float(np.mean(strict_null))
        worst_mode_dom = float(min(mode_dominance.values())) if mode_dominance else 0.0
        real_beats_null_gate = bool(
            bool(rec["strict_promote_gate"])
            and str(rec["variant_type"]) != "inverse_control"
            and p90_dominance >= 0.80
            and mean_dominance >= 0.70
            and worst_mode_dom >= 0.60
            and null_strict_rate <= 0.20
            and actual_p90 <= null_p90_q20 - 1.0e-6
        )
        if real_beats_null_gate:
            decision = "placebo_resistant_promote"
        elif bool(rec["strict_promote_gate"]) and null_strict_rate > 0.20:
            decision = "blocked_by_placebo_promotes"
        elif bool(rec["strict_promote_gate"]) and p90_dominance < 0.80:
            decision = "blocked_by_null_dominance"
        elif bool(rec["strict_promote_gate"]):
            decision = "blocked_by_mixed_placebo"
        else:
            decision = str(rec["promotion_decision"])

        rows.append(
            {
                "basename": base_name,
                "variant_type": rec.get("variant_type", ""),
                "family_tested": rec.get("family_tested", ""),
                "axis_kind_tested": rec.get("axis_kind_tested", ""),
                "axis_count": rec.get("axis_count", np.nan),
                "old_promotion_decision": rec["promotion_decision"],
                "old_strict_promote": bool(rec["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(rec["pred_beats_current_rate"]),
                "null_count": int(len(matched)),
                "null_strict_rate": null_strict_rate,
                "null_p90_q20": null_p90_q20,
                "null_p90_median": null_p90_median,
                "null_p90_best": float(np.min(null_p90)),
                "null_mean_q20": null_mean_q20,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode_dom,
                "placebo_adjusted_p90_vs_median": actual_p90 - null_p90_median,
                "placebo_adjusted_p90_vs_best": actual_p90 - float(np.min(null_p90)),
                "placebo_resistant_gate": real_beats_null_gate,
                "e277_decision": decision,
                **mode_dominance,
                **mode_strict,
                **mode_best_p90,
            }
        )
    summary = pd.DataFrame(rows).sort_values(
        ["placebo_resistant_gate", "p90_dominance", "actual_p90"],
        ascending=[False, False, True],
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    return summary


def write_report(summary: pd.DataFrame, scores: pd.DataFrame, nulls: pd.DataFrame, selected: pd.DataFrame, anatomy: pd.DataFrame) -> None:
    promoted = summary[summary["placebo_resistant_gate"].astype(bool)].copy() if not summary.empty else pd.DataFrame()
    old_strict = int(summary["old_strict_promote"].sum()) if not summary.empty else 0
    placebo_blocked = int(summary["e277_decision"].eq("blocked_by_placebo_promotes").sum()) if not summary.empty else 0
    candidate_rows = [
        "basename",
        "variant_type",
        "family_tested",
        "axis_kind_tested",
        "old_promotion_decision",
        "e277_decision",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "worst_mode_p90_dominance",
        "placebo_adjusted_p90_vs_median",
        "placebo_adjusted_p90_vs_best",
    ]
    null_mode = (
        scores.merge(nulls, left_on="basename", right_on="null_basename", how="inner")
        .groupby(["source_basename", "mode"], dropna=False)
        .agg(
            nulls=("basename", "size"),
            strict_rate=("strict_promote_gate", lambda x: float(np.asarray(x, dtype=bool).mean())),
            best_p90=("pred_delta_vs_current_p90", "min"),
            median_p90=("pred_delta_vs_current_p90", "median"),
            mean_p90=("pred_delta_vs_current_p90", "mean"),
        )
        .reset_index()
        .sort_values(["strict_rate", "best_p90"], ascending=[False, True])
    )
    anatomy_cols = [
        "basename",
        "changed_cells_vs_current",
        "changed_rows_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
    ]

    if len(promoted):
        decision = "At least one q-sleep semantic candidate beats matched placebos. Review the promoted rows before any public submission."
    else:
        decision = "No q-sleep semantic candidate beats matched placebos. E275/E276 remain diagnostic; do not submit from this branch yet."

    lines = [
        "# E277 Placebo-Resistant Q-Sleep Gate",
        "",
        "## Question",
        "",
        "Can any E275/E276 q-sleep diary-energy candidate beat a matched null distribution that preserves its movement magnitude but destroys row/state alignment?",
        "",
        "## Promotion Rule",
        "",
        "A candidate must pass the old strict gate and also beat its own row/subject/dateblock shuffle nulls:",
        "",
        "- p90 dominance over all nulls >= `0.80`;",
        "- mean dominance over all nulls >= `0.70`;",
        "- worst per-mode p90 dominance >= `0.60`;",
        "- null strict-promote rate <= `0.20`;",
        "- actual p90 at least `1e-6` better than null p90 q20;",
        "- inverse controls cannot promote.",
        "",
        "## Summary",
        "",
        f"- semantic/control candidates tested: `{len(summary)}`",
        f"- matched null files generated: `{len(nulls)}`",
        f"- selected E272-style selector models: `{len(selected)}`",
        f"- old strict-promote candidates: `{old_strict}`",
        f"- old strict candidates blocked by placebo-promote rate: `{placebo_blocked}`",
        f"- E277 placebo-resistant promotes: `{len(promoted)}`",
        "",
        "## Candidate Results",
        "",
        md_table(summary[candidate_rows], n=50) if not summary.empty else "_empty_",
        "",
        "## Null Mode Stress",
        "",
        md_table(null_mode, n=60),
        "",
        "## Movement Anatomy Of Actual Candidates",
        "",
        md_table(anatomy[anatomy["basename"].isin(summary["basename"])][anatomy_cols].sort_values("l1_logit_delta_vs_current", ascending=False), n=40) if not summary.empty else "_empty_",
        "",
        "## Decision",
        "",
        decision,
        "",
        "## Next Action",
        "",
        "Build a row-alignment objective, not another amplitude ladder: the real JEPA/mobility/Q3 candidate must be trained or gated to maximize distance from matched row/subject/dateblock shuffle nulls.",
        "",
        "## Files",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{SCORES_OUT.name}`",
        f"- `{NULLS_OUT.name}`",
        f"- `{ANATOMY_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    _, variants, _ = materialize_variants()
    actual = candidate_pool(variants)
    nulls = generate_matched_nulls(actual)
    scores, anatomy, selected = audit_files(actual, nulls)
    summary = make_summary(scores, actual, nulls)
    write_report(summary, scores, nulls, selected, anatomy)
    print(REPORT_OUT)
    print(
        summary[
            [
                "basename",
                "old_promotion_decision",
                "e277_decision",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "worst_mode_p90_dominance",
                "placebo_adjusted_p90_vs_best",
            ]
        ].head(30).round(9).to_string(index=False)
    )


if __name__ == "__main__":
    main()
