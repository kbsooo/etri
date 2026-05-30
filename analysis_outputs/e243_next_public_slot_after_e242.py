#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

E95_BEST = 0.5762913298
E216_FAIL = 0.5772865088


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def first_row(df: pd.DataFrame, **matches: object) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for col, value in matches.items():
        mask &= df[col].astype(str).eq(str(value))
    rows = df.loc[mask]
    if rows.empty:
        raise ValueError(f"No row for {matches}")
    return rows.iloc[0]


def fmt(x: object) -> str:
    if pd.isna(x):
        return ""
    if isinstance(x, float):
        return f"{x:.9f}"
    return str(x)


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = []
    rows.append("| " + " | ".join(cols) + " |")
    rows.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in df.iterrows():
        vals = [fmt(row[col]).replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def analysis_path(name: object) -> str:
    text = str(name)
    if text.startswith("analysis_outputs/"):
        return text
    return f"analysis_outputs/{text}"


def main() -> None:
    e224 = read_csv("e224_e211_q3_scale_pareto_selected.csv").iloc[0]
    e237 = read_csv("e237_cell_decisive_jepa_target_selected.csv").iloc[0]
    e242_rank = read_csv("e242_e237_oof_to_test_transfer_rank_audit.csv")
    e242_gate = read_csv("e242_e237_oof_to_test_transfer_gate_summary.csv")
    e229 = read_csv("e229_next_public_slot_decision_summary.csv")
    e226 = read_csv("e226_noncollinear_candidate_scan_summary.csv")
    e228 = read_csv("e228_triworld_conflict_atlas_summary.csv")
    e230 = read_csv("e230_e224_support_tail_prune_audit_selected.csv")

    e166 = first_row(e226, file_name="submission_e166_broadsurv_s0p01_d8bfa94b.csv")
    e154 = first_row(e228, tag="e154")
    e224_decision = first_row(e229, candidate="e224")

    tail_auc_rank = first_row(e242_rank, rank_by="oof_tail_auc")
    oof_gain_rank = first_row(e242_rank, rank_by="oof_gain_vs_full")
    support_rank = first_row(e242_rank, rank_by="support_gain_vs_e224")
    topcell_rank = first_row(e242_rank, rank_by="q3_top1_over_abs_expected")
    gate_true = first_row(e242_gate, group="gate_true")
    gate_false = first_row(e242_gate, group="gate_false")
    e230_risk = first_row(e230, candidate_id="q3_risktop21_drop")
    e230_swing = first_row(e230, candidate_id="q3_swingtop25_drop")

    decisions = [
        {
            "candidate": "e237_learned_q3_tail",
            "submission": analysis_path(e237["submission_file"]),
            "public_role": "improvement_biased_jepa_tail_sensor",
            "one_file_rank_if_improvement_biased_jepa": 1,
            "one_file_rank_if_clean_jepa_ablation": 2,
            "one_file_rank_if_non_jepa_escape": 3,
            "hidden_world_bet": "A JEPA-style high-impact cell target can identify the Q3 cells where E224's capped Q3 residual should be rolled back, while preserving the S4 body.",
            "why_live_after_e242": (
                "E242 says the top file is not an average-OOF winner "
                f"(rank {int(oof_gain_rank['top_e237_rank'])}/120 by OOF gain) but is rank "
                f"{int(tail_auc_rank['top_e237_rank'])}/120 by OOF tail-AUC, rank "
                f"{int(support_rank['top_e237_rank'])}/120 by support gain, and rank "
                f"{int(topcell_rank['top_e237_rank'])}/120 by Q3 top-cell safety."
            ),
            "not_recommended_when": "The public question is the clean unpruned capped-Q3/S4 JEPA body; E237 pre-answers that by pruning Q3.",
            "public_decoder": "python3 analysis_outputs/e238_e237_public_feedback_decoder.py --score <PUBLIC_LB>",
            "expected_focus_vs_e95": float(e237["actual_expected_focus"]),
            "expected_loss_vs_e224": float(e237["expected_loss_vs_e224"]),
            "adverse_reduction_vs_e224": float(e237["adverse_reduction_vs_e224"]),
            "support_gain_vs_e224": float(e237["support_gain_vs_e224"]),
            "q3_top1_over_abs_expected": float(e237["q3_top1_over_abs_expected"]),
            "q3_dropped_cells": int(e237["q3_dropped_cells"]),
            "s4_dropped_cells": int(e237["s4_dropped_cells"]),
            "collapse_guard_vs_e216": E216_FAIL,
            "primary_failure_read": "A loss worse than mixmin rejects this learned Q3-tail family, not all JEPA representations.",
        },
        {
            "candidate": "e224_clean_capped_q3_s4_jepa",
            "submission": analysis_path(e224["submission_file"]),
            "public_role": "clean_unpruned_jepa_body_sensor",
            "one_file_rank_if_improvement_biased_jepa": 2,
            "one_file_rank_if_clean_jepa_ablation": 1,
            "one_file_rank_if_non_jepa_escape": 2,
            "hidden_world_bet": "E211's S4 body plus capped Q3 residual is public-aligned despite E216's S2 masked-family failure.",
            "why_live_after_e242": (
                "E224 remains the cleanest direct JEPA translator because it is low-cosine to E216 "
                f"({float(e224_decision['cos_vs_e216']):.6f}) and has a fixed E225 routebook."
            ),
            "not_recommended_when": "The next slot must maximize immediate upside rather than isolate whether the unpruned JEPA body works.",
            "public_decoder": "python3 analysis_outputs/e225_e224_public_feedback_decoder.py --score <PUBLIC_LB>",
            "expected_focus_vs_e95": float(e224["expected_focus"]),
            "expected_loss_vs_e224": 0.0,
            "adverse_reduction_vs_e224": 0.0,
            "support_gain_vs_e224": 0.0,
            "q3_top1_over_abs_expected": float(e224["q3_top1_over_abs_expected"]),
            "q3_dropped_cells": 0,
            "s4_dropped_cells": 0,
            "collapse_guard_vs_e216": E216_FAIL,
            "primary_failure_read": "A loss demotes the current capped-Q3/S4 probability translator and sends JEPA back to target-design work.",
        },
        {
            "candidate": "e166_independent_broad_survivor",
            "submission": analysis_path(e166["file_name"]),
            "public_role": "independent_non_jepa_broad_world_sensor",
            "one_file_rank_if_improvement_biased_jepa": 3,
            "one_file_rank_if_clean_jepa_ablation": 3,
            "one_file_rank_if_non_jepa_escape": 1,
            "hidden_world_bet": "The safety atlas is overconservative and broad survivor edge/between-train-runs context is public-real outside the E224/E154 body.",
            "why_live_after_e242": f"Nearly orthogonal to E224 (cos {float(e166['cos_vs_e224']):.6f}) and not an E216 S2 neighbor (cos {float(e166['cos_vs_e216']):.6f}).",
            "not_recommended_when": "The next slot is explicitly meant to use JEPA rather than leave the family.",
            "public_decoder": "python3 analysis_outputs/e227_e166_public_feedback_decoder.py --score <PUBLIC_LB>",
            "expected_focus_vs_e95": float(e166["expected_focus"]),
            "expected_loss_vs_e224": pd.NA,
            "adverse_reduction_vs_e224": pd.NA,
            "support_gain_vs_e224": pd.NA,
            "q3_top1_over_abs_expected": pd.NA,
            "q3_dropped_cells": pd.NA,
            "s4_dropped_cells": pd.NA,
            "collapse_guard_vs_e216": E216_FAIL,
            "primary_failure_read": "A loss says broad survivor/E72-active warnings were causal, not that the E237 Q3-tail law is false.",
        },
        {
            "candidate": "e154_conservative_repaired_branch",
            "submission": analysis_path(e154["file_name"]),
            "public_role": "conservative_repaired_body_counterworld",
            "one_file_rank_if_improvement_biased_jepa": 4,
            "one_file_rank_if_clean_jepa_ablation": 4,
            "one_file_rank_if_non_jepa_escape": 4,
            "hidden_world_bet": "The E144/E154 repaired S3 active-boundary body is the safer branch after JEPA and broad-world sensors are demoted.",
            "why_live_after_e242": f"Useful as a conservative counterfactual, but E224 already covers most of its same-sign body; cos_vs_e224 {float(e154['cos_vs_e224']):.6f}.",
            "not_recommended_when": "The next slot should maximize new information; E154 is partly inherited by E224.",
            "public_decoder": "python3 analysis_outputs/e160_e154_postfeedback_interpreter.py --score <PUBLIC_LB>",
            "expected_focus_vs_e95": pd.NA,
            "expected_loss_vs_e224": pd.NA,
            "adverse_reduction_vs_e224": pd.NA,
            "support_gain_vs_e224": pd.NA,
            "q3_top1_over_abs_expected": pd.NA,
            "q3_dropped_cells": pd.NA,
            "s4_dropped_cells": pd.NA,
            "collapse_guard_vs_e216": E216_FAIL,
            "primary_failure_read": "A loss closes the repaired branch; a win would be a conservative body signal rather than a new JEPA result.",
        },
    ]

    decision_df = pd.DataFrame(decisions)
    decision_path = OUT / "e243_next_public_slot_after_e242_decision.csv"
    decision_df.to_csv(decision_path, index=False)

    contrasts = [
        {
            "contrast": "e237_vs_e224",
            "claim_tested": "Does the learned high-impact Q3 cell target improve the clean capped-Q3/S4 JEPA tensor?",
            "evidence_for": (
                f"Only {int(e237['q3_dropped_cells'])} Q3 cells are changed; expected_loss_vs_e224 "
                f"{float(e237['expected_loss_vs_e224']):.9f}; adverse_reduction "
                f"{float(e237['adverse_reduction_vs_e224']):.9f}; support_gain {float(e237['support_gain_vs_e224']):.9f}."
            ),
            "evidence_against": "E237 and E224 are highly collinear at full-tensor level; without E224 public score, a tie/small loss is underidentified.",
            "decision_rule": "Use E237 for improvement-biased JEPA tail test; use E224 for clean body ablation.",
        },
        {
            "contrast": "e237_vs_e230_hand_prune",
            "claim_tested": "Is E237 a learned version of the Q3 hand-prune or a different tail law?",
            "evidence_for": (
                f"E237 overlaps E230 risk21 by {int(e237['e230_q3_risk_top21_overlap'])}; "
                f"E230 risk expected_loss_vs_e224 {float(e230_risk['expected_loss_vs_e224']):.9f}; "
                f"E230 swing expected_loss_vs_e224 {float(e230_swing['expected_loss_vs_e224']):.9f}."
            ),
            "evidence_against": "Overlap is partial; E237 uses OOF tail labels, while E230 is public-free hand energy.",
            "decision_rule": "Do not submit E230 before E224/E237 feedback unless explicitly testing hand-prune counterfactual.",
        },
        {
            "contrast": "e237_vs_simple_residual_pc10",
            "claim_tested": "Can a simple E208 residual-energy rule replace the learned E237 cell target?",
            "evidence_for": "E240 simple_pc10_top25 passed local E237-like stress and overlapped E237 14/25.",
            "evidence_against": "E241 rejected it on train OOF Q3 benefit: score_pc10 top10 drop delta +0.001867628 and split-stress +0.002633171.",
            "decision_rule": "No simple-PC10 submission; residual energy is a motif/diagnostic, not a translator.",
        },
        {
            "contrast": "e224_vs_e166",
            "claim_tested": "Are the live JEPA and broad-world sensors redundant?",
            "evidence_for": f"E224/E166 cosine {float(e166['cos_vs_e224']):.6f}; top-level routebooks ask different public questions.",
            "evidence_against": "Both have low support probability around 0.466, so both remain hidden-label-tail risky.",
            "decision_rule": "Do not blend before feedback; choose by the public question.",
        },
        {
            "contrast": "e224_vs_e154",
            "claim_tested": "Is E154 an independent next public sensor?",
            "evidence_for": "E154 is conservative and has an existing interpreter.",
            "evidence_against": "E154 is partly inherited by E224; E228 says E154 active cells are fully inside E224 active cells.",
            "decision_rule": "Keep E154 conditional after JEPA/broad attribution, not first if information value is the goal.",
        },
        {
            "contrast": "e237_gate_true_vs_false",
            "claim_tested": "Does the E237 gate select a healthier high-impact cell-tail subset?",
            "evidence_for": (
                f"gate_true median OOF tail-AUC {float(gate_true['oof_tail_auc_median']):.9f} vs "
                f"gate_false {float(gate_false['oof_tail_auc_median']):.9f}; "
                f"gate_true median support_gain {float(gate_true['support_gain_vs_e224_median']):.9f} vs "
                f"gate_false {float(gate_false['support_gain_vs_e224_median']):.9f}."
            ),
            "evidence_against": (
                f"gate_true OOF gain mean {float(gate_true['oof_gain_vs_full_mean']):.9f} is not better than "
                f"gate_false {float(gate_false['oof_gain_vs_full_mean']):.9f}; this is tail discrimination, not average-CV improvement."
            ),
            "decision_rule": "Rank E237 siblings by tail-AUC/support/top-cell stress, never by average OOF gain.",
        },
    ]

    contrast_df = pd.DataFrame(contrasts)
    contrast_path = OUT / "e243_next_public_slot_after_e242_contrasts.csv"
    contrast_df.to_csv(contrast_path, index=False)

    report_lines = [
        "# E243 Next Public Slot After E242",
        "",
        "## Question",
        "",
        "After E216 failed publicly and E242 clarified E237, what is the next single public-slot policy?",
        "",
        "## Short Answer",
        "",
        "- If the goal is **to use JEPA most aggressively as a solution attempt**, submit the locked E237 learned Q3 cell-tail file.",
        "- If the goal is **to get the cleanest scientific read on the unpruned JEPA body**, submit E224 first.",
        "- If the goal is **to leave JEPA and test a non-collinear hidden-world law**, submit E166.",
        "- E154 remains a conservative counter-world, not the highest-information first slot.",
        "",
        "## Decision Table",
        "",
        md_table(decision_df[
            [
                "candidate",
                "public_role",
                "one_file_rank_if_improvement_biased_jepa",
                "one_file_rank_if_clean_jepa_ablation",
                "one_file_rank_if_non_jepa_escape",
                "submission",
                "hidden_world_bet",
            ]
        ]),
        "",
        "## Why E237 Is Now The Closest Real JEPA Attempt",
        "",
        f"- E237 changes only `{int(e237['q3_dropped_cells'])}` Q3 cells versus E224 and leaves S4 intact.",
        f"- It improves the E224-relative public-free tail shape: expected_loss_vs_e224 `{float(e237['expected_loss_vs_e224']):.9f}`, adverse_reduction `{float(e237['adverse_reduction_vs_e224']):.9f}`, support_gain `{float(e237['support_gain_vs_e224']):.9f}`.",
        f"- E242 says the selected file is rank `{int(tail_auc_rank['top_e237_rank'])}/120` by OOF tail-AUC, rank `{int(support_rank['top_e237_rank'])}/120` by support gain, and rank `{int(topcell_rank['top_e237_rank'])}/120` by Q3 top-cell safety.",
        f"- The same file is only rank `{int(oof_gain_rank['top_e237_rank'])}/120` by average OOF gain. That is the key LeJEPA warning: this is a tail-discrimination representation, not a generic CV-improvement model.",
        "",
        "## Why E216 Does Not Kill JEPA",
        "",
        f"E216 public `{E216_FAIL:.10f}` is a hard negative for masked-family S2 rank translation. It is not evidence that Q3/S4 or cell-tail JEPA is dead. E224 is nearly orthogonal to E216, and E237 changes a Q3 tail on top of E224 rather than replaying the S2 route.",
        "",
        "## Main Contrasts",
        "",
        md_table(contrast_df[["contrast", "claim_tested", "decision_rule"]]),
        "",
        "## Current Recommendation",
        "",
        "For a one-file **JEPA-as-solution** public test, use:",
        "",
        f"`{analysis_path(e237['submission_file'])}`",
        "",
        "For a one-file **clean JEPA ablation** public test, use:",
        "",
        f"`{analysis_path(e224['submission_file'])}`",
        "",
        "Do not submit E216 siblings, E240 simple residual-PC10 rules, lower-ranked E237 siblings, or an E224/E166/E154 blend before feedback.",
        "",
        "## If E237 Is Submitted",
        "",
        "Decode the result with:",
        "",
        "```bash",
        "python3 analysis_outputs/e238_e237_public_feedback_decoder.py --score <PUBLIC_LB>",
        "```",
        "",
        "If E224 public is also known, add:",
        "",
        "```bash",
        "python3 analysis_outputs/e238_e237_public_feedback_decoder.py --score <E237_LB> --e224-score <E224_LB>",
        "```",
        "",
    ]

    report_path = OUT / "e243_next_public_slot_after_e242_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Wrote {decision_path.relative_to(ROOT)}")
    print(f"Wrote {contrast_path.relative_to(ROOT)}")
    print(f"Wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
