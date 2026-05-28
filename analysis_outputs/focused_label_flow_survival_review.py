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

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import A2C8, KEYS, RAW05, TARGETS, feature_row  # noqa: E402
from public_selector_universe_audit import build_known_and_refs, family_name  # noqa: E402


PAIRWISE_FILES = [
    OUT / "label_flow_combo_focused_submit_pairwise_scored.csv",
    OUT / "label_flow_combo_gate_pairwise_scored.csv",
    OUT / "label_flow_targetwise_amplified_gate_pairwise_scored.csv",
    OUT / "label_flow_gated_candidate_pairwise_scored.csv",
]

PINNED_FILES = [
    "analysis_outputs/submission_label_flow_focused_6b9335b1.csv",
    "analysis_outputs/submission_label_flow_focused_1bbfb735.csv",
    "analysis_outputs/submission_label_flow_combo_3d536109.csv",
    "analysis_outputs/submission_label_flow_twampl_b8c66b64.csv",
    "analysis_outputs/submission_label_flow_gated_f1046674.csv",
    "analysis_outputs/submission_label_flow_gated_ff8df011.csv",
]

REVIEW_OUT = OUT / "focused_label_flow_survival_review.csv"
REPORT_OUT = OUT / "focused_label_flow_survival_review_report.md"


def read_pairwise_pool() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in PAIRWISE_FILES:
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        frame["pairwise_source"] = path.name
        if "source_path" not in frame.columns:
            frame["source_path"] = frame["file"].astype(str)
        frames.append(frame)
    if not frames:
        raise FileNotFoundError("No label-flow pairwise scored files found.")
    pool = pd.concat(frames, ignore_index=True, sort=False)
    pool["source_path"] = pool["source_path"].astype(str)
    pool = pool.drop_duplicates("source_path", keep="first").reset_index(drop=True)
    return pool


def select_review_paths(pool: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []

    focused = pool[pool["pairwise_source"].eq("label_flow_combo_focused_submit_pairwise_scored.csv")].copy()
    if not focused.empty:
        submit = focused[focused["pair_submit_gate"].fillna(False).astype(bool)].copy()
        rows.append(submit.sort_values("pair_delta_vs_a2c8_p90").head(80))
        rows.append(focused.sort_values("pair_delta_vs_a2c8_p90").head(40))

    for source, limit in [
        ("label_flow_combo_gate_pairwise_scored.csv", 40),
        ("label_flow_targetwise_amplified_gate_pairwise_scored.csv", 30),
        ("label_flow_gated_candidate_pairwise_scored.csv", 30),
    ]:
        sub = pool[pool["pairwise_source"].eq(source)].copy()
        if not sub.empty:
            rows.append(sub.sort_values("pair_delta_vs_a2c8_p90").head(limit))

    pinned = pool[pool["source_path"].isin(PINNED_FILES)].copy()
    if not pinned.empty:
        rows.append(pinned)

    selected = pd.concat(rows, ignore_index=True, sort=False)
    selected = selected.drop_duplicates("source_path", keep="first").reset_index(drop=True)
    missing = [path for path in PINNED_FILES if path not in set(selected["source_path"])]
    if missing:
        selected = pd.concat([selected, pd.DataFrame({"source_path": missing, "pairwise_source": "pinned_missing_pairwise"})])
    selected["resolved_path"] = selected["source_path"].map(lambda x: str((ROOT / str(x)).resolve()))
    exists_mask = [Path(path).exists() for path in selected["resolved_path"]]
    selected = selected[exists_mask].copy()
    return selected.reset_index(drop=True)


def build_candidate_rows(
    selected: pd.DataFrame,
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    ref_vecs: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for rec in selected.to_dict("records"):
        source_path = str(rec["source_path"])
        path = ROOT / source_path
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = source_path
        row["source_path"] = source_path
        row["basename"] = path.name
        row["candidate_family"] = family_name(path)
        row["pairwise_source"] = str(rec.get("pairwise_source", ""))
        rows.append(row)
    return pd.DataFrame(rows).drop_duplicates("file").reset_index(drop=True)


def target_movement_summary(candidate: pd.DataFrame) -> pd.DataFrame:
    target_cols = [f"move_abs_a2c8_{target}" for target in TARGETS]
    out = candidate[["file", *target_cols]].copy()
    out["dominant_target"] = out[target_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    out["dominant_target_move"] = out[target_cols].max(axis=1)
    out["q3_s4_move_share"] = (
        out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]
    ) / (out[target_cols].sum(axis=1) + 1e-12)
    return out[["file", "dominant_target", "dominant_target_move", "q3_s4_move_share", *target_cols]]


def add_review_scores(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    pair_submit = out["pair_submit_gate"].fillna(False).astype(bool)
    pair_control = out["pair_control_better_than_a2c8_gate"].fillna(False).astype(bool)
    pair_probe = out["pair_probe_gate"].fillna(False).astype(bool)
    conflict = out["pair_selector_conflict"].fillna(False).astype(bool)

    out["independent_p90_better_than_a2c8"] = out["selector_p90_delta_vs_a2c8_public"] < 0.0
    out["independent_mean_better_than_a2c8"] = out["selector_delta_vs_a2c8_public"] < 0.0
    out["independent_majority_beats_a2c8"] = out["beats_a2c8_scenario_rate"] >= 0.50
    out["low_bad_axis_for_label_flow"] = out["bad_axis_abs_load"] <= 0.025
    out["q3_s4_focused_move"] = out["q3_s4_move_share"] >= 0.90

    out["independent_survival_flag"] = (
        pair_submit
        & pair_control
        & pair_probe
        & ~conflict
        & out["independent_majority_beats_a2c8"]
        & out["low_bad_axis_for_label_flow"]
        & out["q3_s4_focused_move"]
    )
    out["strict_independent_survival_flag"] = out["independent_survival_flag"] & out["independent_p90_better_than_a2c8"]
    out["review_priority_score"] = (
        out["pair_delta_vs_a2c8_p90"].fillna(0.001)
        + 0.35 * out["selector_p90_delta_vs_a2c8_public"].fillna(0.001)
        + 0.10 * out["selector_delta_vs_a2c8_public"].fillna(0.001)
        + 0.00015 * out["bad_axis_abs_load"].fillna(0.0)
        + 0.00008 * out["selector_stress_spread"].fillna(0.0)
        + 0.00004 * np.maximum(out["mean_abs_move_vs_a2c8"].fillna(0.0) - 0.008, 0.0)
        - 0.00004 * out["independent_majority_beats_a2c8"].astype(float)
        - 0.00003 * out["q3_s4_focused_move"].astype(float)
    )
    return out.sort_values(
        [
            "strict_independent_survival_flag",
            "independent_survival_flag",
            "pair_submit_gate",
            "review_priority_score",
        ],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def write_report(scored: pd.DataFrame, known_stress: pd.DataFrame, selected_count: int) -> None:
    strict = scored[scored["strict_independent_survival_flag"]]
    survive = scored[scored["independent_survival_flag"]]
    pair_submit = scored[scored["pair_submit_gate"].fillna(False).astype(bool)]
    pinned = scored[scored["source_path"].isin(PINNED_FILES)].copy()
    a2c8_row = known_stress[known_stress["file"].eq(A2C8)].head(1)
    raw05_row = known_stress[known_stress["file"].eq(RAW05)].head(1)
    a2c8_p90 = float(a2c8_row["selector_p90_delta_vs_a2c8_public"].iloc[0]) if not a2c8_row.empty else float("nan")
    raw05_p90 = float(raw05_row["selector_p90_delta_vs_a2c8_public"].iloc[0]) if not raw05_row.empty else float("nan")
    corr_cols = scored[
        [
            "pair_delta_vs_a2c8_p90",
            "selector_p90_delta_vs_a2c8_public",
            "mean_abs_move_vs_a2c8",
            "bad_axis_abs_load",
        ]
    ].dropna()
    pair_old_corr = float(corr_cols["pair_delta_vs_a2c8_p90"].corr(corr_cols["selector_p90_delta_vs_a2c8_public"]))
    move_old_corr = float(corr_cols["mean_abs_move_vs_a2c8"].corr(corr_cols["selector_p90_delta_vs_a2c8_public"]))
    bad_old_corr = float(corr_cols["bad_axis_abs_load"].corr(corr_cols["selector_p90_delta_vs_a2c8_public"]))
    pair_submit_old = pair_submit["selector_p90_delta_vs_a2c8_public"].describe(percentiles=[0.1, 0.5, 0.9])
    non_pair_submit_old = scored[~scored["pair_submit_gate"].fillna(False).astype(bool)][
        "selector_p90_delta_vs_a2c8_public"
    ].describe(percentiles=[0.1, 0.5, 0.9])

    show_cols = [
        "source_path",
        "pairwise_source",
        "pair_delta_vs_a2c8_p90",
        "selector_p90_delta_vs_a2c8_public",
        "selector_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "q3_s4_move_share",
        "dominant_target",
        "mean_abs_move_vs_a2c8",
        "independent_survival_flag",
        "strict_independent_survival_flag",
        "review_priority_score",
    ]
    show_cols = [col for col in show_cols if col in scored.columns]

    lines = [
        "# Focused Label-Flow Survival Review",
        "",
        "Purpose: test whether the E14 S4+Q3 label-flow candidates still look plausible under an independent hidden-subset selector stress, rather than only the pairwise selector used to choose them.",
        "",
        "## Stress Setup",
        "",
        f"- selected label-flow candidates: `{selected_count}`",
        f"- pair-submit candidates inside review set: `{len(pair_submit)}`",
        f"- independent survival candidates: `{len(survive)}`",
        f"- strict independent survival candidates: `{len(strict)}`",
        f"- known a2c8 selector p90 delta vs a2c8 public: `{a2c8_p90:.9f}`",
        f"- known raw05 selector p90 delta vs a2c8 public: `{raw05_p90:.9f}`",
        f"- corr(pairwise p90 delta, old-selector p90 delta): `{pair_old_corr:.3f}`",
        f"- corr(move vs a2c8, old-selector p90 delta): `{move_old_corr:.3f}`",
        f"- corr(bad-axis load, old-selector p90 delta): `{bad_old_corr:.3f}`",
        "",
        "Independent survival requires pair submit/control/probe gates, no pairwise conflict, hidden-subset scenario majority beating a2c8, low bad-axis load <= 0.025, and >=90% of movement concentrated in Q3+S4. Strict survival additionally requires the old selector p90 to beat a2c8.",
        "",
        "The failure is not random noise: in this focused family, improving the pairwise p90 score is strongly anti-aligned with the older hidden-subset selector. Pair-submit candidates have old-selector p90 deltas around "
        f"`{float(pair_submit_old['50%']):.9f}` median, while non-pair-submit label-flow sensors sit around `{float(non_pair_submit_old['50%']):.9f}` median.",
        "",
        "## Top Review Candidates",
        "",
        scored[show_cols].head(30).round(9).to_csv(index=False),
        "",
        "## Pinned Frontier/Sensor Candidates",
        "",
        pinned[show_cols].round(9).to_csv(index=False) if not pinned.empty else "_No pinned candidates found._",
        "",
        "## Interpretation",
        "",
    ]
    if strict.empty and survive.empty:
        lines.extend(
            [
                "- Pairwise-positive label-flow does not survive independent hidden-subset geometry. Treat E14 as a sensor, not a submission.",
                "- The likely failure mode is selector overfit to the public-order surrogate or target-local movement that the older anchor geometry does not price as public-positive.",
            ]
        )
    elif strict.empty:
        lines.extend(
            [
                "- Some candidates survive a majority-scenario and geometry sanity gate, but none clear strict old-selector p90. That means they are plausible frontier challenges, not high-confidence LB improvements.",
                "- The useful structure remains S4-dominant with Q3 support; the independent selector is not strong enough to prove the exact weight.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one candidate clears both pairwise and independent p90 stress. This is the strongest local evidence so far for a submit-worthy S4+Q3 label-flow correction.",
                "- Compare strict survivors by movement size and pinned frontier relation before choosing submission order.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)

    pairwise_pool = read_pairwise_pool()
    selected = select_review_paths(pairwise_pool)
    candidate_rows = build_candidate_rows(selected, sample, refs, ref_vecs)

    anchor_rows = known.copy()
    anchor_rows["is_known_public"] = True
    anchor_rows["known_public_lb"] = anchor_rows["public_lb"]
    candidates_for_stress = pd.concat([anchor_rows, candidate_rows], ignore_index=True, sort=False)
    stress = candidate_stress_scores(known, candidates_for_stress)
    known_stress = stress[stress["file"].isin(known["file"].astype(str))].copy()

    pair_cols = [
        "source_path",
        "pairwise_source",
        "weights",
        "atom_ids",
        "pair_delta_vs_a2c8_mean",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "pair_delta_vs_raw05_p90",
        "pair_beats_raw05_rate",
        "pair_probe_gate",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_selector_conflict",
        "pair_rank_score",
        "energy_delta_vs_base",
        "raw_dist_delta_vs_base",
    ]
    pair_cols = [col for col in pair_cols if col in pairwise_pool.columns]
    pair_meta = pairwise_pool[pair_cols].drop_duplicates("source_path")
    target_moves = target_movement_summary(candidate_rows)
    geom_cols = [
        "file",
        "source_path",
        "basename",
        "candidate_family",
        "min_prob",
        "max_prob",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
        "max_abs_move_vs_a2c8",
        "bad_axis_abs_load",
        "raw05_a2c8_compat_energy",
        "good_span_residual_ratio",
    ]
    geom_cols = [col for col in geom_cols if col in candidate_rows.columns]

    reviewed = stress[stress["file"].isin(candidate_rows["file"].astype(str))].copy()
    reviewed = reviewed.merge(candidate_rows[geom_cols].drop_duplicates("file"), on="file", how="left", suffixes=("", "_geom"))
    reviewed = reviewed.merge(pair_meta, on="source_path", how="left")
    reviewed = reviewed.merge(target_moves, on="file", how="left")
    reviewed = add_review_scores(reviewed)
    reviewed.to_csv(REVIEW_OUT, index=False)
    write_report(reviewed, known_stress, len(selected))

    print(REPORT_OUT)
    print(
        {
            "selected": int(len(selected)),
            "reviewed": int(len(reviewed)),
            "pair_submit": int(reviewed["pair_submit_gate"].fillna(False).astype(bool).sum()),
            "independent_survival": int(reviewed["independent_survival_flag"].sum()),
            "strict_independent_survival": int(reviewed["strict_independent_survival_flag"].sum()),
        }
    )
    cols = [
        "source_path",
        "pair_delta_vs_a2c8_p90",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "q3_s4_move_share",
        "independent_survival_flag",
        "strict_independent_survival_flag",
        "review_priority_score",
    ]
    print(reviewed[cols].head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
