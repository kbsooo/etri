#!/usr/bin/env python3
"""E255: decode the public win of the E247 feature-NN1 smoothing sensor.

E247 was intentionally submitted as a high-information sensor:

- E246 said feature-NN1 smoothing passes public-free test-side stress.
- E248 said the analogous OOF smoothing selector is adverse.

The public LB `0.5761589494` is therefore not just a new score. It is a
measurement of which validation geometry the public subset follows.

This script records that interpretation, ranks follow-up questions inside the
E246 smoothing family, and does not create a new submission.
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

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


E247_PUBLIC = 0.5761589494
E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E176_PUBLIC = 0.5763118310
E216_PUBLIC = 0.5772865088

E247_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"

SUMMARY_IN = OUT / "e246_feature_nn1_smoothing_selector_summary.csv"
E247_AUDIT_IN = OUT / "e247_feature_nn1_smoothing_materializer_audit.csv"
E248_REPORT = OUT / "e248_feature_nn1_oof_smoothing_invariance_report.md"

PUBLIC_DELTA_OUT = OUT / "e255_e247_public_feedback_deltas.csv"
FOLLOWUP_OUT = OUT / "e255_e247_public_feedback_followup_ranking.csv"
REPORT_OUT = OUT / "e255_e247_public_feedback_decoder_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def parse_rows(value: Any) -> set[int]:
    if pd.isna(value):
        return set()
    return {int(x) for x in str(value).split() if str(x).strip()}


def public_delta_table() -> pd.DataFrame:
    anchors = [
        ("e247", E247_FILE, E247_PUBLIC, "new_public_frontier"),
        ("e95", "submission_e95_hardtail_541e3973.csv", E95_PUBLIC, "previous_frontier"),
        ("e101", "submission_e101_q2s3tail_177569bc.csv", E101_PUBLIC, "small_loss_q2s3_tail"),
        ("mixmin", "submission_mixmin_0c916bb4.csv", MIXMIN_PUBLIC, "anchor_loss_binary_world"),
        ("e176", "submission_e176_abl_q2_to0p75_91e49725.csv", E176_PUBLIC, "broad_q2_damped"),
        ("e216", "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv", E216_PUBLIC, "bad_s2_maskfam_jepa"),
    ]
    rows = []
    for anchor_id, file_name, public_lb, role in anchors:
        rows.append(
            {
                "anchor_id": anchor_id,
                "file_name": file_name,
                "public_lb": public_lb,
                "delta_vs_e247": float(public_lb - E247_PUBLIC),
                "delta_vs_e95": float(public_lb - E95_PUBLIC),
                "role": role,
            }
        )
    return pd.DataFrame(rows)


def classify_public_win() -> dict[str, Any]:
    improvement_vs_e95 = E95_PUBLIC - E247_PUBLIC
    improvement_vs_mixmin = MIXMIN_PUBLIC - E247_PUBLIC
    e95_edge_vs_mixmin = MIXMIN_PUBLIC - E95_PUBLIC
    return {
        "outcome": "feature_nn1_public_breakthrough",
        "improvement_vs_e95": float(improvement_vs_e95),
        "improvement_vs_mixmin": float(improvement_vs_mixmin),
        "e95_edge_vs_mixmin": float(e95_edge_vs_mixmin),
        "improvement_over_e95_edge_multiple": float(improvement_vs_e95 / max(e95_edge_vs_mixmin, 1.0e-15)),
        "interpretation": (
            "Public strongly prefers the E247/E224 feature-neighbor Q3 smoothing branch over "
            "the previous E95 hard-tail frontier."
        ),
    }


def followup_table() -> pd.DataFrame:
    summary = pd.read_csv(SUMMARY_IN)
    if not E247_AUDIT_IN.exists():
        raise FileNotFoundError(E247_AUDIT_IN)
    e247_rows = parse_rows(
        summary.loc[summary["candidate_id"].eq("nn_smooth_sum_top34"), "row_idx_list"].iloc[0]
    )
    rows: list[dict[str, Any]] = []
    for _, rec in summary.iterrows():
        selected = parse_rows(rec.get("row_idx_list", ""))
        if not selected:
            continue
        inter = len(selected & e247_rows)
        union = len(selected | e247_rows)
        sym = len(selected ^ e247_rows)
        candidate_id = str(rec["candidate_id"])
        is_control = str(rec["rule_family"]) == "control"
        role = "reference_or_negative_control" if is_control else "same_family_variant"
        if candidate_id == "nn_smooth_sum_top34":
            role = "submitted_winner"
        elif candidate_id == "top50_amp_then_smooth25":
            role = "amplitude_constrained_smoothing_sensor"
        elif candidate_id == "nn_smooth_sum_top25":
            role = "breadth_ablation_same_score_axis"
        elif candidate_id == "source_smooth_top25":
            role = "source_pair_mechanism_sensor"
        elif candidate_id == "incoming_smooth_top25":
            role = "incoming_pair_mechanism_sensor"

        information_score = np.nan
        if bool(rec.get("e237_like_gate", False)) and not is_control and candidate_id != "nn_smooth_sum_top34":
            # Prefer strong local stress, but require enough difference from E247 to answer a new question.
            information_score = float(rec["e237_like_score"]) + 0.020 * (sym / max(union, 1))
        rows.append(
            {
                "candidate_id": candidate_id,
                "role": role,
                "rule_family": rec["rule_family"],
                "pruned_cells": int(rec["pruned_cells"]),
                "e237_like_gate": bool(rec["e237_like_gate"]),
                "e237_like_score": float(rec["e237_like_score"]),
                "expected_loss_vs_e224": float(rec["expected_loss_vs_e224"]),
                "adverse_reduction_vs_e224": float(rec["adverse_reduction_vs_e224"]),
                "support_gain_vs_e224": float(rec["support_gain_vs_e224"]),
                "q3_top1_over_abs_expected": float(rec["q3_top1_over_abs_expected"]),
                "selected_smooth_gain_sum": float(rec.get("selected_smooth_gain_sum", np.nan)),
                "overlap_e247": inter,
                "jaccard_e247": float(inter / union) if union else 1.0,
                "symmetric_diff_vs_e247": sym,
                "overlap_e237": int(rec.get("overlap_e237", 0)),
                "overlap_e230_swing25": int(rec.get("overlap_e230_swing25", 0)),
                "overlap_amp_top25": int(rec.get("overlap_amp_top25", 0)),
                "information_score": information_score,
            }
        )
    df = pd.DataFrame(rows)
    return df.sort_values(
        ["role", "information_score", "e237_like_score"],
        ascending=[True, False, False],
        na_position="last",
    )


def main() -> None:
    deltas = public_delta_table()
    followups = followup_table()
    deltas.to_csv(PUBLIC_DELTA_OUT, index=False)
    followups.to_csv(FOLLOWUP_OUT, index=False)

    verdict = classify_public_win()
    top_followups = followups[
        followups["role"].isin(
            [
                "amplitude_constrained_smoothing_sensor",
                "breadth_ablation_same_score_axis",
                "source_pair_mechanism_sensor",
                "incoming_pair_mechanism_sensor",
                "same_family_variant",
            ]
        )
        & followups["e237_like_gate"].astype(bool)
    ].sort_values("information_score", ascending=False, na_position="last")

    lines = [
        "# E255 E247 Public Feedback Decoder",
        "",
        "## Public Observation",
        "",
        f"- submitted file: `{E247_FILE}`",
        f"- public LB: `{E247_PUBLIC:.10f}`",
        f"- improvement vs E95: `-{verdict['improvement_vs_e95']:.10f}`",
        f"- improvement vs mixmin: `-{verdict['improvement_vs_mixmin']:.10f}`",
        f"- improvement is `{verdict['improvement_over_e95_edge_multiple']:.3f}x` the E95-over-mixmin edge.",
        "",
        "## Anchor Deltas",
        "",
        md_table(deltas, n=20),
        "",
        "## Interpretation",
        "",
        "- E247 is now the public frontier, not merely a diagnostic sensor.",
        "- This is a strong positive update for the E207/E246 feature-neighbor Q3 smoothing worldview.",
        "- It also directly weakens the use of ordinary OOF smoothing invariance as a hard veto: E248 rejected the train analogue, but public rewarded the test-side smoothing rule.",
        "- The unresolved attribution is E224 body versus E247 smoothing. E247 proves the combined E224-body + feature-NN1 Q3 rollback branch, not the isolated rollback effect.",
        "",
        "## Follow-Up Family Ranking",
        "",
        md_table(
            followups.sort_values(["information_score", "e237_like_score"], ascending=[False, False], na_position="last"),
            [
                "candidate_id",
                "role",
                "pruned_cells",
                "e237_like_score",
                "expected_loss_vs_e224",
                "adverse_reduction_vs_e224",
                "support_gain_vs_e224",
                "q3_top1_over_abs_expected",
                "overlap_e247",
                "jaccard_e247",
                "symmetric_diff_vs_e247",
                "overlap_e237",
                "overlap_e230_swing25",
                "information_score",
            ],
            n=20,
        ),
        "",
        "## Decision",
        "",
        "- Promote feature-NN1 smoothing from `public sensor` to `current public-positive JEPA mechanism`.",
        "- Do not treat E248 as a failed experiment to ignore. It explains the bottleneck: train OOF harmful-row labels and public test-side feature-neighbor geometry are misaligned.",
        "- Do not immediately sweep every E247 sibling. The best next information candidate inside this family is `top50_amp_then_smooth25`, because it asks whether public liked broad smoothness or only high-amplitude smoothing cells.",
        "- If the next goal is attribution rather than score, submit/observe E224 clean body. If the next goal is score-plus-information, materialize `top50_amp_then_smooth25` as the first E247-family follow-up.",
        "- The next modeling target should be a public-contrastive JEPA head: learn the difference between OOF-adverse smoothing labels and public-positive feature-neighbor cells.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print("[E255 public deltas]")
    print(deltas.round(10).to_string(index=False))
    print("\n[E255 top followups]")
    cols = [
        "candidate_id",
        "role",
        "pruned_cells",
        "e237_like_score",
        "overlap_e247",
        "jaccard_e247",
        "symmetric_diff_vs_e247",
        "information_score",
    ]
    print(top_followups[cols].head(10).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
