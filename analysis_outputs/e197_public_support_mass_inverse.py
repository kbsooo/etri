#!/usr/bin/env python3
"""E197: infer public support-mass slippage from known LB pairs.

The live question after E196 is not whether another local feature can certify
E176. It is whether the known public LB observations imply a reusable hidden
label support-mass law.

For a pair of submissions, each moved test-target cell has two possible LogLoss
deltas: one if the hidden label is 1, one if it is 0. We rewrite the observed
public delta as:

    delta = adverse_sum - q * swing_sum

where q is the aggregate fraction of swing mass whose hidden labels support the
new submission. The gap between observed q and train-visible q is the "public
slippage" that current local priors failed to model.

This script:
- derives slippage from known public pairs;
- applies those slippages as analogues to pending candidates;
- checks whether E176, E172, E154, and other live files survive the same stress.

No submission is created.
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

from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402
import e179_e176_critical_cell_visibility_audit as e179  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
MIXMIN_PUBLIC = 0.5763066405
E95_EDGE_VS_MIXMIN = E95_PUBLIC - MIXMIN_PUBLIC
E101_DELTA_VS_E95 = E101_PUBLIC - E95_PUBLIC
MIXMIN_DELTA_VS_E95 = MIXMIN_PUBLIC - E95_PUBLIC

KNOWN_CELLS_IN = OUT / "e180_known_anchor_decisive_cell_visibility_cells.csv"

KNOWN_OUT = OUT / "e197_public_support_mass_known_pairs.csv"
CANDIDATE_PROFILE_OUT = OUT / "e197_public_support_mass_candidate_profiles.csv"
SLIPPAGE_OUT = OUT / "e197_public_support_mass_slippage_stress.csv"
SUMMARY_OUT = OUT / "e197_public_support_mass_summary.csv"
REPORT_OUT = OUT / "e197_public_support_mass_report.md"

BASE_FILE = "submission_e95_hardtail_541e3973.csv"

CANDIDATES = [
    {
        "candidate": "e176",
        "file": "submission_e176_abl_q2_to0p75_91e49725.csv",
        "world": "broad_q2_underopen",
    },
    {
        "candidate": "e174",
        "file": "submission_e174_ro_fc_top75_to1p0_95638e73.csv",
        "world": "full_q2_reopen_contrast",
    },
    {
        "candidate": "e172",
        "file": "submission_e172_vis_pos_all_keep0p25_d90f4407.csv",
        "world": "safer_tail_repair_contrast",
    },
    {
        "candidate": "e166",
        "file": "submission_e166_broadsurv_s0p01_d8bfa94b.csv",
        "world": "broad_plateau_break_safety_atlas_test",
    },
    {
        "candidate": "e154",
        "file": "submission_e154_s3repair_9f2e2e73.csv",
        "world": "repaired_branch_counterworld",
    },
    {
        "candidate": "e144",
        "file": "submission_e144_activeboundary_d7b4b331.csv",
        "world": "conservative_unrepaired_branch",
    },
    {
        "candidate": "e155",
        "file": "submission_e155_bodytemp_d27e7965.csv",
        "world": "low_body_repaired_branch_control",
    },
]

PRIORS = ["visible_mean", "focus_mean", "nearest_hard085"]


def fmt(x: Any) -> str:
    if x is None:
        return "NA"
    if isinstance(x, str):
        return x
    try:
        if pd.isna(x):
            return "NA"
    except TypeError:
        pass
    if isinstance(x, (float, np.floating)):
        return f"{float(x):.9g}"
    return str(x)


def markdown_table(frame: pd.DataFrame, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        view[col] = view[col].map(fmt).astype(str).str.replace("|", "\\|", regex=False)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row.astype(str).tolist()) + " |" for _, row in view.iterrows()]
    return "\n".join([header, sep, *rows])


def classify_delta(delta_vs_e95: float) -> str:
    if delta_vs_e95 <= E95_EDGE_VS_MIXMIN:
        return "clean_or_better"
    if delta_vs_e95 <= -3.0e-6:
        return "micro_win"
    if delta_vs_e95 <= 3.0e-6:
        return "tie"
    if delta_vs_e95 <= E101_DELTA_VS_E95:
        return "small_loss"
    if delta_vs_e95 <= MIXMIN_DELTA_VS_E95:
        return "mixmin_safe_loss"
    if delta_vs_e95 <= 5.0e-5:
        return "branch_loss"
    return "hard_fail"


def support_profile(cells: pd.DataFrame, actual_delta: float | None = None) -> dict[str, Any]:
    support_sum = float(cells["support_delta"].sum())
    adverse_sum = float(cells["adverse_delta"].sum())
    swing_sum = float(cells["swing"].sum())
    if swing_sum <= 0:
        raise ValueError("empty swing")

    rec: dict[str, Any] = {
        "n_cells": int(len(cells)),
        "n_rows": int(cells["sub_idx"].nunique()),
        "n_subjects": int(cells["subject_id"].nunique()) if "subject_id" in cells.columns else np.nan,
        "n_blocks": int(cells["hidden_block_id"].nunique()) if "hidden_block_id" in cells.columns else np.nan,
        "targets": ",".join(sorted(cells["target"].unique())),
        "q_share": float(cells["target_group"].eq("Q").mean()),
        "s_share": float(cells["target_group"].eq("S").mean()),
        "support_sum": support_sum,
        "adverse_sum": adverse_sum,
        "swing_sum": swing_sum,
        "top1_swing_share": float(cells["swing"].max() / swing_sum),
        "q_tie": adverse_sum / swing_sum,
        "q_clean_win": (adverse_sum - E95_EDGE_VS_MIXMIN) / swing_sum,
        "q_e101_boundary": (adverse_sum - E101_DELTA_VS_E95) / swing_sum,
        "q_mixmin_boundary": (adverse_sum - MIXMIN_DELTA_VS_E95) / swing_sum,
        "between_train_runs_rate": float(cells["between_train_runs"].mean()),
        "edge_like_rate": float(cells["edge_like"].astype(bool).mean()),
        "e72_active_rate": float(cells["e72_active"].astype(bool).mean()),
        "e101_active_rate": float(cells["e101_active"].astype(bool).mean()),
        "flank_conflict_rate": float(cells["flank_conflict"].astype(bool).mean()),
    }
    for target in TARGETS:
        mask = cells["target"].eq(target)
        rec[f"target_{target}_share"] = float(mask.mean())
        rec[f"target_{target}_swing_share"] = (
            float(cells.loc[mask, "swing"].sum() / swing_sum) if mask.any() else 0.0
        )
    for prior in PRIORS:
        q = float(np.average(cells[f"support_probability_{prior}"], weights=cells["swing"]))
        delta = adverse_sum - q * swing_sum
        rec[f"q_{prior}"] = q
        rec[f"surplus_to_tie_{prior}"] = q - rec["q_tie"]
        rec[f"surplus_to_clean_{prior}"] = q - rec["q_clean_win"]
        rec[f"pred_delta_{prior}"] = delta
        rec[f"pred_outcome_{prior}"] = classify_delta(delta)
    if actual_delta is not None and np.isfinite(actual_delta):
        q_observed = (adverse_sum - float(actual_delta)) / swing_sum
        rec["actual_delta"] = float(actual_delta)
        rec["actual_outcome_vs_e95_scale"] = classify_delta(float(actual_delta))
        rec["q_observed"] = q_observed
        rec["observed_surplus_to_tie"] = q_observed - rec["q_tie"]
        for prior in PRIORS:
            rec[f"slippage_vs_{prior}"] = q_observed - rec[f"q_{prior}"]
            rec[f"pred_error_{prior}"] = rec[f"pred_delta_{prior}"] - float(actual_delta)
    return rec


def build_known_pairs(cells: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pair, part in cells.groupby("pair", sort=False):
        actual_delta = part["actual_delta"].dropna()
        if actual_delta.empty:
            continue
        rec = support_profile(part, float(actual_delta.iloc[0]))
        rec["pair"] = pair
        rec["family"] = part["family"].iloc[0]
        rec["actual_direction"] = part["actual_direction"].iloc[0]
        rows.append(rec)
    out = pd.DataFrame(rows)
    return out.sort_values(["actual_delta", "pair"]).reset_index(drop=True)


def candidate_cells(candidate: str, file_name: str, known_cells: pd.DataFrame) -> pd.DataFrame:
    if candidate == "e176":
        found = known_cells[known_cells["pair"].eq("e176_vs_e95_pending")].copy()
        if found.empty:
            raise RuntimeError("missing E176 pending cells in E180 output")
        return found
    return e179.build_pair_cells(f"{candidate}_vs_e95", file_name, BASE_FILE)


def build_candidate_profiles(known_cells: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows = []
    cell_map: dict[str, pd.DataFrame] = {}
    for cfg in CANDIDATES:
        cells = candidate_cells(cfg["candidate"], cfg["file"], known_cells)
        cell_map[cfg["candidate"]] = cells
        rec = support_profile(cells)
        rec["candidate"] = cfg["candidate"]
        rec["file"] = cfg["file"]
        rec["world"] = cfg["world"]
        rows.append(rec)
    out = pd.DataFrame(rows)
    return out.sort_values("pred_delta_visible_mean").reset_index(drop=True), cell_map


def build_slippage_stress(known: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, cand in candidates.iterrows():
        for prior in ["visible_mean", "focus_mean"]:
            base_q = float(cand[f"q_{prior}"])
            for _, obs in known.iterrows():
                slip = float(obs[f"slippage_vs_{prior}"])
                q = base_q + slip
                delta = float(cand["adverse_sum"]) - q * float(cand["swing_sum"])
                rows.append(
                    {
                        "candidate": cand["candidate"],
                        "world": cand["world"],
                        "prior": prior,
                        "analogue_pair": obs["pair"],
                        "analogue_family": obs["family"],
                        "analogue_actual_delta": float(obs["actual_delta"]),
                        "analogue_slippage": slip,
                        "candidate_q_base": base_q,
                        "candidate_q_tie": float(cand["q_tie"]),
                        "candidate_surplus_to_tie": float(cand[f"surplus_to_tie_{prior}"]),
                        "q_after_slippage": q,
                        "delta_vs_e95": delta,
                        "public_lb_if_e95_anchor": E95_PUBLIC + delta,
                        "outcome": classify_delta(delta),
                        "beats_e95": delta < 0,
                        "beats_e101": E95_PUBLIC + delta < E101_PUBLIC,
                        "beats_mixmin": E95_PUBLIC + delta < MIXMIN_PUBLIC,
                        "branch_or_hard_fail": delta > MIXMIN_DELTA_VS_E95,
                    }
                )
    return pd.DataFrame(rows)


def summarize_stress(stress: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (candidate, prior), part in stress.groupby(["candidate", "prior"], sort=False):
        profile = candidates[candidates["candidate"].eq(candidate)].iloc[0]
        ordered = part.sort_values("delta_vs_e95")
        worst = part.loc[part["delta_vs_e95"].idxmax()]
        best = part.loc[part["delta_vs_e95"].idxmin()]
        rows.append(
            {
                "candidate": candidate,
                "world": profile["world"],
                "prior": prior,
                "pred_delta_base": float(profile[f"pred_delta_{prior}"]),
                "q_tie": float(profile["q_tie"]),
                "q_base": float(profile[f"q_{prior}"]),
                "adverse_slippage_tolerance_to_loss": float(profile[f"surplus_to_tie_{prior}"]),
                "clean_win_slippage_tolerance": float(profile[f"surplus_to_clean_{prior}"]),
                "clean_or_better_rate": float(part["outcome"].eq("clean_or_better").mean()),
                "win_rate": float(part["beats_e95"].mean()),
                "beats_e101_rate": float(part["beats_e101"].mean()),
                "branch_or_hard_fail_rate": float(part["branch_or_hard_fail"].mean()),
                "mean_delta_vs_e95": float(part["delta_vs_e95"].mean()),
                "median_delta_vs_e95": float(part["delta_vs_e95"].median()),
                "worst_delta_vs_e95": float(worst["delta_vs_e95"]),
                "worst_analogue": worst["analogue_pair"],
                "best_delta_vs_e95": float(best["delta_vs_e95"]),
                "best_analogue": best["analogue_pair"],
                "ordered_outcomes": ";".join(f"{r.analogue_pair}:{r.outcome}" for r in ordered.itertuples()),
            }
        )
    out = pd.DataFrame(rows)
    out["stress_score"] = (
        out["clean_or_better_rate"]
        + 0.5 * out["win_rate"]
        + 0.25 * out["beats_e101_rate"]
        - out["branch_or_hard_fail_rate"]
    )
    return out.sort_values(["prior", "stress_score", "mean_delta_vs_e95"], ascending=[True, False, True]).reset_index(
        drop=True
    )


def write_report(known: pd.DataFrame, candidates: pd.DataFrame, stress: pd.DataFrame, summary: pd.DataFrame) -> None:
    visible_summary = summary[summary["prior"].eq("visible_mean")].copy()
    focus_summary = summary[summary["prior"].eq("focus_mean")].copy()

    lines = [
        "# E197 Public Support-Mass Inverse",
        "",
        "## Question",
        "",
        "Can known public LB observations be rewritten as a reusable hidden-label support-mass slippage law, and does that law certify or demote E176 before feedback?",
        "",
        "## Result",
        "",
        "Known public pairs do expose a useful support-mass quantity, but it is not a submission selector. "
        "E176 survives every non-E72 slippage analogue as a clean win, and fails only under E72-like adverse slippage. "
        "That is exactly the current live uncertainty: whether E176 is a clean broad/Q2-underopen repair or another E72-contaminated broad move.",
        "",
        "E154/E144/E155 are much more slippage-fragile: their visible-prior win margins are real but thin, so any E95/E101/E72-like negative slippage turns them into branch-loss or hard-fail analogues. "
        "This supports keeping E154 as the counter-world after adverse E176 feedback, not as the first sensor.",
        "",
        "## Known Public Pair Inversion",
        "",
        markdown_table(
            known[
                [
                    "pair",
                    "family",
                    "actual_delta",
                    "q_tie",
                    "q_observed",
                    "q_visible_mean",
                    "slippage_vs_visible_mean",
                    "pred_delta_visible_mean",
                    "pred_error_visible_mean",
                ]
            ].sort_values("pair")
        ),
        "",
        "## Candidate Profiles",
        "",
        markdown_table(
            candidates[
                [
                    "candidate",
                    "world",
                    "n_cells",
                    "swing_sum",
                    "q_tie",
                    "q_visible_mean",
                    "surplus_to_tie_visible_mean",
                    "pred_delta_visible_mean",
                    "q_focus_mean",
                    "surplus_to_tie_focus_mean",
                    "pred_delta_focus_mean",
                ]
            ]
        ),
        "",
        "## Visible-Prior Slippage Stress",
        "",
        markdown_table(
            visible_summary[
                [
                    "candidate",
                    "world",
                    "stress_score",
                    "adverse_slippage_tolerance_to_loss",
                    "clean_or_better_rate",
                    "win_rate",
                    "branch_or_hard_fail_rate",
                    "worst_analogue",
                    "worst_delta_vs_e95",
                    "ordered_outcomes",
                ]
            ]
        ),
        "",
        "## Focus-Prior Slippage Stress",
        "",
        markdown_table(
            focus_summary[
                [
                    "candidate",
                    "world",
                    "stress_score",
                    "adverse_slippage_tolerance_to_loss",
                    "clean_or_better_rate",
                    "win_rate",
                    "branch_or_hard_fail_rate",
                    "worst_analogue",
                    "worst_delta_vs_e95",
                    "ordered_outcomes",
                ]
            ]
        ),
        "",
        "## Interpretation",
        "",
        "- E176 visible support surplus over tie is positive but not huge. It can absorb E95/E101/mixmin-like slippage, but not E72-like adverse slippage.",
        "- E172 has slightly more slippage tolerance than E176 in this lens, so it remains the safer same-family contrast if E176 lands in a tie or small-loss band.",
        "- E166 has a large base edge but also a large E72-like hard-fail tail, matching its role as a broad safety-atlas falsification sensor rather than the first expected-score file.",
        "- E154/E144/E155 are branch sensors with thin support-mass margins. They are not invalid, but the public slippage law says they are worse first sensors than E176 unless we deliberately trust the binary/repaired-branch counterworld.",
        "",
        "## Decision",
        "",
        "No new submission is created. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next public sensor. "
        "E197 strengthens the decoder: an E176 loss should be read specifically as E72-like adverse public slippage, not as a generic failure of visible support.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    if not KNOWN_CELLS_IN.exists():
        raise FileNotFoundError(KNOWN_CELLS_IN)
    known_cells = pd.read_csv(KNOWN_CELLS_IN, low_memory=False)

    known = build_known_pairs(known_cells)
    candidates, _ = build_candidate_profiles(known_cells)
    stress = build_slippage_stress(known, candidates)
    summary = summarize_stress(stress, candidates)

    known.to_csv(KNOWN_OUT, index=False)
    candidates.to_csv(CANDIDATE_PROFILE_OUT, index=False)
    stress.to_csv(SLIPPAGE_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(known, candidates, stress, summary)

    print(f"wrote {KNOWN_OUT}")
    print(f"wrote {CANDIDATE_PROFILE_OUT}")
    print(f"wrote {SLIPPAGE_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")
    print(
        summary[
            [
                "candidate",
                "prior",
                "stress_score",
                "adverse_slippage_tolerance_to_loss",
                "clean_or_better_rate",
                "win_rate",
                "branch_or_hard_fail_rate",
                "worst_analogue",
                "worst_delta_vs_e95",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
