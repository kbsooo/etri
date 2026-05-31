#!/usr/bin/env python3
"""E351: robust selector over the E350 compact lifestyle-state plateau.

Question:
    The E350 plateau is real, but did its ranker choose a too-aggressive point?

This script does not generate another model.  It re-ranks the E350 plateau
candidates with a conservative maximin selector over p90 visibility,
public-analog risk, bad-axis margin, Q1-state specificity, plateau support,
and distance from E349.  Public LB is not used.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e349_e347_target_cell_ablation_stress import clip_prob, short_hash  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402


SCORES_IN = OUT / "e350_compact_state_plateau_scores.csv"
PROFILE_OUT = OUT / "e351_robust_plateau_selector_profiles.csv"
RANKED_OUT = OUT / "e351_robust_plateau_selector_ranked.csv"
REPORT_OUT = OUT / "e351_robust_plateau_selector_report.md"
UPLOAD_PREFIX = "submission_e351_robustplateau"


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(str(path_or_name))


def pct_high(series: pd.Series) -> pd.Series:
    return series.astype(float).rank(pct=True, method="average")


def pct_low(series: pd.Series) -> pd.Series:
    return (-series.astype(float)).rank(pct=True, method="average")


def materialize_uploadsafe(rec: pd.Series, tag: str) -> Path:
    src = locate(rec["file"])
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_{safe_id(tag, 48)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    return out


def add_selector_scores(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    e349 = scores[scores["variant"].eq("canonical_e349")].iloc[0]
    e347 = scores[scores["variant"].eq("canonical_e347")].iloc[0]
    out = scores.copy()
    out["p90_gain_vs_e349"] = float(e349["pred_delta_vs_current_p90"]) - out["pred_delta_vs_current_p90"].astype(float)
    out["risk_delta_vs_e349"] = out["public_analog_risk_score"].astype(float) - float(e349["public_analog_risk_score"])
    out["q1_margin_delta_vs_e349"] = out["q1_specificity_margin"].astype(float) - float(e349["q1_specificity_margin"])
    out["bad_axis_margin"] = 0.015 - out["incremental_bad_axis_vs_current"].astype(float).abs()
    out["scale_abs_delta"] = (out["scale"].astype(float) - 1.0).abs()
    out["s3_tail_present"] = out["s3_alpha"].astype(float) > 0

    plateau = out[out["e350_plateau_gate"].astype(bool)].copy()
    plateau["p90_pct"] = pct_high(-plateau["pred_delta_vs_current_p90"])
    plateau["risk_pct"] = pct_low(plateau["public_analog_risk_score"])
    plateau["bad_margin_pct"] = pct_high(plateau["bad_axis_margin"])
    plateau["q1_specificity_pct"] = pct_high(plateau["q1_specificity_margin"])
    plateau["support_pct"] = pct_high(plateau["plateau_support_score"])
    plateau["compat_e349_pct"] = pct_low(plateau["prob_l1_delta_vs_e349"])
    plateau["micro_scale_pct"] = pct_low(plateau["scale_abs_delta"])
    components = [
        "p90_pct",
        "risk_pct",
        "bad_margin_pct",
        "q1_specificity_pct",
        "support_pct",
        "compat_e349_pct",
        "micro_scale_pct",
    ]
    plateau["e351_worst_axis_pct"] = plateau[components].min(axis=1)
    plateau["e351_mean_axis_pct"] = plateau[components].mean(axis=1)
    plateau["e351_robust_score"] = (
        2.0 * plateau["e351_worst_axis_pct"]
        + plateau["e351_mean_axis_pct"]
        + 0.15 * np.log1p(plateau["plateau_support_score"].astype(float))
        + 0.10 * plateau["s3_tail_present"].astype(float)
    )
    plateau["e351_compat_gate"] = (
        (plateau["p90_gain_vs_e349"] >= 5.0e-8)
        & (plateau["risk_delta_vs_e349"] <= 5.0e-5)
        & (plateau["bad_axis_margin"] >= 0.00020)
        & (plateau["q1_margin_delta_vs_e349"] >= -0.03)
        & (plateau["plateau_support_score"] >= 30)
        & (plateau["prob_l1_delta_vs_e349"] >= 0.001)
        & (plateau["prob_l1_delta_vs_e349"] <= 0.009)
        & (plateau["scale_abs_delta"] <= 0.0051)
    )

    out = out.merge(
        plateau[
            [
                "basename",
                *components,
                "e351_worst_axis_pct",
                "e351_mean_axis_pct",
                "e351_robust_score",
                "e351_compat_gate",
            ]
        ],
        on="basename",
        how="left",
    )
    return out, e349, e347


def choose_profiles(ranked: pd.DataFrame) -> pd.DataFrame:
    plateau = ranked[ranked["e350_plateau_gate"].astype(bool)].copy()
    compat = plateau[plateau["e351_compat_gate"].fillna(False).astype(bool)].copy()
    rows: list[dict[str, object]] = []

    def add(role: str, frame: pd.DataFrame, sort_cols: list[str], ascending: list[bool], reason: str) -> None:
        if frame.empty:
            return
        rec = frame.sort_values(sort_cols, ascending=ascending).iloc[0]
        rows.append({"profile": role, "reason": reason, **rec.to_dict()})

    add(
        "e350_rank_selected",
        ranked[ranked["selected_uploadsafe_file"].astype(str).str.len() > 0],
        ["e350_rank_score"],
        [False],
        "original E350 ranker selection",
    )
    add(
        "e351_robust",
        compat,
        ["e351_robust_score", "e351_worst_axis_pct", "p90_gain_vs_e349"],
        [False, False, False],
        "maximin robust selector under compatibility gates",
    )
    add(
        "e351_low_risk",
        compat,
        ["public_analog_risk_score", "p90_gain_vs_e349", "e351_robust_score"],
        [True, False, False],
        "lowest public-analog risk while still improving E349 p90",
    )
    add(
        "e351_p90",
        compat,
        ["pred_delta_vs_current_p90", "public_analog_risk_score", "e351_robust_score"],
        [True, True, False],
        "strongest p90 inside conservative compatibility gates",
    )
    add(
        "e351_e349_nearest",
        compat,
        ["prob_l1_delta_vs_e349", "p90_gain_vs_e349", "e351_robust_score"],
        [True, False, False],
        "nearest meaningful change from E349 with p90 improvement",
    )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.drop_duplicates(subset=["profile", "basename"]).reset_index(drop=True)
    return out


def write_report(ranked: pd.DataFrame, profiles: pd.DataFrame, selected_path: Path | None) -> None:
    cols = [
        "profile",
        "variant",
        "threshold_frac",
        "scale",
        "s3_alpha",
        "reason",
        "e351_compat_gate",
        "e351_robust_score",
        "e351_worst_axis_pct",
        "pred_delta_vs_current_p90",
        "p90_gain_vs_e349",
        "public_analog_risk_score",
        "risk_delta_vs_e349",
        "incremental_bad_axis_vs_current",
        "bad_axis_margin",
        "q1_specificity_margin",
        "q1_margin_delta_vs_e349",
        "plateau_support_score",
        "prob_l1_delta_vs_e349",
        "prob_l1_delta_vs_e347",
        "selected_uploadsafe_file",
    ]
    cols = [c for c in cols if c in profiles.columns]
    top_cols = [c for c in cols if c != "profile" and c != "reason"]
    compat = ranked[ranked["e351_compat_gate"].fillna(False).astype(bool)].copy()
    selected_text = rel(selected_path) if selected_path is not None else "none"
    lines = [
        "# E351 Robust Plateau Selector",
        "",
        "## Question",
        "",
        "Inside the E350 plateau, is the original rank-selected point too aggressive, and is there a more robust public-free candidate?",
        "",
        "## Method",
        "",
        "- Input: E350 plateau scores only; no public LB tuning.",
        "- Rank axes: p90 visibility, public-analog risk, bad-axis margin, Q1-state specificity, plateau support, E349 compatibility, and micro-scale size.",
        "- Conservative compatibility gate requires p90 improvement versus E349, bounded public-analog risk, bad-axis margin, Q1 specificity, non-near-duplicate distance, and scale delta <= 0.005.",
        "",
        "## Decision",
        "",
        f"- plateau candidates: `{int(ranked['e350_plateau_gate'].fillna(False).sum())}`",
        f"- E351 compatibility candidates: `{len(compat)}`",
        f"- selected robust upload-safe candidate: `{selected_text}`",
        "",
        "## Profile Comparison",
        "",
        md_table(profiles[cols], n=20, floatfmt=".9f") if not profiles.empty else "_empty_",
        "",
        "## Top Robust Candidates",
        "",
        md_table(compat.sort_values(["e351_robust_score", "e351_worst_axis_pct"], ascending=[False, False])[top_cols], n=30, floatfmt=".9f") if not compat.empty else "_empty_",
        "",
        "## Interpretation",
        "",
    ]
    if selected_path is None:
        lines.extend(
            [
                "No E350 plateau candidate passed the conservative robust selector.",
                "This would mean E350 is useful as a latent-basin proof, but not enough to replace E349 as a public candidate.",
            ]
        )
    else:
        lines.extend(
            [
                "E351 found a safer point inside the E350 plateau.",
                "This does not disprove E350's selected candidate; it separates the score-seeking point from the lower-regret point.",
                "If public slots are scarce, the robust E351 candidate is a more conservative sensor than the original E350 rank winner.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(RANKED_OUT)}`",
            f"- `{rel(PROFILE_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scores = pd.read_csv(SCORES_IN)
    ranked, _, _ = add_selector_scores(scores)
    profiles = choose_profiles(ranked)
    ranked = ranked.sort_values(["e351_compat_gate", "e351_robust_score"], ascending=[False, False]).reset_index(drop=True)
    ranked.to_csv(RANKED_OUT, index=False)

    selected_path: Path | None = None
    if not profiles.empty:
        robust = profiles[profiles["profile"].eq("e351_robust")]
        if not robust.empty:
            rec = robust.iloc[0]
            selected_path = materialize_uploadsafe(rec, f"selected_{rec['variant']}")
            profiles.loc[profiles["profile"].eq("e351_robust"), "selected_uploadsafe_file"] = rel(selected_path)

    profiles.to_csv(PROFILE_OUT, index=False)
    write_report(ranked, profiles, selected_path)
    print(f"wrote {rel(RANKED_OUT)} {ranked.shape}")
    print(f"wrote {rel(PROFILE_OUT)} {profiles.shape}")
    print(f"wrote {rel(REPORT_OUT)}")
    print(f"selected {rel(selected_path) if selected_path else 'none'}")
    show_cols = [
        "profile",
        "variant",
        "scale",
        "s3_alpha",
        "e351_robust_score",
        "e351_worst_axis_pct",
        "pred_delta_vs_current_p90",
        "public_analog_risk_score",
        "q1_specificity_margin",
        "plateau_support_score",
        "prob_l1_delta_vs_e349",
        "selected_uploadsafe_file",
    ]
    print(profiles[[c for c in show_cols if c in profiles.columns]].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
