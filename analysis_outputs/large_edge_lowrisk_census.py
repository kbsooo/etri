from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

A2C8_LB = 0.5774393210
RAW05_LB = 0.5775263072
RAW05_GAP = RAW05_LB - A2C8_LB

CORE_TABLES = [
    "public_pairwise_order_selector_candidates.csv",
    "public_pairwise_order_selector_shortlist.csv",
    "selector_support_topology_audit.csv",
    "block_measurement_selector_rescore.csv",
    "block_measurement_selector_rescore_shortlist.csv",
    "direction_probe_selector_reconciliation.csv",
    "focused_label_flow_survival_review.csv",
    "hidden_public_local_bridge_shortlist.csv",
    "hidden_public_localization_candidate_ranking.csv",
    "inverse7_raw_anchor_bridge_scale_scan_scores.csv",
    "jepa_selector_frontier_audit_candidates.csv",
    "label_flow_blockrate_jepa_pairwise_scored.csv",
    "label_flow_combo_focused_submit_pairwise_scored.csv",
    "label_flow_combo_gate_pairwise_scored.csv",
    "label_flow_gated_candidate_pairwise_scored.csv",
    "label_flow_gated_candidate_shortlist.csv",
    "label_flow_localized_sensor_audit.csv",
    "label_flow_localized_sensor_audit_shortlist.csv",
    "label_flow_sensor_scale_curve.csv",
    "label_flow_sensor_scale_curve_shortlist.csv",
    "label_flow_targetwise_amplified_gate_pairwise_scored.csv",
    "old_positive_anchor_pairwise_rescore.csv",
    "old_positive_anchor_pairwise_rescore_shortlist.csv",
    "public_lb_inverse8_selected_stress_audit.csv",
    "public_probe_independent_evidence_audit_summary.csv",
    "public_selector_universe_audit_candidates.csv",
    "s4q3_oof_anchor_audit.csv",
    "s4q3_oof_top_selector_rescore.csv",
    "selector_disambiguation_sensor_candidates.csv",
    "worldview_sensor_discriminability_audit.csv",
]

FILE_COLS = ["file", "file_selector", "source_path", "basename", "role"]
FAMILY_COLS = [
    "candidate_family",
    "family",
    "lane",
    "role",
    "support_source",
    "source_group",
    "sensor_tag",
    "candidate_bucket",
    "source_table",
]
NUMERIC_ALIASES = {
    "pair_p90": [
        "pair_delta_vs_a2c8_p90",
        "pair_p90_delta",
        "selector_p90_delta_vs_a2c8_public",
    ],
    "pair_mean": [
        "pair_delta_vs_a2c8_mean",
        "selector_delta_vs_a2c8_public",
        "pair_delta_vs_a2c8_median",
    ],
    "old_p90": ["old_p90_delta", "old_selector_p90_delta_vs_a2c8", "best_old_p90"],
    "old_rate": ["old_better_rate", "old_selector_beats_a2c8_rate"],
    "raw_mean": ["raw_mean_delta"],
    "raw_worst": ["raw_worst_delta"],
    "anchor_low_half_max": [
        "anchor_low_half_max_delta",
        "anchor_low_anchor_energy_half_max_delta",
        "low_half_max_delta",
    ],
    "anchor_low_half_median": [
        "anchor_low_half_median_delta",
        "anchor_low_anchor_energy_half_median_delta",
        "low_half_median_delta",
    ],
    "honest_cv_mean": ["honest_cv_mean_delta"],
    "honest_cv_worst": ["honest_cv_worst_delta"],
    "mean_abs_move": [
        "mean_abs_move_vs_a2c8",
        "mean_abs_prob_move_vs_a2c8",
        "mean_abs_move_vs_a2c8_prob",
    ],
    "mean_abs_move_vs_raw05": [
        "mean_abs_move_vs_raw05",
        "mean_abs_move_vs_raw05_prob",
    ],
    "bad_axis": ["bad_axis_abs_load", "bad_axis_abs_load_geom"],
    "raw05_compat": ["raw05_a2c8_compat_energy", "raw05_a2c8_compat_energy_geom"],
    "q3s4_move_share": ["q3s4_move_share", "q3_s4_move_share"],
    "pair_beats_rate": ["pair_beats_a2c8_rate", "pair_better_rate"],
    "selector_beats_rate": ["beats_a2c8_scenario_rate"],
}
BOOL_COLS = [
    "pair_submit_gate",
    "pair_probe_gate",
    "pair_control_better_than_a2c8_gate",
    "pair_p90_negative",
    "pair_majority",
    "old_majority",
    "two_selector_majority",
    "resolved_better_than_a2c8_gate",
    "normal_submit_gate",
    "strict_large_safe",
    "large_lowbad_movement",
    "selector_hard_veto",
    "low_public_bad_axis",
    "low_bad_axis",
    "low_bad_axis_for_label_flow",
    "raw05_novel_movement",
    "raw_support_gate",
    "anchor_low_half_gate",
    "anchor_low_quarter_gate",
    "bridge_gate",
    "e35_normal_submit_gate",
]


def read_best_selector_error() -> float:
    path = OUT / "selector_resolution_boundary_audit_selectors.csv"
    if not path.exists():
        return 0.000218288
    df = pd.read_csv(path)
    vals = pd.to_numeric(df.get("best_error"), errors="coerce").dropna()
    return float(vals.min()) if len(vals) else 0.000218288


def first_existing(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    out = pd.Series(np.nan, index=df.index, dtype="object")
    for col in cols:
        if col not in df.columns:
            continue
        mask = out.isna()
        vals = df[col]
        out.loc[mask] = vals.loc[mask]
    return out


def first_numeric(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    out = pd.Series(np.nan, index=df.index, dtype="float64")
    for col in cols:
        if col not in df.columns:
            continue
        mask = out.isna()
        vals = pd.to_numeric(df[col], errors="coerce")
        out.loc[mask] = vals.loc[mask]
    return out


def to_bool_series(s: pd.Series) -> pd.Series:
    if s.empty:
        return pd.Series(dtype="bool")
    if s.dtype == bool:
        return s.fillna(False)
    text = s.astype(str).str.strip().str.lower()
    return text.isin(["true", "1", "1.0", "yes", "y", "t"])


def any_bool(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    out = pd.Series(False, index=df.index)
    for col in cols:
        if col in df.columns:
            out = out | to_bool_series(df[col])
    return out


def canonical_file(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if text.startswith("analysis_outputs/"):
        text = text[len("analysis_outputs/") :]
    return text


def load_table(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        return pd.DataFrame()
    header = pd.read_csv(path, nrows=0)
    available = set(header.columns)
    requested: set[str] = set(FILE_COLS + FAMILY_COLS + BOOL_COLS + ["is_known_public", "known_public_lb"])
    for cols in NUMERIC_ALIASES.values():
        requested.update(cols)
    usecols = [c for c in header.columns if c in requested and c in available]
    if not usecols:
        return pd.DataFrame()
    df = pd.read_csv(path, usecols=usecols, low_memory=False)
    if df.empty:
        return pd.DataFrame()
    out = pd.DataFrame(index=df.index)
    out["source_table"] = name
    out["file"] = first_existing(df, FILE_COLS).map(canonical_file)
    out["family"] = first_existing(df, FAMILY_COLS).astype(str)
    for key, cols in NUMERIC_ALIASES.items():
        out[key] = first_numeric(df, cols)
    for col in BOOL_COLS:
        out[col] = to_bool_series(df[col]) if col in df.columns else False
    out["known_public"] = to_bool_series(df["is_known_public"]) if "is_known_public" in df.columns else False
    out["known_public_lb"] = (
        pd.to_numeric(df["known_public_lb"], errors="coerce")
        if "known_public_lb" in df.columns
        else np.nan
    )
    out = out[out["file"].astype(str).str.len() > 0].copy()
    return out


def classify_edges(df: pd.DataFrame, selector_error: float) -> pd.DataFrame:
    out = df.copy()
    out["pair_edge"] = -out["pair_p90"]
    out["old_edge"] = -out["old_p90"]
    out["raw_edge"] = -out["raw_mean"]
    out["anchor_low_half_edge"] = -out["anchor_low_half_max"]
    edge_cols = ["pair_edge", "old_edge", "raw_edge", "anchor_low_half_edge"]
    out["best_observed_edge"] = out[edge_cols].max(axis=1, skipna=True)
    all_edge_missing = out[edge_cols].isna().all(axis=1)
    edge_argmax = out[edge_cols].fillna(-np.inf).idxmax(axis=1)
    out["best_edge_source"] = edge_argmax.str.replace("_edge", "", regex=False)
    out.loc[all_edge_missing, "best_edge_source"] = "missing"

    out["pair_negative"] = out["pair_p90"].lt(0) | out["pair_p90_negative"]
    out["pair_edge_gt_raw05_gap"] = out["pair_edge"].gt(RAW05_GAP)
    out["pair_edge_gt_selector_error"] = out["pair_edge"].gt(selector_error)
    out["old_edge_gt_selector_error"] = out["old_edge"].gt(selector_error)
    out["raw_edge_gt_selector_error"] = out["raw_edge"].gt(selector_error)
    out["anchor_edge_gt_selector_error"] = out["anchor_low_half_edge"].gt(selector_error)
    out["any_edge_gt_selector_error"] = out[
        [
            "pair_edge_gt_selector_error",
            "old_edge_gt_selector_error",
            "raw_edge_gt_selector_error",
            "anchor_edge_gt_selector_error",
        ]
    ].any(axis=1)

    out["observed_low_bad_flag"] = any_bool(
        out, ["low_public_bad_axis", "low_bad_axis", "low_bad_axis_for_label_flow"]
    )
    out["low_bad_axis_gate"] = out["observed_low_bad_flag"] | out["bad_axis"].le(0.03)
    out["medium_bad_axis_gate"] = out["bad_axis"].le(0.07)
    out["raw05_compatible_gate"] = out["raw05_compat"].le(0.01)
    out["not_hard_veto"] = ~out["selector_hard_veto"]
    out["two_selector_support"] = out["two_selector_majority"] | (
        out["pair_majority"] & out["old_majority"]
    )
    out["any_submit_like_support"] = (
        out["pair_submit_gate"]
        | out["pair_control_better_than_a2c8_gate"]
        | out["resolved_better_than_a2c8_gate"]
        | out["normal_submit_gate"]
        | out["strict_large_safe"]
        | out["bridge_gate"]
    )
    out["large_pair_lowbad_gate"] = out["pair_edge_gt_selector_error"] & out["low_bad_axis_gate"]
    out["large_pair_two_selector_gate"] = (
        out["pair_edge_gt_selector_error"] & out["two_selector_support"]
    )
    out["normal_large_safe_gate"] = (
        out["pair_edge_gt_selector_error"]
        & out["low_bad_axis_gate"]
        & out["raw05_compatible_gate"]
        & out["not_hard_veto"]
        & (out["two_selector_support"] | out["any_submit_like_support"])
    )
    out["diagnostic_large_conflict_gate"] = (
        out["any_edge_gt_selector_error"] & ~out["normal_large_safe_gate"]
    )
    out["edge_over_selector_error"] = out["best_observed_edge"] / selector_error
    out["pair_edge_over_selector_error"] = out["pair_edge"] / selector_error
    out["pair_edge_over_raw05_gap"] = out["pair_edge"] / RAW05_GAP
    return out


def aggregate_by_file(rows: pd.DataFrame, selector_error: float) -> pd.DataFrame:
    bool_cols = [
        c
        for c in rows.columns
        if rows[c].dtype == bool or c.endswith("_gate") or c.endswith("_support")
    ]
    numeric_min_cols = ["pair_p90", "old_p90", "raw_mean", "anchor_low_half_max", "bad_axis", "raw05_compat"]
    numeric_max_cols = [
        "mean_abs_move",
        "pair_edge",
        "old_edge",
        "raw_edge",
        "anchor_low_half_edge",
        "best_observed_edge",
        "edge_over_selector_error",
        "pair_edge_over_selector_error",
        "pair_edge_over_raw05_gap",
        "pair_beats_rate",
        "selector_beats_rate",
    ]
    gb = rows.groupby("file", sort=False, dropna=False)
    out = pd.DataFrame({"file": gb.size().index})
    out["row_count"] = gb.size().to_numpy()
    out["source_count"] = gb["source_table"].nunique().to_numpy()
    out["sources"] = gb["source_table"].agg(
        lambda s: ",".join(sorted(set(s.dropna().astype(str))))
    ).to_numpy()
    out["family"] = gb["family"].first().to_numpy()
    out["known_public"] = gb["known_public"].any().to_numpy()
    out["known_public_lb"] = gb["known_public_lb"].min().to_numpy()
    for col in numeric_min_cols:
        out[f"best_min_{col}"] = gb[col].min().to_numpy()
    for col in numeric_max_cols:
        out[f"best_max_{col}"] = gb[col].max().to_numpy()
    for col in bool_cols:
        out[col] = gb[col].any().to_numpy()
    if out.empty:
        return out
    out["normal_large_safe_gate"] = out["normal_large_safe_gate"].fillna(False).astype(bool)
    out["large_pair_lowbad_gate"] = out["large_pair_lowbad_gate"].fillna(False).astype(bool)
    out["large_pair_two_selector_gate"] = out["large_pair_two_selector_gate"].fillna(False).astype(bool)
    out["pair_edge_gt_selector_error"] = out["pair_edge_gt_selector_error"].fillna(False).astype(bool)
    out["pair_edge_gt_raw05_gap"] = out["pair_edge_gt_raw05_gap"].fillna(False).astype(bool)
    out["pair_negative"] = out["pair_negative"].fillna(False).astype(bool)
    out["any_edge_gt_selector_error"] = out["any_edge_gt_selector_error"].fillna(False).astype(bool)
    out["edge_margin_after_selector"] = out["best_max_pair_edge"] - selector_error
    out = out.sort_values(
        [
            "normal_large_safe_gate",
            "large_pair_lowbad_gate",
            "pair_edge_gt_selector_error",
            "best_max_pair_edge",
            "best_max_best_observed_edge",
        ],
        ascending=[False, False, False, False, False],
    )
    return out


def markdown_table(df: pd.DataFrame, cols: list[str], n: int = 12) -> str:
    if df.empty:
        return "_none_"
    sub = df.loc[:, [c for c in cols if c in df.columns]].head(n).copy()
    if sub.empty:
        return "_none_"

    def fmt(x: object) -> str:
        if isinstance(x, (float, np.floating)):
            if np.isnan(x):
                return ""
            if abs(float(x)) < 0.01:
                return f"{float(x):.9f}"
            return f"{float(x):.6f}"
        text = str(x)
        return text.replace("|", "\\|")

    headers = list(sub.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in sub.iterrows():
        lines.append("| " + " | ".join(fmt(row[c]) for c in headers) + " |")
    return "\n".join(lines)


def build_report(rows: pd.DataFrame, by_file: pd.DataFrame, summary: pd.DataFrame, selector_error: float) -> str:
    source_summary = (
        rows.groupby("source_table")
        .agg(
            rows=("file", "size"),
            unique_files=("file", "nunique"),
            pair_negative=("pair_negative", "sum"),
            pair_edge_gt_raw05_gap=("pair_edge_gt_raw05_gap", "sum"),
            pair_edge_gt_selector_error=("pair_edge_gt_selector_error", "sum"),
            normal_large_safe=("normal_large_safe_gate", "sum"),
            any_edge_gt_selector_error=("any_edge_gt_selector_error", "sum"),
        )
        .reset_index()
        .sort_values(["normal_large_safe", "pair_edge_gt_selector_error", "any_edge_gt_selector_error"], ascending=False)
    )
    top_pair = by_file[by_file["pair_negative"]].sort_values("best_max_pair_edge", ascending=False)
    top_any = by_file[by_file["any_edge_gt_selector_error"]].sort_values(
        "best_max_best_observed_edge", ascending=False
    )
    top_safe = by_file[by_file["normal_large_safe_gate"]].copy()
    lines = [
        "# E44 Large-Edge Low-Risk Census",
        "",
        "## Observe",
        "",
        "E43 showed that near-frontier candidate edges are smaller than selector error. The remaining cheap falsification is whether the existing scored universe already contains a larger sign-consistent movement that current selectors overlooked.",
        "",
        "## Wonder",
        "",
        "Do we have any candidate whose favorable edge is large enough to beat the best selector error while also passing low-bad-axis/raw05/two-selector stress?",
        "",
        "## Hypothesis",
        "",
        "H43: if the plateau is mostly a candidate-selection failure rather than a representation/selector-resolution failure, at least one existing scored candidate should have a pairwise public-order edge larger than the current best selector error and survive low-risk gates.",
        "",
        "## Method",
        "",
        f"- Raw05-A2C8 public gap: `{RAW05_GAP:.10f}`.",
        f"- Best current selector error from E43: `{selector_error:.9f}`.",
        f"- Scored tables loaded: `{summary.loc[0, 'loaded_tables']}`.",
        f"- Normal large-safe gate: pair p90 edge greater than selector error, low bad-axis, raw05-compatible, no hard veto, and either two-selector or submit-like support.",
        "",
        "## Result",
        "",
        markdown_table(summary, list(summary.columns), n=20),
        "",
        "## Source Breakdown",
        "",
        markdown_table(
            source_summary,
            [
                "source_table",
                "rows",
                "unique_files",
                "pair_negative",
                "pair_edge_gt_raw05_gap",
                "pair_edge_gt_selector_error",
                "normal_large_safe",
                "any_edge_gt_selector_error",
            ],
            n=30,
        ),
        "",
        "## Top Pair-Favorable Rows",
        "",
        markdown_table(
            top_pair,
            [
                "file",
                "family",
                "best_min_pair_p90",
                "best_max_pair_edge",
                "best_max_pair_edge_over_selector_error",
                "best_max_pair_edge_over_raw05_gap",
                "large_pair_lowbad_gate",
                "large_pair_two_selector_gate",
                "normal_large_safe_gate",
                "source_count",
            ],
            n=20,
        ),
        "",
        "## Top Any-Edge Conflict Rows",
        "",
        markdown_table(
            top_any,
            [
                "file",
                "family",
                "best_min_pair_p90",
                "best_min_old_p90",
                "best_min_raw_mean",
                "best_min_anchor_low_half_max",
                "best_max_best_observed_edge",
                "best_max_edge_over_selector_error",
                "normal_large_safe_gate",
                "diagnostic_large_conflict_gate",
                "source_count",
            ],
            n=20,
        ),
        "",
        "## Normal Large-Safe Candidates",
        "",
        markdown_table(
            top_safe,
            [
                "file",
                "family",
                "best_min_pair_p90",
                "best_max_pair_edge",
                "best_min_bad_axis",
                "best_min_raw05_compat",
                "two_selector_support",
                "any_submit_like_support",
                "source_count",
            ],
            n=20,
        ),
        "",
        "## Decision",
        "",
    ]
    normal_safe = int(summary.loc[0, "normal_large_safe_files"])
    pair_large = int(summary.loc[0, "pair_edge_gt_selector_error_files"])
    any_large = int(summary.loc[0, "any_edge_gt_selector_error_files"])
    if normal_safe:
        lines.append(
            "At least one existing candidate has a selector-error-scale pair edge and passes the low-risk gate. These rows need file-level inspection before any submission because this census only normalizes existing stress signals."
        )
    elif pair_large:
        lines.append(
            "Some candidates have selector-error-scale pair edges, but none pass the combined low-risk gate. Treat them as conflict sensors, not normal submissions."
        )
    elif any_large:
        lines.append(
            "No candidate has a selector-error-scale pairwise public-order edge. Large favorable signals exist only in raw/anchor/honest-CV views and are exactly the worldview conflict already diagnosed in E38-E43."
        )
    else:
        lines.append(
            "No existing scored candidate has any favorable edge above the best selector error. This would strengthen the representation-move bottleneck."
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- `analysis_outputs/large_edge_lowrisk_census_rows.csv`",
            "- `analysis_outputs/large_edge_lowrisk_census_by_file.csv`",
            "- `analysis_outputs/large_edge_lowrisk_census_summary.csv`",
            "- `analysis_outputs/large_edge_lowrisk_census_report.md`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    selector_error = read_best_selector_error()
    frames = []
    loaded = []
    for table in CORE_TABLES:
        df = load_table(table)
        if df.empty:
            continue
        frames.append(df)
        loaded.append(table)
    if not frames:
        raise RuntimeError("No candidate tables loaded")
    rows = pd.concat(frames, ignore_index=True)
    rows = classify_edges(rows, selector_error)
    by_file = aggregate_by_file(rows, selector_error)
    summary = pd.DataFrame(
        [
            {
                "loaded_tables": len(loaded),
                "row_count": len(rows),
                "unique_files": by_file["file"].nunique(),
                "pair_negative_rows": int(rows["pair_negative"].sum()),
                "pair_negative_files": int(by_file["pair_negative"].sum()),
                "pair_edge_gt_raw05_gap_rows": int(rows["pair_edge_gt_raw05_gap"].sum()),
                "pair_edge_gt_raw05_gap_files": int(by_file["pair_edge_gt_raw05_gap"].sum()),
                "pair_edge_gt_selector_error_rows": int(rows["pair_edge_gt_selector_error"].sum()),
                "pair_edge_gt_selector_error_files": int(by_file["pair_edge_gt_selector_error"].sum()),
                "large_pair_lowbad_rows": int(rows["large_pair_lowbad_gate"].sum()),
                "large_pair_lowbad_files": int(by_file["large_pair_lowbad_gate"].sum()),
                "large_pair_two_selector_rows": int(rows["large_pair_two_selector_gate"].sum()),
                "large_pair_two_selector_files": int(by_file["large_pair_two_selector_gate"].sum()),
                "normal_large_safe_rows": int(rows["normal_large_safe_gate"].sum()),
                "normal_large_safe_files": int(by_file["normal_large_safe_gate"].sum()),
                "any_edge_gt_selector_error_rows": int(rows["any_edge_gt_selector_error"].sum()),
                "any_edge_gt_selector_error_files": int(by_file["any_edge_gt_selector_error"].sum()),
                "best_pair_edge": float(pd.to_numeric(rows["pair_edge"], errors="coerce").max()),
                "best_pair_edge_over_selector_error": float(
                    pd.to_numeric(rows["pair_edge_over_selector_error"], errors="coerce").max()
                ),
                "best_pair_edge_over_raw05_gap": float(
                    pd.to_numeric(rows["pair_edge_over_raw05_gap"], errors="coerce").max()
                ),
                "best_any_edge": float(pd.to_numeric(rows["best_observed_edge"], errors="coerce").max()),
                "best_any_edge_over_selector_error": float(
                    pd.to_numeric(rows["edge_over_selector_error"], errors="coerce").max()
                ),
            }
        ]
    )
    rows.to_csv(OUT / "large_edge_lowrisk_census_rows.csv", index=False)
    by_file.to_csv(OUT / "large_edge_lowrisk_census_by_file.csv", index=False)
    summary.to_csv(OUT / "large_edge_lowrisk_census_summary.csv", index=False)
    (OUT / "large_edge_lowrisk_census_report.md").write_text(
        build_report(rows, by_file, summary, selector_error), encoding="utf-8"
    )
    print(summary.to_string(index=False))
    print(f"loaded={len(loaded)} tables")
    print("top pair favorable:")
    cols = ["file", "family", "best_min_pair_p90", "best_max_pair_edge", "normal_large_safe_gate"]
    print(by_file[by_file["pair_negative"]][cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
