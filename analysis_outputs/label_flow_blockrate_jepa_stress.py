from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_pairwise_order_selector import (  # noqa: E402
    build_candidate_features,
    evaluate_pairwise_models,
    rel_path,
    score_candidates,
)
from public_selector_universe_audit import build_known_and_refs, family_name  # noqa: E402


REPORT = ANALYSIS / "label_flow_blockrate_jepa_stress_report.md"
SEMANTIC_SUMMARY_OUT = ANALYSIS / "label_flow_blockrate_jepa_semantic_summary.csv"
DOWNSTREAM_SUMMARY_OUT = ANALYSIS / "label_flow_blockrate_jepa_downstream_summary.csv"
PAIRWISE_OUT = ANALYSIS / "label_flow_blockrate_jepa_pairwise_scored.csv"
PAIRWISE_SHORTLIST_OUT = ANALYSIS / "label_flow_blockrate_jepa_pairwise_shortlist.csv"


def safe_read(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def fold_stability(frame: pd.DataFrame, keys: list[str], metric: str, higher_is_better: bool = True) -> pd.DataFrame:
    if frame.empty or metric not in frame.columns:
        return pd.DataFrame()
    grouped = (
        frame.groupby(keys, dropna=False)
        .agg(
            folds=("fold", "nunique"),
            mean=(metric, "mean"),
            std=(metric, "std"),
            min=(metric, "min"),
            max=(metric, "max"),
        )
        .reset_index()
    )
    grouped["cv_instability"] = grouped["std"].fillna(0.0) / grouped["mean"].abs().clip(lower=1e-6)
    grouped["rank_metric"] = grouped["mean"] - 0.5 * grouped["std"].fillna(0.0) if higher_is_better else -grouped["mean"] - 0.5 * grouped["std"].fillna(0.0)
    return grouped.sort_values("rank_metric", ascending=False).reset_index(drop=True)


def semantic_diagnostics() -> tuple[pd.DataFrame, dict[str, object]]:
    two = safe_read(JEPA / "two_level_proto_jepa_folds.csv")
    proto = safe_read(JEPA / "jepa_semantic_prototype_search_folds.csv")

    rows: list[dict[str, object]] = []
    if not two.empty:
        keys = ["context_variant", "semantic_family", "semantic_k", "coarse_family", "coarse_k", "mode"]
        stab = fold_stability(two, keys, "pred_rate_r2", higher_is_better=True)
        for rec in stab.head(30).to_dict("records"):
            filt = np.ones(len(two), dtype=bool)
            for key in keys:
                filt &= two[key].astype(str).eq(str(rec[key])).to_numpy()
            sub = two.loc[filt]
            rows.append(
                {
                    "source": "two_level_proto",
                    **{k: rec[k] for k in keys},
                    "folds": int(rec["folds"]),
                    "pred_rate_r2_mean": float(rec["mean"]),
                    "pred_rate_r2_std": float(0.0 if pd.isna(rec["std"]) else rec["std"]),
                    "pred_rate_r2_min": float(rec["min"]),
                    "oracle_rate_r2_mean": float(sub["oracle_rate_r2"].mean()),
                    "semantic_acc_mean": float(sub["semantic_acc"].mean()),
                    "semantic_logloss_mean": float(sub["semantic_logloss"].mean()),
                    "stress_pass": bool((rec["mean"] > 0.02) and (rec["min"] > -0.10) and (sub["oracle_rate_r2"].mean() > 0.25)),
                }
            )

    if not proto.empty:
        keys = ["family", "k", "context_variant"]
        stab = fold_stability(proto, keys, "pred_rate_r2", higher_is_better=True)
        for rec in stab.head(30).to_dict("records"):
            filt = np.ones(len(proto), dtype=bool)
            for key in keys:
                filt &= proto[key].astype(str).eq(str(rec[key])).to_numpy()
            sub = proto.loc[filt]
            rows.append(
                {
                    "source": "semantic_proto",
                    "context_variant": rec["context_variant"],
                    "semantic_family": rec["family"],
                    "semantic_k": rec["k"],
                    "coarse_family": "none",
                    "coarse_k": 0,
                    "mode": "direct",
                    "folds": int(rec["folds"]),
                    "pred_rate_r2_mean": float(rec["mean"]),
                    "pred_rate_r2_std": float(0.0 if pd.isna(rec["std"]) else rec["std"]),
                    "pred_rate_r2_min": float(rec["min"]),
                    "oracle_rate_r2_mean": float(sub["oracle_rate_r2"].mean()),
                    "semantic_acc_mean": float(sub["proto_acc"].mean()),
                    "semantic_logloss_mean": float(sub["proto_logloss"].mean()),
                    "stress_pass": bool((rec["mean"] > 0.02) and (rec["min"] > -0.10) and (sub["oracle_rate_r2"].mean() > 0.30)),
                }
            )

    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.sort_values(
            ["stress_pass", "pred_rate_r2_mean", "oracle_rate_r2_mean"],
            ascending=[False, False, False],
        ).reset_index(drop=True)
        summary.to_csv(SEMANTIC_SUMMARY_OUT, index=False)

    facts = {
        "semantic_rows": int(len(summary)),
        "semantic_pass": int(summary["stress_pass"].sum()) if "stress_pass" in summary else 0,
        "best_pred_rate_r2": float(summary["pred_rate_r2_mean"].max()) if "pred_rate_r2_mean" in summary else np.nan,
        "best_oracle_rate_r2": float(summary["oracle_rate_r2_mean"].max()) if "oracle_rate_r2_mean" in summary else np.nan,
    }
    return summary, facts


def downstream_diagnostics() -> tuple[pd.DataFrame, dict[str, object]]:
    scans: list[pd.DataFrame] = []
    for path, source in [
        (JEPA / "transductive_episode_count_jepa_subject_chunk_scan.csv", "transductive_episode_count"),
        (JEPA / "mp_count_conditioning_jepa_geometry_scan.csv", "mp_count_conditioning"),
    ]:
        df = safe_read(path)
        if not df.empty:
            df = df.copy()
            df["source"] = source
            scans.append(df)
    if not scans:
        return pd.DataFrame(), {"downstream_rows": 0}
    all_scan = pd.concat(scans, ignore_index=True, sort=False)
    keys = [c for c in ["source", "cv_mode", "method", "group", "strength", "concentration", "base_mix", "scale"] if c in all_scan.columns]
    agg = (
        all_scan.groupby(keys, dropna=False)
        .agg(
            rows=("oof_delta_vs_stage2", "size"),
            mean_delta=("oof_delta_vs_stage2", "mean"),
            min_delta=("oof_delta_vs_stage2", "min"),
            max_delta=("oof_delta_vs_stage2", "max"),
            mean_oof=("oof_loss", "mean"),
        )
        .reset_index()
        .sort_values("mean_delta")
        .reset_index(drop=True)
    )
    if "cv_mode" in all_scan.columns:
        mode_best = all_scan.sort_values("oof_delta_vs_stage2").groupby(["source", "cv_mode"], as_index=False).head(1)
        mode_best.to_csv(ANALYSIS / "label_flow_blockrate_jepa_downstream_mode_best.csv", index=False)
    agg.to_csv(DOWNSTREAM_SUMMARY_OUT, index=False)
    facts = {
        "downstream_rows": int(len(all_scan)),
        "best_downstream_delta": float(all_scan["oof_delta_vs_stage2"].min()),
        "best_subject_chunk_delta": float(all_scan.loc[all_scan.get("cv_mode", "").astype(str).eq("subject_chunk"), "oof_delta_vs_stage2"].min())
        if "cv_mode" in all_scan.columns and all_scan.get("cv_mode", pd.Series(dtype=str)).astype(str).eq("subject_chunk").any()
        else np.nan,
        "best_geometry_delta": float(all_scan.loc[all_scan.get("cv_mode", "").astype(str).eq("geometry"), "oof_delta_vs_stage2"].min())
        if "cv_mode" in all_scan.columns and all_scan.get("cv_mode", pd.Series(dtype=str)).astype(str).eq("geometry").any()
        else np.nan,
    }
    return agg, facts


def candidate_pool() -> pd.DataFrame:
    files = sorted(JEPA.glob("submission_transductive_episode_count_jepa*.csv"))
    files += sorted(JEPA.glob("submission_mp_count_public_blend*.csv"))
    records: list[dict[str, object]] = []
    for path in files:
        source = "label_flow_submission"
        if "mp_count" in path.name:
            source = "mp_count_submission"
        records.append(
            {
                "resolved_path": str(path.resolve()),
                "source_path": rel_path(path),
                "basename": path.name,
                "pool_source": source,
                "pool_priority": 1.0,
                "candidate_family": family_name(path),
            }
        )
    return pd.DataFrame(records).drop_duplicates("resolved_path").reset_index(drop=True)


def pairwise_candidate_diagnostics() -> tuple[pd.DataFrame, dict[str, object]]:
    pool = candidate_pool()
    if pool.empty:
        return pd.DataFrame(), {"candidate_pool": 0}
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    known = known.sort_values("public_lb").reset_index(drop=True)
    model_df, _known_pairs = evaluate_pairwise_models(known)
    features = build_candidate_features(pool, sample, refs, ref_vecs)
    scored = score_candidates(known, features, model_df)
    scored.to_csv(PAIRWISE_OUT, index=False)
    shortlist = scored[
        scored["pair_submit_gate"].astype(bool)
        | scored["pair_control_better_than_a2c8_gate"].astype(bool)
        | scored["pair_probe_gate"].astype(bool)
    ].copy()
    if shortlist.empty:
        shortlist = scored.head(50).copy()
    shortlist.to_csv(PAIRWISE_SHORTLIST_OUT, index=False)
    facts = {
        "candidate_pool": int(len(pool)),
        "candidate_scored": int(len(scored)),
        "pair_submit_gate": int(scored["pair_submit_gate"].sum()),
        "pair_probe_gate": int(scored["pair_probe_gate"].sum()),
        "pair_control_better_than_a2c8_gate": int(scored["pair_control_better_than_a2c8_gate"].sum()),
        "best_pair_p90_vs_a2c8": float(scored["pair_delta_vs_a2c8_p90"].min()),
        "best_pair_beats_a2c8_rate": float(scored.sort_values("pair_delta_vs_a2c8_p90")["pair_beats_a2c8_rate"].iloc[0]),
    }
    return scored, facts


def markdown_table(df: pd.DataFrame, n: int, cols: list[str]) -> str:
    if df.empty:
        return "(empty)"
    keep = [c for c in cols if c in df.columns]
    return df[keep].head(n).round(9).to_csv(index=False).strip()


def main() -> None:
    semantic, semantic_facts = semantic_diagnostics()
    downstream, downstream_facts = downstream_diagnostics()
    scored, pair_facts = pairwise_candidate_diagnostics()

    label_flow_supported = (
        semantic_facts.get("best_oracle_rate_r2", -999) > 0.30
        and semantic_facts.get("best_pred_rate_r2", -999) > 0.0
    )
    submit_supported = pair_facts.get("pair_submit_gate", 0) > 0

    lines = [
        "# Label-Flow Block-Rate JEPA Stress",
        "",
        "Question: can label-flow/block-rate JEPA be treated as a semantic hidden-world representation, or is it another local-CV shortcut?",
        "",
        "## Falsifiable Hypothesis",
        "",
        "H15/H03 refinement: hidden blocks live on a low-dimensional label-rate manifold. A useful JEPA target should preserve block target-rate structure, be predictable from strict context without current-row leakage, improve downstream OOF under geometry and subject-chunk stress, and avoid public pairwise bad-axis gates.",
        "",
        "Success criteria:",
        "",
        "- semantic target preservation: oracle rate R2 > 0.30;",
        "- context predictability: pred rate R2 > 0 with fold-min not catastrophically negative;",
        "- downstream stress: subject-chunk and geometry branches both show non-trivial OOF gains;",
        "- public-risk stress: at least one candidate passes pair_submit_gate, or a probe passes without selector conflict.",
        "",
        "## Semantic Representation Stress",
        "",
        f"- semantic configs summarized: `{semantic_facts.get('semantic_rows', 0)}`",
        f"- semantic stress-pass configs: `{semantic_facts.get('semantic_pass', 0)}`",
        f"- best oracle_rate_r2: `{semantic_facts.get('best_oracle_rate_r2', np.nan):.6f}`",
        f"- best pred_rate_r2: `{semantic_facts.get('best_pred_rate_r2', np.nan):.6f}`",
        "",
        "```csv",
        markdown_table(
            semantic,
            20,
            [
                "source",
                "context_variant",
                "semantic_family",
                "semantic_k",
                "coarse_family",
                "coarse_k",
                "mode",
                "pred_rate_r2_mean",
                "pred_rate_r2_min",
                "oracle_rate_r2_mean",
                "semantic_acc_mean",
                "stress_pass",
            ],
        ),
        "```",
        "",
        "## Downstream OOF Stress",
        "",
        f"- downstream rows scanned: `{downstream_facts.get('downstream_rows', 0)}`",
        f"- best downstream delta vs stage2: `{downstream_facts.get('best_downstream_delta', np.nan):.6f}`",
        f"- best subject_chunk delta: `{downstream_facts.get('best_subject_chunk_delta', np.nan):.6f}`",
        f"- best geometry delta: `{downstream_facts.get('best_geometry_delta', np.nan):.6f}`",
        "",
        "```csv",
        markdown_table(
            downstream,
            20,
            [
                "source",
                "cv_mode",
                "method",
                "group",
                "strength",
                "concentration",
                "base_mix",
                "scale",
                "mean_delta",
                "min_delta",
                "max_delta",
            ],
        ),
        "```",
        "",
        "## Public Pairwise Candidate Stress",
        "",
        f"- candidate files scored: `{pair_facts.get('candidate_scored', 0)}` / pool `{pair_facts.get('candidate_pool', 0)}`",
        f"- pair_submit_gate: `{pair_facts.get('pair_submit_gate', 0)}`",
        f"- pair_control_better_than_a2c8_gate: `{pair_facts.get('pair_control_better_than_a2c8_gate', 0)}`",
        f"- pair_probe_gate: `{pair_facts.get('pair_probe_gate', 0)}`",
        f"- best p90 delta vs a2c8: `{pair_facts.get('best_pair_p90_vs_a2c8', np.nan):.9f}`",
        "",
        "```csv",
        markdown_table(
            scored,
            25,
            [
                "source_path",
                "candidate_family",
                "pool_source",
                "pair_delta_vs_a2c8_p90",
                "pair_delta_vs_a2c8_mean",
                "pair_beats_a2c8_rate",
                "pair_delta_vs_raw05_p90",
                "pair_beats_raw05_rate",
                "bad_axis_abs_load",
                "pair_submit_gate",
                "pair_probe_gate",
                "pair_selector_conflict",
                "pair_rank_score",
            ],
        ),
        "```",
        "",
        "## Decision",
        "",
        f"- label-flow semantic structure supported: `{bool(label_flow_supported)}`",
        f"- direct submit support from this branch: `{bool(submit_supported)}`",
        "",
    ]
    if label_flow_supported and not submit_supported:
        lines.extend(
            [
                "Interpretation: label-flow/block-rate is a real semantic representation, but current candidate translation still fails public-risk stress. Use it as latent energy/gate, not as direct probability replacement.",
                "",
                "Next experiment: build a gate that only applies block-rate corrections on samples where semantic confidence is high, raw05 distance is low, and target-dependency violation decreases.",
            ]
        )
    elif not label_flow_supported:
        lines.extend(
            [
                "Interpretation: the current label-flow target is not predictable enough under strict context. Do not build a submission from it; revise the target representation or context.",
            ]
        )
    else:
        lines.extend(
            [
                "Interpretation: at least one candidate passed public-risk stress. Promote the shortlist to submission survival review before any public submit.",
            ]
        )

    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SEMANTIC_SUMMARY_OUT.name}`",
            f"- `{DOWNSTREAM_SUMMARY_OUT.name}`",
            "- `label_flow_blockrate_jepa_downstream_mode_best.csv`",
            f"- `{PAIRWISE_OUT.name}`",
            f"- `{PAIRWISE_SHORTLIST_OUT.name}`",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT)
    print("\n[semantic]")
    print(markdown_table(semantic, 12, ["source", "context_variant", "semantic_family", "semantic_k", "coarse_family", "coarse_k", "mode", "pred_rate_r2_mean", "pred_rate_r2_min", "oracle_rate_r2_mean", "stress_pass"]))
    print("\n[pairwise]")
    print(markdown_table(scored, 12, ["source_path", "pair_delta_vs_a2c8_p90", "pair_beats_a2c8_rate", "bad_axis_abs_load", "pair_submit_gate", "pair_probe_gate", "pair_selector_conflict"]))


if __name__ == "__main__":
    main()
