from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_pairwise_order_selector import (  # noqa: E402
    KEY_ANCHORS,
    build_candidate_features,
    build_known_and_refs,
    evaluate_pairwise_models,
    rel_path,
    resolve_submission,
    score_candidates,
)


DETAIL_OUT = OUT / "block_measurement_selector_rescore.csv"
FAMILY_OUT = OUT / "block_measurement_selector_rescore_family_summary.csv"
SHORTLIST_OUT = OUT / "block_measurement_selector_rescore_shortlist.csv"
SUMMARY_OUT = OUT / "block_measurement_selector_rescore_summary.csv"
REPORT_OUT = OUT / "block_measurement_selector_rescore_report.md"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

TABLE_SOURCES: list[tuple[str, str, int]] = [
    ("block_neutral_safe", "block_scale_jepa_neutral_safe.csv", 400),
    ("block_neutral_shortlist", "block_scale_jepa_neutral_shortlist.csv", 400),
    ("block_neutral_saved_proxy", "block_scale_jepa_neutral_saved_proxy.csv", 400),
    ("block_target_shortlist", "block_scale_jepa_target_shortlist.csv", 400),
    ("block_target_proxy", "block_scale_jepa_target_candidate_proxy.csv", 500),
    ("block_submission_shortlist", "block_scale_jepa_submission_shortlist.csv", 250),
    ("block_axis_shortlist", "block_scale_jepa_axis_submission_shortlist.csv", 250),
    ("block_axis_combined", "block_scale_jepa_axis_combined_shortlist_proxy.csv", 250),
    ("block_axis_projector", "block_scale_jepa_axis_projector_selected.csv", 250),
    ("block_public_blend_selected", "block_scale_jepa_public_blend_selected.csv", 500),
    ("block_public_blend_shortlist", "block_scale_jepa_public_blend_shortlist.csv", 500),
    ("block_public_blend_proxy", "block_scale_jepa_public_blend_proxy.csv", 500),
    ("blockpublic_q3s4_selected", "block_public_jepa_q3s4_selected.csv", 250),
    ("blockpublic_q3s4_shortlist", "block_public_jepa_q3s4_shortlist.csv", 250),
    ("blockpublic_q3s4_refine_selected", "block_public_jepa_q3s4_refine_selected.csv", 250),
    ("blockpublic_q3s4_refine_shortlist", "block_public_jepa_q3s4_refine_shortlist.csv", 250),
    ("hidden_block_rateprobe", "hidden_block_rateprobe_shortlist.csv", 350),
    ("hidden_block_rateprobe_safe", "hidden_block_rateprobe_neutral_mix_safe_scores.csv", 350),
    ("hidden_block_sequence", "hidden_block_sequence_motif_shortlist.csv", 350),
    ("hidden_block_sequence_safe", "hidden_block_sequence_motif_neutral_mix_safe_scores.csv", 350),
    ("hidden_block_sequence_cellgate", "hidden_block_sequence_motif_cellgate_safe_scores.csv", 350),
    ("hidden_block_orthogonal", "hidden_block_orthogonal_gate_selected.csv", 250),
    ("jepa_block_consensus_gate", "jepa_block_consensus_gate_selected.csv", 350),
    ("jepa_block_rawcorrector", "jepa_block_consensus_rawcorrector_selected.csv", 350),
    ("jepa_block_rawcorrector_refine", "jepa_block_consensus_rawcorrector_refine_selected.csv", 350),
    ("jepa_block_rawcorrector_micro", "jepa_block_consensus_rawcorrector_microrefine_selected.csv", 350),
    ("jepa_block_count_shift", "jepa_block_count_shift_selected.csv", 350),
    ("jepa_public_blockentropy", "jepa_public_blockentropy_shortlist.csv", 350),
    ("public_blockentropy", "public_blockentropy_selected.csv", 350),
    ("raw05_blockcount_refine", "raw05_jepa_blockcount_regularized_refine_shortlist.csv", 350),
    ("presleep_anchor_saved", "presleep_anchor_saved_candidates.csv", 350),
    ("presleep_multitarget_saved", "presleep_multitarget_saved_candidates.csv", 350),
    ("public_presleep_blend", "public_presleep_blend_candidates.csv", 500),
    ("public_presleep_multitarget", "public_presleep_multitarget_candidates.csv", 500),
    ("public_presleep_q3", "public_presleep_q3_candidates.csv", 500),
    ("presleep_orthcap", "presleep_orthcap_candidates.csv", 350),
]

GLOB_SOURCES: list[tuple[str, str, int]] = [
    ("glob_blockscale", "submission_blockscale*.csv", 900),
    ("glob_blockpublic", "submission_blockpublic*.csv", 300),
    ("glob_hiddenblock", "submission_hiddenblock*.csv", 1200),
    ("glob_presleep", "submission_*presleep*.csv", 800),
    ("glob_raw05_block", "submission_raw05_jepa*block*.csv", 250),
]

SORT_HINTS = [
    "pair_rank_score",
    "selection_score",
    "submission_priority_score",
    "candidate_selector_risk",
    "posterior_expected_public_vs_anchor",
    "raw_axis_expected_public_vs_stage2",
    "mean_expected",
    "robust_score",
    "scenario_robust_score",
    "bridge_score",
    "oof_mean_loss",
    "candidate_loss",
    "geometry_delta",
]


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def family_bucket(path: Path, source: str) -> str:
    name = path.name
    if "blockscale" in name:
        return "block_scale_jepa"
    if "blockpublic" in name or "public_blockentropy" in name:
        return "public_block_jepa"
    if "hiddenblock" in name or "hidden_block" in source:
        return "hidden_block"
    if "presleep" in name or "presleep" in source:
        return "presleep_measurement"
    if "raw05_jepa" in name and "block" in name:
        return "raw05_block_jepa"
    if "jepa_block" in name or "block_count" in name or "blockcount" in name:
        return "jepa_block"
    return source


def sort_source_frame(frame: pd.DataFrame) -> pd.DataFrame:
    sort_cols = [col for col in SORT_HINTS if col in frame.columns]
    if not sort_cols:
        return frame
    work = frame.copy()
    ascending = []
    for col in sort_cols:
        if col in {"bridge_score"}:
            ascending.append(False)
        else:
            ascending.append(True)
    return work.sort_values(sort_cols, ascending=ascending)


def add_record(
    records: list[dict[str, object]],
    seen: set[str],
    value: object,
    source: str,
    priority: float,
    extra: dict[str, object] | None = None,
) -> None:
    path = resolve_submission(value)
    if path is None:
        return
    key = str(path.resolve())
    if key in seen:
        return
    seen.add(key)
    rec = {
        "resolved_path": key,
        "source_path": rel_path(path),
        "basename": path.name,
        "pool_source": source,
        "pool_priority": float(priority),
        "candidate_bucket": family_bucket(path, source),
    }
    if extra:
        for k, v in extra.items():
            if k not in rec:
                rec[k] = v
    records.append(rec)


def candidate_pool() -> pd.DataFrame:
    records: list[dict[str, object]] = []
    seen: set[str] = set()

    for name in KEY_ANCHORS:
        add_record(records, seen, name, "known_anchor", 0.0)

    for source, file_name, limit in TABLE_SOURCES:
        path = OUT / file_name
        if not path.exists():
            continue
        try:
            frame = pd.read_csv(path)
        except Exception as exc:  # noqa: BLE001
            print(f"skip table {path}: {type(exc).__name__}: {exc}", flush=True)
            continue
        if "file" not in frame.columns:
            continue
        frame = sort_source_frame(frame).head(limit)
        for rank, (_, row) in enumerate(frame.iterrows(), start=1):
            extra = {
                "source_table": file_name,
                "source_rank": rank,
            }
            for col in SORT_HINTS:
                if col in row:
                    extra[f"src_{col}"] = row[col]
            add_record(records, seen, row.get("file"), source, float(rank), extra)

    for source, pattern, limit in GLOB_SOURCES:
        paths = sorted(OUT.glob(pattern))[:limit]
        for rank, path in enumerate(paths, start=1):
            add_record(records, seen, path, source, float(10_000 + rank))

    if not records:
        raise RuntimeError("No block/measurement candidates collected.")
    pool = pd.DataFrame(records)
    pool = pool.sort_values(["pool_priority", "pool_source", "source_path"]).reset_index(drop=True)
    return pool


def add_shape_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS]
    total = out[move_cols].sum(axis=1).replace(0, np.nan)
    out["q_group_move_share"] = out[[f"move_abs_a2c8_{t}" for t in ["Q1", "Q2", "Q3"]]].sum(axis=1) / total
    out["s_group_move_share"] = out[[f"move_abs_a2c8_{t}" for t in ["S1", "S2", "S3", "S4"]]].sum(axis=1) / total
    out["q3s4_move_share"] = (out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]) / total
    out["q3_move_share"] = out["move_abs_a2c8_Q3"] / total
    out["s4_move_share"] = out["move_abs_a2c8_S4"] / total
    out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    out["movement_scale"] = out["mean_abs_move_vs_a2c8"].fillna(0.0)
    out["large_lowbad_movement"] = (
        (out["movement_scale"] >= 0.0015)
        & (out["bad_axis_abs_load"].fillna(9.0) <= 0.055)
        & (out["raw05_a2c8_compat_energy"].fillna(9.0) <= 0.020)
    )
    return out


def summarize(scored: pd.DataFrame, model_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = scored[~scored["pool_source"].eq("known_anchor")].copy()
    summary = pd.DataFrame(
        [
            {
                "candidate_pool": int(len(target)),
                "pair_p90_negative": int((target["pair_delta_vs_a2c8_p90"].fillna(9) < 0).sum()),
                "pair_majority": int((target["pair_beats_a2c8_rate"].fillna(0) >= 0.70).sum()),
                "old_majority": int((target["beats_a2c8_scenario_rate"].fillna(0) >= 0.50).sum()),
                "old_p90_le_a2c8_known_gap": int(
                    (target["selector_p90_delta_vs_a2c8_public"].fillna(9) <= 0.00058).sum()
                ),
                "pair_probe_gate": int(target["pair_probe_gate"].fillna(False).sum()),
                "pair_control_gate": int(target["pair_control_better_than_a2c8_gate"].fillna(False).sum()),
                "pair_submit_gate": int(target["pair_submit_gate"].fillna(False).sum()),
                "pair_selector_conflict": int(target["pair_selector_conflict"].fillna(False).sum()),
                "two_selector_majority": int(
                    (
                        (target["pair_beats_a2c8_rate"].fillna(0) >= 0.70)
                        & (target["beats_a2c8_scenario_rate"].fillna(0) >= 0.50)
                    ).sum()
                ),
                "large_lowbad_movement": int(target["large_lowbad_movement"].fillna(False).sum()),
                "large_lowbad_two_selector": int(
                    (
                        target["large_lowbad_movement"].fillna(False)
                        & (target["pair_beats_a2c8_rate"].fillna(0) >= 0.70)
                        & (target["beats_a2c8_scenario_rate"].fillna(0) >= 0.50)
                    ).sum()
                ),
                "pairwise_models_order_pass": int(model_df["order_pass"].fillna(False).sum()),
                "pairwise_models_tested": int(len(model_df)),
            }
        ]
    )

    group_cols = ["candidate_bucket", "pool_source"]
    rows: list[dict[str, object]] = []
    for keys, group in target.groupby(group_cols, dropna=False, sort=True):
        bucket, source = keys
        rows.append(
            {
                "candidate_bucket": bucket,
                "pool_source": source,
                "n": int(len(group)),
                "pair_p90_negative": int((group["pair_delta_vs_a2c8_p90"].fillna(9) < 0).sum()),
                "pair_majority": int((group["pair_beats_a2c8_rate"].fillna(0) >= 0.70).sum()),
                "old_majority": int((group["beats_a2c8_scenario_rate"].fillna(0) >= 0.50).sum()),
                "pair_probe_gate": int(group["pair_probe_gate"].fillna(False).sum()),
                "pair_control_gate": int(group["pair_control_better_than_a2c8_gate"].fillna(False).sum()),
                "pair_submit_gate": int(group["pair_submit_gate"].fillna(False).sum()),
                "pair_conflict": int(group["pair_selector_conflict"].fillna(False).sum()),
                "two_selector_majority": int(
                    (
                        (group["pair_beats_a2c8_rate"].fillna(0) >= 0.70)
                        & (group["beats_a2c8_scenario_rate"].fillna(0) >= 0.50)
                    ).sum()
                ),
                "large_lowbad": int(group["large_lowbad_movement"].fillna(False).sum()),
                "best_pair_p90": float(group["pair_delta_vs_a2c8_p90"].min()),
                "best_old_p90": float(group["selector_p90_delta_vs_a2c8_public"].min()),
                "median_move": float(group["movement_scale"].median()),
                "dominant_target_top": str(group["dominant_target"].mode().iloc[0]) if len(group) else "",
            }
        )
    family = pd.DataFrame(rows)
    if not family.empty:
        family = family.sort_values(
            ["two_selector_majority", "pair_submit_gate", "pair_probe_gate", "best_pair_p90", "best_old_p90"],
            ascending=[False, False, False, True, True],
        ).reset_index(drop=True)
    return summary, family


def write_report(scored: pd.DataFrame, summary: pd.DataFrame, family: pd.DataFrame) -> None:
    candidates = scored[~scored["pool_source"].eq("known_anchor")].copy()
    shortlist_cols = [
        "source_path",
        "candidate_bucket",
        "pool_source",
        "pool_priority",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "pair_delta_vs_raw05_p90",
        "pair_beats_raw05_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "large_lowbad_movement",
        "q3s4_move_share",
        "s_group_move_share",
        "dominant_target",
        "pair_probe_gate",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_selector_conflict",
        "pair_rank_score",
    ]
    shortlist_cols = [col for col in shortlist_cols if col in scored.columns]

    two_selector = candidates[
        (candidates["pair_beats_a2c8_rate"].fillna(0) >= 0.70)
        & (candidates["beats_a2c8_scenario_rate"].fillna(0) >= 0.50)
    ].copy()
    gates = candidates[
        candidates["pair_submit_gate"].fillna(False)
        | candidates["pair_control_better_than_a2c8_gate"].fillna(False)
        | candidates["pair_probe_gate"].fillna(False)
    ].copy()
    best_pair = candidates.sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]).head(25)
    best_old = candidates.sort_values(["selector_p90_delta_vs_a2c8_public", "pair_delta_vs_a2c8_p90"]).head(25)
    large_lowbad = candidates[candidates["large_lowbad_movement"].fillna(False)].sort_values(
        ["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]
    ).head(25)

    lines = [
        "# Block / Measurement Selector Rescore",
        "",
        "Question: do existing block, hidden-block, pre-sleep measurement, or raw05-block candidates contain a selector-resolvable movement that was missed by the S4/Q3-focused audits?",
        "",
        "This is an audit of already generated submissions. It does not train a new model and does not use public LB as a direct optimizer.",
        "",
        "## Summary",
        "",
        markdown_table(summary),
        "",
        "## Family Summary",
        "",
        markdown_table(family.head(40)),
        "",
        "## Two-Selector Majority Candidates",
        "",
        markdown_table(two_selector[shortlist_cols].head(40)),
        "",
        "## Pairwise Gate Candidates",
        "",
        markdown_table(gates[shortlist_cols].sort_values(["pair_submit_gate", "pair_probe_gate", "pair_rank_score"], ascending=[False, False, True]).head(40)),
        "",
        "## Best Pairwise P90",
        "",
        markdown_table(best_pair[shortlist_cols]),
        "",
        "## Best Old Hidden-Subset P90",
        "",
        markdown_table(best_old[shortlist_cols]),
        "",
        "## Large Low-Bad Movement Candidates",
        "",
        markdown_table(large_lowbad[shortlist_cols]),
        "",
        "## Read",
        "",
        "- A useful candidate here must not merely be locally strong; it must get at least pairwise majority support and old hidden-subset majority support, while keeping bad-axis load low.",
        "- If two-selector majority and large-lowbad two-selector counts are zero, then the existing block/measurement universe is not the missing large safe movement.",
        "- If pairwise gates exist but old majority is absent, the family is another selector-conflict sensor, not a submit candidate.",
        "",
        "## Files",
        "",
        f"- `{DETAIL_OUT.name}`",
        f"- `{FAMILY_OUT.name}`",
        f"- `{SHORTLIST_OUT.name}`",
        f"- `{SUMMARY_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _ = evaluate_pairwise_models(known)

    pool = candidate_pool()
    print(f"block/measurement candidate pool after dedupe: {len(pool)}", flush=True)
    features = build_candidate_features(pool, sample, refs, ref_vecs)
    features = add_shape_metrics(features)

    known_lb = known.set_index("file")["public_lb"].to_dict()
    features["known_public_lb"] = features["basename"].map(known_lb)
    features["is_known_public"] = features["known_public_lb"].notna()

    old_input = features.copy()
    old_input["file"] = old_input["basename"]
    old_scores = candidate_stress_scores(known, old_input)
    old_keep = [
        "file",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
    ]
    old_keep = [col for col in old_keep if col in old_scores.columns]
    old_scores = old_scores[old_keep].rename(columns={"file": "basename"})
    features = features.merge(old_scores, on="basename", how="left")

    scored = score_candidates(known, features, model_df)
    scored["pair_majority"] = scored["pair_beats_a2c8_rate"].fillna(0) >= 0.70
    scored["old_majority"] = scored["beats_a2c8_scenario_rate"].fillna(0) >= 0.50
    scored["two_selector_majority"] = scored["pair_majority"] & scored["old_majority"]
    scored["old_p90_le_a2c8_known_gap"] = scored["selector_p90_delta_vs_a2c8_public"].fillna(9) <= 0.00058
    scored["strict_large_safe"] = (
        scored["two_selector_majority"]
        & scored["large_lowbad_movement"].fillna(False)
        & scored["old_p90_le_a2c8_known_gap"]
        & (scored["pair_delta_vs_a2c8_p90"].fillna(9) < 0)
    )

    summary, family = summarize(scored, model_df)
    scored.to_csv(DETAIL_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)

    shortlist_cols = [
        "source_path",
        "candidate_bucket",
        "pool_source",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "movement_scale",
        "large_lowbad_movement",
        "dominant_target",
        "pair_probe_gate",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_selector_conflict",
        "two_selector_majority",
        "strict_large_safe",
        "pair_rank_score",
    ]
    shortlist_cols = [col for col in shortlist_cols if col in scored.columns]
    shortlist = scored[
        scored["is_known_public"].fillna(False)
        | scored["pair_submit_gate"].fillna(False)
        | scored["pair_control_better_than_a2c8_gate"].fillna(False)
        | scored["pair_probe_gate"].fillna(False)
        | scored["two_selector_majority"].fillna(False)
        | scored["strict_large_safe"].fillna(False)
    ].copy()
    if shortlist.empty:
        shortlist = scored.sort_values(["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]).head(120)
    shortlist[shortlist_cols].sort_values(
        ["strict_large_safe", "two_selector_majority", "pair_submit_gate", "pair_probe_gate", "pair_rank_score"],
        ascending=[False, False, False, False, True],
    ).head(200).to_csv(SHORTLIST_OUT, index=False)

    write_report(scored, summary, family)

    print(REPORT_OUT)
    print("[summary]")
    print(summary.to_string(index=False))
    print("[family top]")
    print(family.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
