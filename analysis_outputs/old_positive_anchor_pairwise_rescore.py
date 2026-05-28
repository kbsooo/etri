from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS  # noqa: E402
from public_pairwise_order_selector import (  # noqa: E402
    evaluate_pairwise_models,
    build_candidate_features,
    rel_path,
    resolve_submission,
    score_candidates,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


UNIVERSE_IN = OUT / "public_selector_universe_audit_candidates.csv"
RESCORED_OUT = OUT / "old_positive_anchor_pairwise_rescore.csv"
SHORT_OUT = OUT / "old_positive_anchor_pairwise_rescore_shortlist.csv"
REPORT_OUT = OUT / "old_positive_anchor_pairwise_rescore_report.md"


def make_pool(universe: pd.DataFrame) -> pd.DataFrame:
    masks = {
        "old_scenario_majority": universe["scenario_majority_beats_a2c8"].fillna(False).astype(bool),
        "old_frontier_escape": universe["frontier_escape_candidate"].fillna(False).astype(bool),
        "old_novel_frontier": universe["novel_frontier_candidate"].fillna(False).astype(bool),
    }
    selected = pd.concat(
        [
            universe[masks["old_scenario_majority"]],
            universe[masks["old_frontier_escape"]],
            universe[masks["old_novel_frontier"]],
            universe.sort_values("submission_priority_score").head(200),
        ],
        ignore_index=True,
        sort=False,
    ).drop_duplicates("source_path")
    rows: list[dict[str, object]] = []
    for rec in selected.to_dict("records"):
        path = resolve_submission(rec.get("source_path") or rec.get("file"))
        if path is None:
            continue
        row = {
            "resolved_path": str(path),
            "source_path": rel_path(path),
            "basename": path.name,
            "pool_source": "old_positive_rescore",
            "pool_priority": float(rec.get("submission_priority_score", 1.0)),
        }
        for key, value in rec.items():
            if key not in row:
                row[key] = value
        rows.append(row)
    pool = pd.DataFrame(rows)
    return pool.drop_duplicates("resolved_path").reset_index(drop=True)


def add_target_shape(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS]
    out["total_target_move"] = out[move_cols].sum(axis=1)
    out["q3s4_move"] = out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]
    out["q3s4_move_share"] = out["q3s4_move"] / (out["total_target_move"] + 1e-12)
    out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    out["two_selector_majority"] = (
        out["scenario_majority_beats_a2c8"].fillna(False).astype(bool)
        & (out["pair_beats_a2c8_rate"] >= 0.50)
    )
    out["two_selector_probe"] = (
        out["scenario_majority_beats_a2c8"].fillna(False).astype(bool)
        & out["pair_probe_gate"].fillna(False).astype(bool)
    )
    out["two_selector_control"] = (
        out["scenario_majority_beats_a2c8"].fillna(False).astype(bool)
        & out["pair_control_better_than_a2c8_gate"].fillna(False).astype(bool)
    )
    out["q3s4_anchor_like"] = (
        out["q3s4_move_share"].ge(0.70)
        & out["scenario_majority_beats_a2c8"].fillna(False).astype(bool)
        & out["pair_beats_a2c8_rate"].ge(0.50)
        & out["low_public_bad_axis"].fillna(False).astype(bool)
    )
    return out


def write_report(scored: pd.DataFrame) -> None:
    cols = [
        "source_path",
        "candidate_family",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "pair_delta_vs_raw05_p90",
        "pair_beats_raw05_rate",
        "q3s4_move_share",
        "dominant_target",
        "move_abs_a2c8_Q3",
        "move_abs_a2c8_S4",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "pair_probe_gate",
        "pair_control_better_than_a2c8_gate",
        "pair_selector_conflict",
    ]
    cols = [c for c in cols if c in scored.columns]
    old_majority = scored[scored["scenario_majority_beats_a2c8"].fillna(False).astype(bool)]
    two_majority = scored[scored["two_selector_majority"]]
    two_probe = scored[scored["two_selector_probe"]]
    q3s4 = scored[scored["q3s4_anchor_like"]]
    q3s4_shape = scored[scored["q3s4_move_share"].ge(0.70)]

    lines = [
        "# Old-Positive Anchor Pairwise Rescore",
        "",
        "Purpose: check whether candidates supported by the old hidden-subset selector also survive pairwise public-order stress, and whether any such candidate provides an independent S4/Q3 positive anchor.",
        "",
        "## Counts",
        "",
        f"- rescored candidates: `{len(scored)}`",
        f"- old scenario-majority candidates: `{len(old_majority)}`",
        f"- old-majority AND pair-majority candidates: `{len(two_majority)}`",
        f"- old-majority AND pair-probe candidates: `{len(two_probe)}`",
        f"- q3/s4 share >= 0.70 candidates: `{len(q3s4_shape)}`",
        f"- q3/s4 anchor-like candidates: `{len(q3s4)}`",
        "",
        "## Old-Majority Candidates",
        "",
        old_majority.sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"])[cols].head(40).round(9).to_csv(index=False),
        "",
        "## Q3/S4-Shaped Candidates",
        "",
        q3s4_shape.sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"])[cols].head(40).round(9).to_csv(index=False),
        "",
        "## Two-Selector Agreement Candidates",
        "",
        two_majority.sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"])[cols].head(40).round(9).to_csv(index=False)
        if len(two_majority)
        else "_None._",
        "",
        "## Interpretation",
        "",
    ]
    if q3s4.empty and two_majority.empty:
        lines.extend(
            [
                "- The existing old-positive universe does not contain an independent S4/Q3 positive anchor. Old-majority candidates are stage2-like broad moves, while Q3/S4-shaped candidates are not old-majority and do not clear pairwise p90.",
                "- This supports the E15/E16 reading: S4/Q3 label-flow is a real semantic direction but underidentified by current public anchors.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one agreement candidate exists. It should be reviewed as a possible anchor-like calibration source before any public submission.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    universe = pd.read_csv(UNIVERSE_IN)
    pool = make_pool(universe)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _ = evaluate_pairwise_models(known)
    features = build_candidate_features(pool, sample, refs, ref_vecs)
    scored = add_target_shape(score_candidates(known, features, model_df))
    scored.to_csv(RESCORED_OUT, index=False)
    shortlist = scored[
        scored["two_selector_majority"]
        | scored["two_selector_probe"]
        | scored["q3s4_anchor_like"]
        | scored["pair_probe_gate"].fillna(False).astype(bool)
    ].copy()
    if shortlist.empty:
        shortlist = scored.sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]).head(80)
    shortlist.to_csv(SHORT_OUT, index=False)
    write_report(scored)
    print(REPORT_OUT)
    print(
        {
            "rescored": int(len(scored)),
            "old_majority": int(scored["scenario_majority_beats_a2c8"].fillna(False).astype(bool).sum()),
            "two_selector_majority": int(scored["two_selector_majority"].sum()),
            "two_selector_probe": int(scored["two_selector_probe"].sum()),
            "q3s4_anchor_like": int(scored["q3s4_anchor_like"].sum()),
        }
    )


if __name__ == "__main__":
    main()
