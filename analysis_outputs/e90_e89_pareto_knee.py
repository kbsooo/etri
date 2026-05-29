#!/usr/bin/env python3
"""E90 Pareto-knee selector over E89 decontamination rows.

E89 selected the lowest E72-contamination strict row. This follow-up asks a
different question: is there a knee point that keeps most of E86's local
margin/hidden-world strength while still reducing E72 proximity below the
standard E85/no-Q2 safety controls?
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e89_e86_e72_decontamination_scan as e89  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCAN_IN = OUT / "e89_e86_e72_decontamination_scan.csv"
SCORES_OUT = OUT / "e90_e89_pareto_knee_scores.csv"
SUMMARY_OUT = OUT / "e90_e89_pareto_knee_summary.csv"
REPORT_OUT = OUT / "e90_e89_pareto_knee_report.md"
SUBMISSION_PREFIX = "submission_e90_e72pareto"


def safe_norm(value: float, low: float, high: float) -> float:
    span = high - low
    if abs(span) <= 1.0e-18:
        return 0.0
    return (value - low) / span


def score_candidates(scan: pd.DataFrame) -> pd.DataFrame:
    strict = scan[
        scan["nonanchor_evaluated"].fillna(False).astype(bool)
        & scan["strict_gate"].fillna(False).astype(bool)
    ].copy()

    e86 = scan[(scan["strategy"].eq("control")) & (scan["source"].eq("e86"))].iloc[0]
    e85 = scan[(scan["strategy"].eq("control")) & (scan["source"].eq("e85"))].iloc[0]
    noq2 = scan[(scan["strategy"].eq("control")) & (scan["source"].eq("noq2"))].iloc[0]
    low_contam = scan[scan["strict_gate"].fillna(False).astype(bool)].sort_values(
        ["e72_failed_contamination_index", "all_delta_vs_mixmin"]
    ).iloc[0]

    clean_threshold = min(
        float(e85["e72_failed_contamination_index"]),
        float(noq2["e72_failed_contamination_index"]),
    )

    rows: list[dict[str, float | str | bool]] = []
    for rec in strict.to_dict("records"):
        all_delta = float(rec["all_delta_vs_mixmin"])
        contamination = float(rec["e72_failed_contamination_index"])
        hidden = float(rec["hidden_q2s3_mean_minus_base"])
        world = float(rec["world_support_minus_base"])
        block = float(rec["block_q2s3_beats_base_rate"])
        tail = float(rec["block_q2s3_tail_safe_rate"])

        cleaner_than_controls = contamination < clean_threshold
        margin_ok = all_delta < -1.0e-5
        world_ok = world < 0.0
        hidden_ok = hidden < 0.0

        margin_retention = safe_norm(
            float(e85["all_delta_vs_mixmin"]) - all_delta,
            0.0,
            float(e85["all_delta_vs_mixmin"]) - float(e86["all_delta_vs_mixmin"]),
        )
        decontam_gain = safe_norm(
            float(e86["e72_failed_contamination_index"]) - contamination,
            0.0,
            float(e86["e72_failed_contamination_index"]) - float(low_contam["e72_failed_contamination_index"]),
        )
        hidden_retention = safe_norm(
            float(e85["hidden_q2s3_mean_minus_base"]) - hidden,
            0.0,
            float(e85["hidden_q2s3_mean_minus_base"]) - float(e86["hidden_q2s3_mean_minus_base"]),
        )
        world_retention = safe_norm(
            float(e85["world_support_minus_base"]) - world,
            0.0,
            float(e85["world_support_minus_base"]) - float(e86["world_support_minus_base"]),
        )

        projection_scope = rec.get("projection_scope", "")
        projection_penalty = 0.08 if isinstance(projection_scope, str) and projection_scope else 0.0
        e89_mincontam_bonus = 0.02 if rec["tag"] == low_contam["tag"] else 0.0
        row_coherence_bonus = 0.03 if rec["strategy"] == "row_e72_fallback" else 0.0

        pareto_score = (
            0.35 * np.clip(margin_retention, 0.0, 1.2)
            + 0.25 * np.clip(decontam_gain, 0.0, 1.2)
            + 0.15 * np.clip(world_retention, 0.0, 1.2)
            + 0.10 * np.clip(hidden_retention, 0.0, 1.2)
            + 0.10 * tail
            + 0.05 * block
            + row_coherence_bonus
            + e89_mincontam_bonus
            - projection_penalty
        )

        rows.append(
            {
                "tag": rec["tag"],
                "strategy": rec["strategy"],
                "source": rec.get("source", ""),
                "fallback": rec.get("fallback", ""),
                "row_quantile": rec.get("row_quantile", np.nan),
                "cell_quantile": rec.get("cell_quantile", np.nan),
                "beta": rec.get("beta", np.nan),
                "projection_scope": projection_scope,
                "pred_index": int(rec["pred_index"]),
                "cleaner_than_e85_noq2": bool(cleaner_than_controls),
                "eligible": bool(cleaner_than_controls and margin_ok and world_ok and hidden_ok),
                "pareto_score": float(pareto_score),
                "margin_retention_vs_e86_e85": float(margin_retention),
                "decontam_gain_vs_e86_to_min": float(decontam_gain),
                "hidden_retention_vs_e86_e85": float(hidden_retention),
                "world_retention_vs_e86_e85": float(world_retention),
                "all_delta_vs_mixmin": all_delta,
                "e72_failed_contamination_index": contamination,
                "hidden_q2s3_mean_minus_base": hidden,
                "world_support_minus_base": world,
                "block_q2s3_beats_base_rate": block,
                "block_q2s3_tail_safe_rate": tail,
                "mixmin_reversal_index": float(rec["mixmin_reversal_index"]),
            }
        )

    scored = pd.DataFrame(rows).sort_values(
        ["eligible", "pareto_score", "all_delta_vs_mixmin"],
        ascending=[False, False, True],
    )
    return scored


def materialize(scored: pd.DataFrame) -> Path | None:
    eligible = scored[scored["eligible"].astype(bool)].copy()
    if eligible.empty:
        return None

    selected = eligible.iloc[0]
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    _, preds, _, _, _ = e89.build_candidates(sample)
    out = sample[KEYS].copy()
    out[TARGETS] = preds[int(selected["pred_index"])]
    suffix = str(selected["tag"]).split("_")[-1]
    path = OUT / f"{SUBMISSION_PREFIX}_{suffix}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(scored: pd.DataFrame, submission_path: Path | None) -> None:
    selected = scored[scored["eligible"].astype(bool)].head(1)
    cols = [
        "strategy",
        "source",
        "fallback",
        "row_quantile",
        "cell_quantile",
        "pareto_score",
        "margin_retention_vs_e86_e85",
        "decontam_gain_vs_e86_to_min",
        "world_retention_vs_e86_e85",
        "hidden_retention_vs_e86_e85",
        "all_delta_vs_mixmin",
        "e72_failed_contamination_index",
        "world_support_minus_base",
        "hidden_q2s3_mean_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "tag",
    ]
    lines = [
        "# E90 E89 Pareto-Knee Selector",
        "",
        "## Observe",
        "",
        "E89 minimized E72 contamination, but its selected cell fallback sacrifices part of E86's hidden/world/block edge.",
        "",
        "## Wonder",
        "",
        "Is there a strict row that remains cleaner than both E85 and no-Q2 while preserving more of E86's local structural strength than the minimum-contamination E89 file?",
        "",
        "## Method",
        "",
        "- Reuse the E89 strict/deployable scan.",
        "- Keep only rows cleaner than both E85 and no-Q2 by E72 contamination index.",
        "- Score a Pareto knee over margin retention, E72 decontamination, hidden/world retention, block/tail safety, and a small row-coherence bonus.",
        "- Penalize projection-away rows because FH79 showed global projection is not the clean repair.",
        "",
        "## Selected Row",
        "",
        e56.markdown_table(selected[cols]) if len(selected) else "None.",
        "",
        "## Top Eligible Rows",
        "",
        e56.markdown_table(scored[scored["eligible"].astype(bool)][cols].head(15)),
        "",
        "## Decision",
        "",
    ]
    if submission_path is None:
        lines.append("No E90 Pareto-knee submission was materialized.")
    else:
        lines += [
            f"Materialized Pareto-knee candidate: `{submission_path.name}`.",
            "",
            "This is not safer than E89 on contamination alone. It is a balanced public sensor: it tests whether public rewards preserving E86 row-level structural strength after removing the worst E72-contaminated rows.",
        ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan = pd.read_csv(SCAN_IN)
    scored = score_candidates(scan)
    submission_path = materialize(scored)
    scored["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scored["materialized_submission"] = scored["tag"].astype(str).str.endswith(suffix)
    scored.to_csv(SCORES_OUT, index=False)
    summary_cols = [
        "strategy",
        "fallback",
        "eligible",
        "pareto_score",
        "all_delta_vs_mixmin",
        "e72_failed_contamination_index",
        "world_support_minus_base",
        "hidden_q2s3_mean_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "tag",
    ]
    scored.head(20)[summary_cols].to_csv(SUMMARY_OUT, index=False)
    write_report(scored, submission_path)
    selected = scored[scored["materialized_submission"].astype(bool)]
    print(
        {
            "rows": int(len(scored)),
            "eligible": int(scored["eligible"].sum()),
            "submission": str(submission_path) if submission_path is not None else None,
            "selected": selected[["strategy", "fallback", "row_quantile", "pareto_score"]].to_dict("records"),
        }
    )


if __name__ == "__main__":
    main()
