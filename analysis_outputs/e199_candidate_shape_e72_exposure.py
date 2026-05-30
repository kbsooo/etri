#!/usr/bin/env python3
"""E199: direct clean-shape E72 exposure for all E197 candidates.

E198 joined E197 slippage stress with E192 pressure-branch anatomy, but several
E197 candidates were not scored by E192 because E192 only used refreshed
pressure branches. The next small question is:

    "If E176 fails and we branch to E172/E154/E144/E166/E155, are any of those
    candidates visibly E72-shaped under the boundary-clean detector?"

This script scores the direct candidate-vs-E95 movement tensor for every E197
candidate with the same clean `shape_target_context_abs` E72 model used in
E191/E192. No submission is created.
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

import e185_known_lb_pair_structural_decoder as e185  # noqa: E402
import e190_e72_contamination_detector as e190  # noqa: E402
import e192_shape_e72_score_anatomy as e192  # noqa: E402
import e197_public_support_mass_inverse as e197  # noqa: E402


KNOWN_CELLS_IN = OUT / "e180_known_anchor_decisive_cell_visibility_cells.csv"
E191_SUMMARY_IN = OUT / "e191_boundary_aware_e72_score_summary.csv"
E197_PROFILES_IN = OUT / "e197_public_support_mass_candidate_profiles.csv"
E198_SUMMARY_IN = OUT / "e198_e72_slippage_exposure_summary.csv"

SUMMARY_OUT = OUT / "e199_candidate_shape_e72_exposure_summary.csv"
NEAREST_OUT = OUT / "e199_candidate_shape_e72_exposure_nearest.csv"
CONTRIB_OUT = OUT / "e199_candidate_shape_e72_exposure_contrib.csv"
REPORT_OUT = OUT / "e199_candidate_shape_e72_exposure_report.md"


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


def required(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def shape_band(prob: float, p95: float, p99: float, positive_floor: float) -> str:
    if not np.isfinite(prob):
        return "not_scored"
    if prob >= positive_floor:
        return "known_positive_scale"
    if prob >= p99:
        return "non_e72_p99_tail"
    if prob >= p95:
        return "non_e72_p95_tail"
    return "below_non_e72_p95"


def direct_role(candidate: str) -> str:
    roles = {
        "e176": "first_sensor",
        "e172": "same_family_safety_after_tie_or_small_loss",
        "e174": "full_q2_reopen_contrast_after_feedback",
        "e166": "broad_safety_atlas_falsification_sensor",
        "e154": "first_repaired_branch_counterworld",
        "e144": "conservative_repaired_tail_risk_control",
        "e155": "low_body_repaired_branch_control",
    }
    return roles.get(candidate, "candidate")


def direct_verdict(row: pd.Series) -> str:
    candidate = str(row["candidate"])
    band = str(row["direct_shape_e72_band"])
    thin = bool(row["thin_visible_margin"])
    if band == "known_positive_scale":
        return "direct_e72_positive_scale"
    if candidate == "e144" and band == "non_e72_p99_tail":
        return "e144_direct_p99_tail_alarm_not_positive"
    if band == "non_e72_p99_tail":
        return "direct_p99_tail_alarm_not_positive"
    if band == "non_e72_p95_tail":
        return "direct_p95_tail_alarm_not_positive"
    if thin:
        return "thin_margin_clean_shape"
    return "direct_clean_shape"


def candidate_zrecord(candidate: str, world: str, file_name: str, cells: pd.DataFrame) -> dict[str, Any]:
    forward: dict[str, Any] = {
        "candidate": candidate,
        "scenario": "direct_vs_e95",
        "world": world,
        "file": file_name,
        "n_diff_cells": int(len(cells)),
        "n_rows": int(cells["sub_idx"].nunique()),
        "top_targets": ",".join(cells.sort_values("swing", ascending=False)["target"].head(4).tolist()),
    }
    reverse = dict(forward)
    for set_name in e185.SETS:
        e185.add_set_features(forward, cells.copy(), set_name, reverse=False)
        e185.add_set_features(reverse, cells.copy(), set_name, reverse=True)

    rec = {
        "candidate": candidate,
        "scenario": "direct_vs_e95",
        "world": world,
        "file": file_name,
        "n_diff_cells": forward["n_diff_cells"],
        "n_rows": forward["n_rows"],
        "top_targets": forward["top_targets"],
    }
    for col in sorted(set(forward).union(reverse)):
        if any(col.startswith(prefix) for fs in e185.FEATURE_SETS for prefix in fs.include_prefixes):
            rec[f"z__{col}"] = float(forward.get(col, 0.0) or 0.0) - float(reverse.get(col, 0.0) or 0.0)
    return rec


def detector_health(summary: pd.DataFrame) -> pd.Series:
    rows = summary[
        summary["feature_view"].eq("shape_target_context_abs")
        & summary["score_spec"].eq("plain_logit_c025")
        & summary["split"].eq("loo_pair_id")
        & summary["boundary_clean_gate"].astype(bool)
    ]
    if rows.empty:
        raise RuntimeError("missing E191 clean detector row")
    return rows.iloc[0]


def main() -> None:
    for path in [KNOWN_CELLS_IN, E191_SUMMARY_IN, E197_PROFILES_IN, E198_SUMMARY_IN]:
        required(path)

    known = e192.load_known()
    am = e192.fit_anatomy_model(known)
    known["shape_e72_prob"] = e192.predict_prob(am, known)

    neg = known.loc[known["e72_neighbor_label"].eq(0), "shape_e72_prob"]
    pos = known.loc[known["e72_neighbor_label"].eq(1), "shape_e72_prob"]
    p95 = float(np.quantile(neg, 0.95))
    p99 = float(np.quantile(neg, 0.99))
    positive_floor = float(pos.min())
    positive_mean = float(pos.mean())

    known_cells = pd.read_csv(KNOWN_CELLS_IN, low_memory=False)
    profiles = pd.read_csv(E197_PROFILES_IN)
    e198 = pd.read_csv(E198_SUMMARY_IN)
    detector = detector_health(pd.read_csv(E191_SUMMARY_IN))

    rows: list[dict[str, Any]] = []
    for cfg in e197.CANDIDATES:
        cells = e197.candidate_cells(cfg["candidate"], cfg["file"], known_cells)
        rows.append(candidate_zrecord(cfg["candidate"], cfg["world"], cfg["file"], cells))

    direct = pd.DataFrame(rows)
    direct = e190.abs_features(direct)
    direct = e192.ensure_branch_cols(direct, am.cols)
    direct["direct_shape_e72_prob"] = e192.predict_prob(am, direct)
    direct["direct_shape_e72_band"] = direct["direct_shape_e72_prob"].map(
        lambda p: shape_band(float(p), p95, p99, positive_floor)
    )
    direct["candidate_role"] = direct["candidate"].map(direct_role)
    direct["known_non_e72_p95"] = p95
    direct["known_non_e72_p99"] = p99
    direct["known_positive_floor"] = positive_floor
    direct["known_positive_mean"] = positive_mean

    profile_cols = [
        "candidate",
        "surplus_to_tie_visible_mean",
        "surplus_to_tie_focus_mean",
        "q_visible_mean",
        "q_focus_mean",
        "swing_sum",
    ]
    direct = direct.merge(profiles[profile_cols], on="candidate", how="left")
    direct["thin_visible_margin"] = direct["surplus_to_tie_visible_mean"].le(0.02)

    e198_cols = [
        "candidate",
        "shape_e72_prob_max",
        "shape_e72_band",
        "visible_outcome_e72_vs_e95",
        "visible_outcome_e72_vs_mixmin",
        "focus_outcome_e72_vs_e95",
        "focus_outcome_e72_vs_mixmin",
        "verdict",
    ]
    direct = direct.merge(e198[e198_cols], on="candidate", how="left", suffixes=("", "_e198_branch"))
    direct = direct.rename(
        columns={
            "shape_e72_prob_max": "branch_shape_e72_prob_max",
            "shape_e72_band": "branch_shape_e72_band",
            "verdict": "e198_slippage_shape_verdict",
        }
    )
    direct["direct_minus_branch_shape_prob"] = direct["direct_shape_e72_prob"] - direct[
        "branch_shape_e72_prob_max"
    ]
    direct["direct_verdict"] = direct.apply(direct_verdict, axis=1)

    nearest_source = direct.copy()
    nearest_source["shape_e72_prob"] = nearest_source["direct_shape_e72_prob"]
    nearest = e192.nearest_known(am, known, nearest_source, k=8)
    nearest_summary = (
        nearest.groupby(["candidate", "scenario"], as_index=False)
        .agg(
            top3_label_rate=("known_label", lambda s: float(np.mean(s.head(3)))),
            top3_exact_boundary_rate=("known_pair_is_e95_e101", lambda s: float(np.mean(s.head(3)))),
            top3_contexts=("known_pair_context", lambda s: ";".join(map(str, s.head(3)))),
            top1_context=("known_pair_context", "first"),
            top1_label=("known_label", "first"),
            top1_prob=("known_prob", "first"),
            top1_euclidean=("euclidean", "first"),
        )
    )
    direct = direct.merge(nearest_summary, on=["candidate", "scenario"], how="left")

    contrib = e192.group_contributions(am, direct, ["candidate", "scenario"])
    contrib_detail = e192.contribution_frame(am, direct, ["candidate", "scenario"], "candidate_direct")

    summary_cols = [
        "candidate",
        "scenario",
        "candidate_role",
        "world",
        "n_diff_cells",
        "n_rows",
        "top_targets",
        "surplus_to_tie_visible_mean",
        "surplus_to_tie_focus_mean",
        "direct_shape_e72_prob",
        "direct_shape_e72_band",
        "branch_shape_e72_prob_max",
        "branch_shape_e72_band",
        "direct_minus_branch_shape_prob",
        "top3_label_rate",
        "top3_contexts",
        "top1_context",
        "top1_label",
        "direct_verdict",
        "visible_outcome_e72_vs_e95",
        "visible_outcome_e72_vs_mixmin",
        "focus_outcome_e72_vs_e95",
        "focus_outcome_e72_vs_mixmin",
    ]
    grouped_cols = [
        "candidate",
        "scenario",
        "contrib_family_shape",
        "contrib_family_target",
        "contrib_family_context",
        "abscontrib_family_shape",
        "abscontrib_family_target",
        "abscontrib_family_context",
        "contrib_target_Q1",
        "contrib_target_Q2",
        "contrib_target_Q3",
        "contrib_target_S1",
        "contrib_target_S2",
        "contrib_target_S3",
        "contrib_target_S4",
    ]
    final = direct[summary_cols].merge(contrib[grouped_cols], on=["candidate", "scenario"], how="left")
    final = final.sort_values("direct_shape_e72_prob", ascending=False).reset_index(drop=True)

    final.to_csv(SUMMARY_OUT, index=False)
    nearest.to_csv(NEAREST_OUT, index=False)
    contrib_detail.to_csv(CONTRIB_OUT, index=False)

    report_cols = [
        "candidate",
        "candidate_role",
        "surplus_to_tie_visible_mean",
        "direct_shape_e72_prob",
        "direct_shape_e72_band",
        "branch_shape_e72_prob_max",
        "top3_label_rate",
        "top3_contexts",
        "direct_verdict",
    ]
    report = [
        "# E199 Candidate Clean-Shape E72 Exposure",
        "",
        "## Question",
        "",
        "E198 scored only the pressure-branch candidates present in E192. If E176 fails and the",
        "next branch is E172/E154/E144/E166/E155, do any of those direct candidate movements",
        "look E72-shaped under the boundary-clean detector?",
        "",
        "## Detector Health",
        "",
        (
            "- Boundary-clean detector: `shape_target_context_abs / plain_logit_c025 / loo_pair_id` "
            f"with AUC `{fmt(detector['auc'])}`, AP `{fmt(detector['avg_precision'])}`, "
            f"top-k recall `{fmt(detector['topk_recall'])}`, exact E95/E101 mean probability "
            f"`{fmt(detector['exact_e95_e101_mean_prob'])}`."
        ),
        (
            f"- Thresholds from full known anatomy: non-E72 p95 `{fmt(p95)}`, non-E72 p99 `{fmt(p99)}`, "
            f"E72-positive floor `{fmt(positive_floor)}`."
        ),
        "",
        "## Direct Candidate Scores",
        "",
        markdown_table(final[report_cols]),
        "",
        "## Interpretation",
        "",
        "- E172 and E174 are clean under direct candidate-vs-E95 shape scoring. This removes the main missing-shape caveat from E198 for the same-family safety and Q2-amplitude contrasts.",
        "- E166 is also clean-shape non-E72. Its E197 hard-fail risk is therefore broad support-mass slippage/tail exposure, not visible E72 movement shape.",
        "- E154 and E155 are clean-shape non-E72 but thin-margin. Their risk remains repaired-branch margin fragility rather than E72 contamination.",
        "- E144 is the only direct movement with a p99 tail alarm (`non_e72_p99_tail`), still far below the E72-positive floor. This supports preferring E154 over E144 as the first repaired-branch counter-world after adverse E176 feedback.",
        "- E176 remains clean by direct scoring too. E199 therefore reinforces the E198 distinction between algebraic E72-like slippage and visible E72 shape exposure.",
        "",
        "## Decision",
        "",
        "No submission is created. Keep E176 first. If E176 lands in a tie/small-loss band, E172 is a cleaner same-family safety contrast than E174 by information role and is not E72-shaped. If E176 lands in a branch/hard-loss band, E154 remains the first repaired-branch counter-world; E144 should be treated as a tail-risk control, not first follow-up.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")

    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {NEAREST_OUT}")
    print(f"Wrote {CONTRIB_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(final[report_cols].to_string(index=False))


if __name__ == "__main__":
    main()
