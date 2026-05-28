from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import A2C8, TARGETS, feature_row, load_sub  # noqa: E402
from public_pairwise_order_selector import evaluate_pairwise_models, score_candidates  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


DETAIL_OUT = OUT / "direction_probe_selector_reconciliation.csv"
SUMMARY_OUT = OUT / "direction_probe_selector_reconciliation_by_family.csv"
REPORT_OUT = OUT / "direction_probe_selector_reconciliation_report.md"


CANDIDATES = [
    ("mixmin", "rank1", "submission_mixmin_0c916bb4.csv"),
    ("mixmin", "rank2", "submission_mixmin_5a4c25e0.csv"),
    ("mixmin", "rank3", "submission_mixmin_f0d12643.csv"),
    ("mixmin", "frontier1", "submission_mixmin_f6c04249.csv"),
    ("mixmin", "frontier2", "submission_mixmin_ef4b1c19.csv"),
    ("mixmin", "frontier3", "submission_mixmin_7f9cb635.csv"),
    ("mixmin", "frontier4", "submission_mixmin_615da9a7.csv"),
    ("direns", "combo_best", "submission_direns_c4af1fd8.csv"),
    ("direns", "anchor_best", "submission_direns_2a96ae73.csv"),
    ("direns", "secondary", "submission_direns_c0fdb76b.csv"),
    ("direns", "sibling", "submission_direns_1e0f159d.csv"),
    ("direns", "orth_diag", "submission_direns_b0962ff8.csv"),
    ("sparseladder", "balanced", "submission_sparseladder_b01acaa1.csv"),
    ("sparseladder", "max_scale", "submission_sparseladder_89817541.csv"),
    ("sparseladder", "no_q2", "submission_sparseladder_f1ee16b0.csv"),
    ("blockorth", "best", "submission_blockorth_3a28f87f.csv"),
    ("blockorth", "prefix", "submission_blockorth_0352b65f.csv"),
    ("targetabl", "q3_stage", "submission_targetabl_b19056bb.csv"),
    ("targetabl", "q3_s234", "submission_targetabl_1049b8e7.csv"),
    ("inverse7blend", "best", "submission_inverse7blend_1040423d.csv"),
    ("inv7gate", "prefix_best", "submission_inv7gate_e35a7114.csv"),
    ("inv7gate", "sibling", "submission_inv7gate_0a9c0c66.csv"),
]


META_FILES = [
    OUT / "jepa_direction_mixture_minimax_optimizer_selected.csv",
    OUT / "jepa_sparse_direction_ensemble_orthogonalizer_selected.csv",
    OUT / "jepa_target_ablation_scale_probe_selected.csv",
    OUT / "jepa_blockwise_bad_axis_decomposition_selected.csv",
    OUT / "jepa_inverse7_gated_sparse_scale_selected.csv",
]


def collect_metadata() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    useful = [
        "file",
        "name",
        "submit_role",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "combo_weighted_delta_vs_b01_ladder",
        "combo_weighted_win_vs_b01_ladder",
        "combo_p90_delta_vs_b01_ladder",
        "combo_worst_delta_vs_b01_ladder",
        "combo_weighted_delta_vs_direns_c4af",
        "mean_abs_move_vs_a2c8",
        "source_name",
        "source_weights",
        "variant",
        "target_group",
        "row_gate",
        "cell_gate",
        "projection",
        "axis_group",
        "anti_lambda",
        "scale",
    ]
    for path in META_FILES:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        cols = [col for col in useful if col in df.columns]
        part = df[cols].copy()
        part["meta_source"] = path.name
        frames.append(part)
    if not frames:
        return pd.DataFrame(columns=["file"])
    meta = pd.concat(frames, ignore_index=True, sort=False)
    meta = meta.drop_duplicates("file", keep="first")
    return meta


def build_candidate_features(sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for family, role, name in CANDIDATES:
        path = OUT / name
        if not path.exists():
            continue
        row = feature_row(path, sample, refs, ref_vecs)
        row.update(
            {
                "source_path": str(path.relative_to(ROOT)),
                "file": str(path.relative_to(ROOT)),
                "basename": name,
                "probe_family": family,
                "probe_role": role,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def add_flags(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    move_cols = [f"move_abs_a2c8_{target}" for target in TARGETS]
    out["dominant_target"] = out[move_cols].idxmax(axis=1).str.replace("move_abs_a2c8_", "", regex=False)
    out["q3s4_move_share"] = (
        out["move_abs_a2c8_Q3"] + out["move_abs_a2c8_S4"]
    ) / (out[move_cols].sum(axis=1) + 1e-12)
    out["stage_move_share"] = (
        out["move_abs_a2c8_S1"]
        + out["move_abs_a2c8_S2"]
        + out["move_abs_a2c8_S3"]
        + out["move_abs_a2c8_S4"]
    ) / (out[move_cols].sum(axis=1) + 1e-12)
    out["old_majority"] = out["beats_a2c8_scenario_rate"].fillna(0.0) >= 0.50
    out["pair_majority"] = out["pair_beats_a2c8_rate"].fillna(0.0) >= 0.70
    out["pair_p90_negative"] = out["pair_delta_vs_a2c8_p90"] < 0.0
    out["two_selector_majority"] = out["old_majority"] & out["pair_majority"]
    out["submit_shape"] = (
        out["pair_p90_negative"]
        & out["pair_majority"]
        & out["old_majority"]
        & (out["bad_axis_abs_load"].fillna(1.0) <= 0.075)
        & (out["mean_abs_move_vs_a2c8"].fillna(0.0) >= 0.002)
    )
    out["reconciliation_rank"] = (
        out["pair_delta_vs_a2c8_p90"].fillna(0.001)
        + 0.20 * out["selector_p90_delta_vs_a2c8_public"].fillna(0.001)
        + 0.00020 * out["bad_axis_abs_load"].fillna(0.0)
        - 0.00008 * out["pair_beats_a2c8_rate"].fillna(0.0)
        - 0.00008 * out["beats_a2c8_scenario_rate"].fillna(0.0)
    )
    return out.sort_values(
        ["submit_shape", "two_selector_majority", "reconciliation_rank"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def score_probes(features: pd.DataFrame, known: pd.DataFrame) -> pd.DataFrame:
    old_scored = candidate_stress_scores(known, features)
    old_cols = [
        "file",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
    ]
    old_scored = old_scored[[col for col in old_cols if col in old_scored.columns]].copy()
    merged = features.merge(old_scored, on="file", how="left")
    model_df, _ = evaluate_pairwise_models(known)
    pair_scored = score_candidates(known, merged, model_df)
    scored = pair_scored[pair_scored["probe_family"].notna()].copy()
    return add_flags(scored)


def summarize(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for family, group in scored.groupby("probe_family", sort=True):
        best = group.sort_values("reconciliation_rank").iloc[0]
        rows.append(
            {
                "probe_family": family,
                "n": int(len(group)),
                "pair_p90_negative": int(group["pair_p90_negative"].sum()),
                "pair_majority": int(group["pair_majority"].sum()),
                "old_majority": int(group["old_majority"].sum()),
                "two_selector_majority": int(group["two_selector_majority"].sum()),
                "submit_shape": int(group["submit_shape"].sum()),
                "best_file": best["source_path"],
                "best_pair_p90": float(best["pair_delta_vs_a2c8_p90"]),
                "best_pair_rate": float(best["pair_beats_a2c8_rate"]),
                "best_old_p90": float(best["selector_p90_delta_vs_a2c8_public"]),
                "best_old_rate": float(best["beats_a2c8_scenario_rate"]),
                "best_bad_axis": float(best["bad_axis_abs_load"]),
                "best_move": float(best["mean_abs_move_vs_a2c8"]),
                "best_q3s4_share": float(best["q3s4_move_share"]),
                "best_stage_share": float(best["stage_move_share"]),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["submit_shape", "two_selector_majority", "best_pair_p90", "best_old_p90"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


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


def write_report(scored: pd.DataFrame, summary: pd.DataFrame) -> None:
    view_cols = [
        "source_path",
        "probe_family",
        "probe_role",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "q3s4_move_share",
        "stage_move_share",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "combo_weighted_delta_vs_b01_ladder",
        "combo_p90_delta_vs_b01_ladder",
        "old_majority",
        "pair_majority",
        "two_selector_majority",
        "submit_shape",
    ]
    top = scored.sort_values("reconciliation_rank").head(20)
    lines = [
        "# Direction Probe Selector Reconciliation",
        "",
        "Question: do the newer score-oriented sparse/target-ablation/direction-ensemble/minimax probes survive the same pairwise-vs-old selector stress used to reject S4/Q3 label-flow sensors?",
        "",
        "## Summary",
        "",
        f"- probes scored: `{len(scored)}`.",
        f"- pair p90 negative: `{int(scored['pair_p90_negative'].sum())}`.",
        f"- pair majority: `{int(scored['pair_majority'].sum())}`.",
        f"- old majority: `{int(scored['old_majority'].sum())}`.",
        f"- two-selector majority: `{int(scored['two_selector_majority'].sum())}`.",
        f"- submit-shape candidates: `{int(scored['submit_shape'].sum())}`.",
        "",
        "## By Family",
        "",
        markdown_table(summary),
        "",
        "## Top Reconciliation Rows",
        "",
        markdown_table(top[[col for col in view_cols if col in top.columns]]),
        "",
        "## Decision",
        "",
    ]
    if int(scored["submit_shape"].sum()) == 0:
        lines.extend(
            [
                "- No newer score-oriented probe becomes submit-safe under the old+pairwise combined gate.",
                "- The minimax/direns family is still more public-actionable than the S4/Q3 label-flow sensor because it carries much larger movement and strong combo/honest-CV evidence, but it is not validated by the old hidden-subset selector.",
                "- Treat the current mixmin/direns files as score-oriented public probes, not as evidence that the 0.54 bottleneck is solved.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one newer direction probe reached two-selector submit shape. Inspect target movement and anchor metadata before promotion.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8)
    known, refs, ref_vecs = build_known_and_refs(sample)
    features = build_candidate_features(sample, refs, ref_vecs)
    meta = collect_metadata()
    if not meta.empty:
        features = features.merge(meta, left_on="basename", right_on="file", how="left", suffixes=("", "_meta"))
        if "file_meta" in features.columns:
            features = features.drop(columns=["file_meta"])
    scored = score_probes(features, known)
    summary = summarize(scored)
    scored.to_csv(DETAIL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scored, summary)

    print(REPORT_OUT)
    print(
        {
            "n": len(scored),
            "pair_p90_negative": int(scored["pair_p90_negative"].sum()),
            "pair_majority": int(scored["pair_majority"].sum()),
            "old_majority": int(scored["old_majority"].sum()),
            "two_selector_majority": int(scored["two_selector_majority"].sum()),
            "submit_shape": int(scored["submit_shape"].sum()),
        }
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
