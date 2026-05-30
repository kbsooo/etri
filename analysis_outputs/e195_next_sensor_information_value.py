#!/usr/bin/env python3
"""Compare E176 and E154 as the next public sensor.

E194 made the counter-world explicit: E176 first is robust unless the inherited
binary-world view is trusted much more than pair/shape/broad-body evidence.
E195 asks a different question: if we spend one public slot, which file gives a
cleaner decision tree over the live worldviews?
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def fmt(x: float | int | str | None) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    if isinstance(x, str):
        return x
    return f"{x:.9g}"


def markdown_table(df: pd.DataFrame) -> str:
    safe = df.copy()
    for col in safe.columns:
        safe[col] = safe[col].map(lambda x: fmt(x) if isinstance(x, (float, int)) else str(x))
        safe[col] = safe[col].str.replace("|", "\\|", regex=False)
    header = "| " + " | ".join(safe.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(safe.columns)) + " |"
    lines = [header, sep]
    for _, row in safe.iterrows():
        lines.append("| " + " | ".join(row.astype(str).tolist()) + " |")
    return "\n".join(lines)


def text_has(series: pd.Series, token: str) -> pd.Series:
    return series.fillna("").astype(str).str.contains(token, case=False, regex=False)


def classify_e176_bands(bands: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in bands.iterrows():
        outcome = row["outcome"]
        if outcome in {"q2_underopen_breakthrough", "clean_win", "micro_win"}:
            validates = "broad_q2_underopen"
            kills = "binary_world_counterprior_as_first_choice"
            action_class = "promote_e176"
        elif outcome in {"tie", "small_loss"}:
            validates = "hidden_label_resolution_bottleneck"
            kills = "expected_score_certification_for_e176"
            action_class = "ambiguous_or_shift_to_e154_by_question"
        else:
            validates = "binary_world_or_other_counterworld"
            kills = "partial_reopen_expected_score_lane"
            action_class = "demote_e176_route_e154_or_search"
        rows.append(
            {
                "sensor": "e176",
                "outcome": outcome,
                "public_lb_range": f"({fmt(row['public_lb_lo_exclusive'])}, {fmt(row['public_lb_hi_inclusive'])}]",
                "validates": validates,
                "kills_or_weakens": kills,
                "action_class": action_class,
                "routes_to_e154": int(
                    "e154" in str(row.get("candidate_to_test", "")).lower()
                    or "e154" in str(row.get("next_action", "")).lower()
                ),
                "forbids_same_family_tuning": int(bool(str(row.get("forbidden_action", "")).strip())),
                "next_action": row.get("next_action", ""),
            }
        )
    return pd.DataFrame(rows)


def classify_e154_bands(bands: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary[["outcome", "branch_status", "e155_gate", "candidate_to_test", "allowed_next", "forbidden"]]
    merged = bands.merge(summary, on="outcome", how="left")
    rows = []
    for _, row in merged.iterrows():
        outcome = row["outcome"]
        if outcome in {"breakthrough_win", "clean_win", "micro_win"}:
            validates = "repaired_branch"
            kills = "e176_first_priority_but_not_e176_worldview"
            action_class = "promote_e154"
        elif outcome in {"tie", "small_loss"}:
            validates = "repaired_branch_underresolved_or_added_body_question"
            kills = "full_e154_expected_score_certification"
            action_class = "e155_or_e144_component_branch"
        else:
            validates = "repaired_branch_failure"
            kills = "repaired_branch_siblings"
            action_class = "e144_or_representation_search"
        rows.append(
            {
                "sensor": "e154",
                "outcome": outcome,
                "public_lb_range": f"({fmt(row['public_lb_lo_exclusive'])}, {fmt(row['public_lb_hi_inclusive'])}]",
                "validates": validates,
                "kills_or_weakens": kills,
                "action_class": action_class,
                "routes_to_e176": 0,
                "routes_to_e155_or_e144": int(
                    "e155" in str(row.get("candidate_to_test", "")).lower()
                    or "e144" in str(row.get("candidate_to_test", "")).lower()
                    or "e155" in str(row.get("allowed_next", "")).lower()
                    or "e144" in str(row.get("allowed_next", "")).lower()
                ),
                "forbids_same_family_tuning": int(bool(str(row.get("forbidden", "")).strip())),
                "next_action": row.get("next_action_e154", row.get("allowed_next", "")),
            }
        )
    return pd.DataFrame(rows)


def build_pairwise_resolution() -> pd.DataFrame:
    e177_pairwise = read_csv("e177_e176_public_feedback_decoder_pairwise.csv")
    e158_pairwise = read_csv("e158_repaired_branch_public_decoder_pairwise.csv")

    e176_e154 = e177_pairwise.loc[
        e177_pairwise["new"].eq("e176_q2_underopen") & e177_pairwise["base"].eq("e154")
    ].iloc[0]
    e154_e144 = e158_pairwise.loc[e158_pairwise["left"].eq("e154") & e158_pairwise["right"].eq("e144")].iloc[0]
    e154_e155 = e158_pairwise.loc[e158_pairwise["left"].eq("e154") & e158_pairwise["right"].eq("e155")].iloc[0]

    return pd.DataFrame(
        [
            {
                "contrast": "e176_vs_e154",
                "question": "broad/Q2-underopen vs repaired-branch counterworld",
                "moved_cells": int(e176_e154["moved_cells"]),
                "moved_rows": int(e176_e154["moved_rows"]),
                "focus_expected_delta": float(e176_e154["expected_delta_focus_mean"]),
                "top1_swing": float(e176_e154["top1_swing"]),
                "cells_for_2e6_guard": int(e176_e154["cells_for_2e6_guard"]),
                "cells_for_e95_edge": int(e176_e154["cells_for_e95_edge"]),
                "readability": "public-readable but hard-label fragile",
            },
            {
                "contrast": "e154_vs_e144",
                "question": "full repaired branch vs unrepaired residual branch",
                "moved_cells": int(e154_e144["changed_cells_left_minus_right"]),
                "moved_rows": int(e154_e144["changed_rows_left_minus_right"]),
                "focus_expected_delta": float(e154_e144["local_all_minus_delta_left_minus_right"]),
                "top1_swing": np.nan,
                "cells_for_2e6_guard": np.nan,
                "cells_for_e95_edge": np.nan,
                "readability": "barely readable against E144",
            },
            {
                "contrast": "e154_vs_e155",
                "question": "full repaired branch vs lower-amplitude sibling",
                "moved_cells": int(e154_e155["changed_cells_left_minus_right"]),
                "moved_rows": int(e154_e155["changed_rows_left_minus_right"]),
                "focus_expected_delta": float(e154_e155["local_all_minus_delta_left_minus_right"]),
                "top1_swing": np.nan,
                "cells_for_2e6_guard": np.nan,
                "cells_for_e95_edge": np.nan,
                "readability": "not public-readable by E158 guard",
            },
        ]
    )


def build_summary(e176_map: pd.DataFrame, e154_map: pd.DataFrame, pairwise: pd.DataFrame) -> pd.DataFrame:
    e194_family = read_csv("e194_evidence_ledger_robustness_family_alone.csv")
    e194_thresh = read_csv("e194_evidence_ledger_robustness_thresholds.csv")
    binary_flip = float(
        e194_thresh.loc[
            e194_thresh["family_scaled"].eq("binary_world") & e194_thresh["challenger"].eq("e154"),
            "flip_multiplier",
        ].iloc[0]
    )
    pair_floor = float(
        e194_thresh.loc[
            e194_thresh["family_scaled"].eq("antisymmetric_pair_after_dropping_noncomparable_visible")
            & e194_thresh["challenger"].eq("e154"),
            "flip_multiplier",
        ].iloc[0]
    )
    e176_vs_e154 = pairwise.loc[pairwise["contrast"].eq("e176_vs_e154")].iloc[0]
    e154_vs_e144 = pairwise.loc[pairwise["contrast"].eq("e154_vs_e144")].iloc[0]
    e154_vs_e155 = pairwise.loc[pairwise["contrast"].eq("e154_vs_e155")].iloc[0]

    rows = [
        {
            "sensor": "e176",
            "file": "analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv",
            "primary_question": "Does broad/Q2-underopen pair/shape/body evidence beat the binary-world counterprior?",
            "validated_world_if_win": "broad_q2_underopen",
            "main_counterworld_if_loss": "e154_repaired_branch",
            "bands": len(e176_map),
            "win_bands": int(e176_map["outcome"].isin(["q2_underopen_breakthrough", "clean_win", "micro_win"]).sum()),
            "adverse_bands": int(e176_map["outcome"].isin(["e101_worse_mixmin_safe", "branch_loss", "hard_fail"]).sum()),
            "counterworld_route_bands": int(e176_map["routes_to_e154"].sum()),
            "same_family_forbidden_bands": int(e176_map["forbids_same_family_tuning"].sum()),
            "readable_counterworld_contrast": "yes",
            "contrast_cells": int(e176_vs_e154["moved_cells"]),
            "contrast_expected_delta": float(e176_vs_e154["focus_expected_delta"]),
            "information_value_read": "dominant first sensor because win validates current top worldview and loss routes to explicit E154 counterworld",
            "decision_condition": f"prefer unless binary-world is trusted >{binary_flip:.3f}x or pair geometry <{pair_floor:.3f}x after removing non-comparable visible evidence",
            "sensor_rank": 1,
        },
        {
            "sensor": "e154",
            "file": "analysis_outputs/submission_e154_s3repair_9f2e2e73.csv",
            "primary_question": "Is the repaired E144-collinear S3 active-boundary branch public-real?",
            "validated_world_if_win": "repaired_branch",
            "main_counterworld_if_loss": "e144_or_representation_search",
            "bands": len(e154_map),
            "win_bands": int(e154_map["outcome"].isin(["breakthrough_win", "clean_win", "micro_win"]).sum()),
            "adverse_bands": int(e154_map["outcome"].isin(["branch_loss", "hard_fail"]).sum()),
            "counterworld_route_bands": 0,
            "same_family_forbidden_bands": int(e154_map["forbids_same_family_tuning"].sum()),
            "readable_counterworld_contrast": "partial",
            "contrast_cells": int(e154_vs_e144["moved_cells"]),
            "contrast_expected_delta": float(e154_vs_e144["focus_expected_delta"]),
            "information_value_read": "good alternate-world sensor but does not directly resolve the current E176 broad/Q2-underopen worldview",
            "decision_condition": f"prefer first only under high-binary/low-pair worldview; e154-vs-e155 is not readable ({float(e154_vs_e155['focus_expected_delta']):.9g})",
            "sensor_rank": 2,
        },
    ]
    family_note = "; ".join(
        f"{r.family}:{r.winner_if_alone}" for r in e194_family.itertuples(index=False)
    )
    out = pd.DataFrame(rows)
    out["family_alone_context"] = family_note
    return out


def write_report(summary: pd.DataFrame, band_map: pd.DataFrame, pairwise: pd.DataFrame) -> Path:
    path = OUT / "e195_next_sensor_information_value_report.md"
    top = summary.sort_values("sensor_rank").iloc[0]
    body = f"""# E195 Next Sensor Information Value

## Question

After E194, should the next public slot still be E176, or is E154 the better sensor because it represents the strongest counter-world?

## Result

E176 remains the better first sensor. It is not just the higher-balance file; it gives the cleaner decision tree. If E176 wins, it validates the current broad/Q2-underopen worldview. If E176 loses badly, the decoder already routes to E154 or representation search and forbids same-family keep-factor tuning. E154 is valuable, but it tests only the repaired E144-collinear branch and leaves the E176 broad worldview mostly unobserved.

Recommended first sensor: `{top['file']}`.

## Sensor Summary

{markdown_table(summary)}

## Pairwise Resolution

{markdown_table(pairwise)}

## Band Action Map

{markdown_table(band_map)}

## Interpretation

- E176-vs-E154 is public-readable but hard-label fragile: `1027` cells over `238` rows, focus expected delta `{fmt(float(pairwise.loc[pairwise['contrast'].eq('e176_vs_e154'), 'focus_expected_delta'].iloc[0]))}`, and only `1` cell for the `2e-6` guard.
- E154-vs-E144 is barely readable; E154-vs-E155 is not readable by the E158 guard. That makes E154 useful as a repaired-branch public question, but less efficient as the first slot after E194.
- E176 first is a directional bet: pair/shape/broad-body evidence should be trusted more than the inherited binary-world counterprior. E154 first is coherent only if the binary-world view is intentionally promoted above the E194 flip condition.

## Decision

No new submission is created. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next single public sensor. If its public LB lands in an adverse E177 band, switch to E154 or representation search according to the pre-registered decoder instead of tuning another E176 sibling.
"""
    path.write_text(body, encoding="utf-8")
    return path


def main() -> None:
    e176_bands = read_csv("e177_e176_public_feedback_decoder_bands.csv")
    e154_bands = read_csv("e158_repaired_branch_public_decoder_bands.csv")
    e154_summary = read_csv("e160_e154_postfeedback_interpreter_summary.csv")

    e176_map = classify_e176_bands(e176_bands)
    e154_map = classify_e154_bands(e154_bands, e154_summary)
    e154_map = e154_map.rename(columns={"routes_to_e155_or_e144": "routes_to_branch_control"})
    e176_map["routes_to_branch_control"] = 0
    e154_map["routes_to_e154"] = 0
    band_map = pd.concat([e176_map, e154_map], ignore_index=True, sort=False)

    pairwise = build_pairwise_resolution()
    summary = build_summary(e176_map, e154_map, pairwise)

    summary_path = OUT / "e195_next_sensor_information_value_summary.csv"
    band_path = OUT / "e195_next_sensor_information_value_band_map.csv"
    pairwise_path = OUT / "e195_next_sensor_information_value_pairwise.csv"
    summary.to_csv(summary_path, index=False)
    band_map.to_csv(band_path, index=False)
    pairwise.to_csv(pairwise_path, index=False)
    report_path = write_report(summary, band_map, pairwise)

    print("wrote", summary_path)
    print("wrote", band_path)
    print("wrote", pairwise_path)
    print("wrote", report_path)
    print(summary[["sensor", "sensor_rank", "counterworld_route_bands", "contrast_expected_delta", "information_value_read"]].to_string(index=False))


if __name__ == "__main__":
    main()
