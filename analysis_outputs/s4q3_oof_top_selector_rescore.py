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


AUDIT_IN = OUT / "s4q3_oof_anchor_audit.csv"
DETAIL_OUT = OUT / "s4q3_oof_top_selector_rescore.csv"
SHORTLIST_OUT = OUT / "s4q3_oof_top_selector_rescore_shortlist.csv"
SUMMARY_OUT = OUT / "s4q3_oof_top_selector_rescore_summary.csv"
REPORT_OUT = OUT / "s4q3_oof_top_selector_rescore_report.md"
TOP_N = 400
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


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


def candidate_pool_from_oof() -> pd.DataFrame:
    audit = pd.read_csv(AUDIT_IN)
    local = audit[
        audit["local_q3s4_strong"].fillna(False).astype(bool)
        & audit["matched_source_path"].notna()
    ].copy()
    local = local.sort_values(
        ["q3s4_delta_vs_stage2_oof", "q3s4_scenario_p90"], ascending=[True, True]
    ).head(TOP_N)

    records: list[dict[str, object]] = []
    seen: set[str] = set()

    def add(path_value: object, source: str, priority: float, extra: dict[str, object] | None = None) -> None:
        path = resolve_submission(path_value)
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
            "pool_priority": priority,
        }
        if extra:
            rec.update(extra)
        records.append(rec)

    for name in KEY_ANCHORS:
        add(name, "known_anchor", 0.0)

    for rank, (_, row) in enumerate(local.iterrows(), start=1):
        extra = {
            "oof_path": row["oof_path"],
            "oof_rank": rank,
            "oof_q3s4_delta_vs_stage2": row["q3s4_delta_vs_stage2_oof"],
            "oof_q3_delta_vs_stage2": row["q3_delta_vs_stage2_oof"],
            "oof_s4_delta_vs_stage2": row["s4_delta_vs_stage2_oof"],
            "oof_q3s4_scenario_p90": row["q3s4_scenario_p90"],
            "oof_q3s4_scenario_win_rate": row["q3s4_scenario_win_rate"],
        }
        add(row["matched_source_path"], "top_oof_q3s4", float(rank), extra)

    if not records:
        raise RuntimeError("No OOF candidates resolved to submission CSVs.")
    return pd.DataFrame(records)


def add_shape_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    move_cols = [f"move_abs_a2c8_{t}" for t in TARGETS]
    total = out[move_cols].sum(axis=1).replace(0, np.nan)
    out["q3s4_move"] = out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]
    out["q3s4_move_share"] = out["q3s4_move"] / total
    out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    return out


def main() -> None:
    if not AUDIT_IN.exists():
        raise FileNotFoundError("Run s4q3_oof_anchor_audit.py first.")

    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _ = evaluate_pairwise_models(known)

    pool = candidate_pool_from_oof()
    features = build_candidate_features(pool, sample, refs, ref_vecs)
    features = add_shape_metrics(features)

    old_scores = candidate_stress_scores(known, features)
    old_keep = [
        "file",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
    ]
    old_keep = [c for c in old_keep if c in old_scores.columns]
    features = features.merge(old_scores[old_keep], on="file", how="left", suffixes=("", "_old"))

    known_lb = known.set_index("file")["public_lb"].to_dict()
    features["known_public_lb"] = features["basename"].map(known_lb)
    features["is_known_public"] = features["known_public_lb"].notna()
    scored = score_candidates(known, features, model_df)

    scored["old_majority"] = scored["beats_a2c8_scenario_rate"].fillna(0) >= 0.50
    scored["pair_majority"] = scored["pair_beats_a2c8_rate"].fillna(0) >= 0.70
    scored["pair_p90_negative"] = scored["pair_delta_vs_a2c8_p90"].fillna(9) < 0
    scored["local_q3s4_strong"] = scored["pool_source"].eq("top_oof_q3s4")
    scored["oof_selector_anchor_like"] = (
        scored["local_q3s4_strong"]
        & scored["pair_p90_negative"]
        & scored["pair_majority"]
        & scored["old_majority"]
    )
    scored["strict_s4q3_oof_anchor_like"] = (
        scored["oof_selector_anchor_like"]
        & (scored["q3s4_move_share"].fillna(0) >= 0.70)
        & (scored["selector_p90_delta_vs_a2c8_public"].fillna(9) <= 0.00058)
    )

    scored.to_csv(DETAIL_OUT, index=False)
    shortlist_cols = [
        "source_path",
        "oof_rank",
        "oof_q3s4_delta_vs_stage2",
        "oof_q3s4_scenario_p90",
        "oof_q3s4_scenario_win_rate",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "q3s4_move_share",
        "dominant_target",
        "pair_probe_gate",
        "pair_control_better_than_a2c8_gate",
        "pair_submit_gate",
        "pair_selector_conflict",
        "oof_selector_anchor_like",
        "strict_s4q3_oof_anchor_like",
    ]
    shortlist_cols = [c for c in shortlist_cols if c in scored.columns]
    shortlist = scored[
        scored["pool_source"].eq("top_oof_q3s4")
        | scored["is_known_public"].fillna(False)
        | scored["oof_selector_anchor_like"]
        | scored["strict_s4q3_oof_anchor_like"]
    ].sort_values(
        ["strict_s4q3_oof_anchor_like", "oof_selector_anchor_like", "oof_rank"],
        ascending=[False, False, True],
    )
    shortlist[shortlist_cols].head(120).to_csv(SHORTLIST_OUT, index=False)

    top = scored[scored["pool_source"].eq("top_oof_q3s4")].copy()
    summary = pd.DataFrame(
        [
            {
                "top_oof_scored": len(top),
                "pair_p90_negative": int(top["pair_p90_negative"].sum()),
                "pair_majority": int(top["pair_majority"].sum()),
                "old_majority": int(top["old_majority"].sum()),
                "pair_probe_gate": int(top["pair_probe_gate"].fillna(False).sum()),
                "pair_control_gate": int(top["pair_control_better_than_a2c8_gate"].fillna(False).sum()),
                "pair_submit_gate": int(top["pair_submit_gate"].fillna(False).sum()),
                "selector_conflict": int(top["pair_selector_conflict"].fillna(False).sum()),
                "q3s4_shape70": int((top["q3s4_move_share"].fillna(0) >= 0.70).sum()),
                "oof_selector_anchor_like": int(top["oof_selector_anchor_like"].sum()),
                "strict_s4q3_oof_anchor_like": int(top["strict_s4q3_oof_anchor_like"].sum()),
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)

    corr_lines = []
    for ycol in ["pair_delta_vs_a2c8_p90", "selector_p90_delta_vs_a2c8_public"]:
        sub = top[["oof_q3s4_delta_vs_stage2", ycol]].dropna()
        if len(sub) >= 5:
            corr_lines.append(
                f"- corr(oof_q3s4_delta_vs_stage2, {ycol}) = `{sub['oof_q3s4_delta_vs_stage2'].corr(sub[ycol]):.3f}` over n={len(sub)}"
            )

    best_cols = [
        "source_path",
        "oof_rank",
        "oof_q3s4_delta_vs_stage2",
        "oof_q3s4_scenario_p90",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "q3s4_move_share",
        "dominant_target",
        "pair_probe_gate",
        "pair_selector_conflict",
        "oof_selector_anchor_like",
    ]
    best_cols = [c for c in best_cols if c in scored.columns]
    top_local = top.sort_values("oof_rank").head(20)[best_cols]
    best_pair = top.sort_values("pair_delta_vs_a2c8_p90").head(20)[best_cols]
    anchors = top[top["oof_selector_anchor_like"]][best_cols]

    lines = [
        "# S4/Q3 OOF Top Selector Rescore",
        "",
        "Question: do the strongest local Q3/S4 OOF candidates survive direct pairwise and hidden-subset selector scoring?",
        "",
        "## Summary",
        "",
        markdown_table(summary),
        "",
        "## Correlations",
        "",
        "\n".join(corr_lines) if corr_lines else "_No sufficient overlap._",
        "",
        "## Top Local OOF Candidates After Selector Scoring",
        "",
        markdown_table(top_local),
        "",
        "## Best Pairwise Among Top OOF Candidates",
        "",
        markdown_table(best_pair),
        "",
        "## OOF Selector Anchor-Like Candidates",
        "",
        markdown_table(anchors),
        "",
        "## Interpretation",
        "",
    ]
    if int(summary.loc[0, "strict_s4q3_oof_anchor_like"]) == 0:
        lines.extend(
            [
                "- The strongest local Q3/S4 OOF candidates do not provide the missing independent S4/Q3 public anchor.",
                "- Local OOF strength and public-sensitive selector support are different views; local Q3/S4 gains alone should not be promoted to public submissions.",
                "- This strengthens the validation-mismatch diagnosis: the missing object is a selector-resolvable public-positive movement, not merely another local-CV strong S4/Q3 candidate.",
            ]
        )
    else:
        lines.extend(
            [
                "- A local Q3/S4 OOF candidate also survives both selectors.",
                "- Decompose this candidate family before any public submission because OOF-derived families can still encode public-mask shortcuts.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
