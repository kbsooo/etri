from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

A2C8_LB = 0.5774393210
RAW05_LB = 0.5775263072
RAW05_GAP = RAW05_LB - A2C8_LB


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(OUT / path)


def safe_min(series: pd.Series) -> float:
    vals = pd.to_numeric(series, errors="coerce").dropna()
    return float(vals.min()) if len(vals) else np.nan


def safe_median(series: pd.Series) -> float:
    vals = pd.to_numeric(series, errors="coerce").dropna()
    return float(vals.median()) if len(vals) else np.nan


def ratio(edge: float, err: float) -> float:
    if not np.isfinite(err) or err <= 0:
        return np.nan
    return float(edge / err)


def selector_resolution_table() -> pd.DataFrame:
    rows: list[dict] = []

    pair = read_csv("public_pairwise_order_selector_models.csv")
    rows.append(
        {
            "selector": "pairwise_public_order_models",
            "source": "public_pairwise_order_selector_models.csv",
            "n_views": len(pair),
            "best_error": safe_min(pair["loo_mae"]),
            "median_error": safe_median(pair["loo_mae"]),
            "best_p90_error": safe_min(pair["loo_p90_abs_error"]),
            "best_l2o_error": safe_min(pair["l2o_mae"]),
            "rank_or_sign_strength": safe_median(pair["known_rank_accuracy_vs_a2c8"]),
            "gate_count": int(pair["order_pass"].fillna(False).astype(bool).sum()),
            "error_type": "LOO/L2O over known public pairwise order models",
        }
    )

    rel = read_csv("selector_disambiguation_reliability.csv")
    for _, r in rel.iterrows():
        rows.append(
            {
                "selector": str(r["selector"]),
                "source": "selector_disambiguation_reliability.csv",
                "n_views": int(r["models"]),
                "best_error": float(r["best_loo_mae"]),
                "median_error": float(r["median_loo_mae"]),
                "best_p90_error": np.nan,
                "best_l2o_error": float(r["best_l2o_mae"]),
                "rank_or_sign_strength": float(r["raw05_direction_correct_rate"]),
                "gate_count": int(r["pass_models"]),
                "error_type": "reported LOO/L2O reliability",
            }
        )

    e40 = read_csv("test_movement_fingerprint_selector_views.csv")
    rows.append(
        {
            "selector": "test_movement_fingerprint",
            "source": "test_movement_fingerprint_selector_views.csv",
            "n_views": len(e40),
            "best_error": safe_min(e40["loocv_mae"]),
            "median_error": safe_median(e40["loocv_mae"]),
            "best_p90_error": safe_min(e40["loocv_max_abs_error"]),
            "best_l2o_error": np.nan,
            "rank_or_sign_strength": safe_median(e40["pairwise_rank_accuracy"]),
            "gate_count": int(e40["loose_selector_gate"].fillna(False).astype(bool).sum()),
            "error_type": "known-anchor LOO movement fingerprint",
        }
    )

    e41 = read_csv("movement_badaxis_geometry_selector_views.csv")
    rows.append(
        {
            "selector": "movement_badaxis_geometry",
            "source": "movement_badaxis_geometry_selector_views.csv",
            "n_views": len(e41),
            "best_error": safe_min(e41["loocv_mae"]),
            "median_error": safe_median(e41["loocv_mae"]),
            "best_p90_error": safe_min(e41["loocv_max_abs_error"]),
            "best_l2o_error": np.nan,
            "rank_or_sign_strength": safe_median(e41["pairwise_rank_accuracy"]),
            "gate_count": int(e41["loose_selector_gate"].fillna(False).astype(bool).sum()),
            "error_type": "known-anchor LOO movement plus bad-axis geometry",
        }
    )

    e42 = read_csv("zero_anchor_selector_calibration_views.csv")
    rows.append(
        {
            "selector": "fixed_zero_anchor_axis",
            "source": "zero_anchor_selector_calibration_views.csv",
            "n_views": len(e42),
            "best_error": safe_min(e42["nonbaseline_loocv_mae"]),
            "median_error": safe_median(e42["nonbaseline_loocv_mae"]),
            "best_p90_error": safe_min(e42["nonbaseline_loocv_max_abs_error"]),
            "best_l2o_error": np.nan,
            "rank_or_sign_strength": safe_median(e42["pairwise_rank_accuracy"]),
            "gate_count": int(e42["usable_zero_anchor_gate"].fillna(False).astype(bool).sum()),
            "error_type": "nonbaseline LOO with A2C8 fixed at zero",
        }
    )

    df = pd.DataFrame(rows)
    for col in ["best_error", "median_error", "best_p90_error", "best_l2o_error"]:
        df[f"raw05_gap_to_{col}"] = df[col].apply(lambda x: ratio(RAW05_GAP, x))
        df[f"{col}_below_raw05_gap"] = df[col] <= RAW05_GAP
        df[f"{col}_below_half_raw05_gap"] = df[col] <= RAW05_GAP / 2.0
    df["frontier_resolution_gate"] = (
        df["best_error_below_raw05_gap"].fillna(False)
        & df["best_l2o_error_below_raw05_gap"].fillna(True)
        & (df["gate_count"] > 0)
    )
    return df.sort_values(["frontier_resolution_gate", "best_error"], ascending=[False, True])


def edge_rows_from_candidate_predictions(
    path: str,
    selector_name: str,
    view_error_map: dict[str, float],
    predicted_col: str = "predicted_delta_vs_best",
    view_col: str = "view",
) -> pd.DataFrame:
    df = read_csv(path).copy()
    if predicted_col not in df.columns:
        return pd.DataFrame()
    if view_col not in df.columns:
        df[view_col] = selector_name
    keep = [
        c
        for c in ["name", "file", "role", view_col, predicted_col, "predicted_public_lb"]
        if c in df.columns
    ]
    out = df[keep].copy()
    out = out.rename(columns={view_col: "view", predicted_col: "predicted_delta"})
    out["selector"] = selector_name
    out["error_scale"] = out["view"].map(view_error_map).astype(float)
    out["edge_vs_a2c8"] = -out["predicted_delta"]
    out["edge_vs_raw05"] = RAW05_GAP - out["predicted_delta"]
    out["edge_vs_a2c8_to_error"] = out.apply(
        lambda r: ratio(r["edge_vs_a2c8"], r["error_scale"]), axis=1
    )
    out["edge_vs_raw05_to_error"] = out.apply(
        lambda r: ratio(r["edge_vs_raw05"], r["error_scale"]), axis=1
    )
    out["certified_better_than_a2c8"] = out["predicted_delta"] + out["error_scale"] < 0
    out["certified_better_than_raw05"] = (
        out["predicted_delta"] + out["error_scale"] < RAW05_GAP
    )
    return out


def candidate_edge_table(selector_df: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    e40_views = read_csv("test_movement_fingerprint_selector_views.csv")
    e40_errors = dict(zip(e40_views["view"], e40_views["loocv_mae"]))
    frames.append(
        edge_rows_from_candidate_predictions(
            "test_movement_fingerprint_selector_candidates.csv",
            "test_movement_fingerprint",
            e40_errors,
            predicted_col="predicted_delta_vs_best",
        )
    )

    e41_views = read_csv("movement_badaxis_geometry_selector_views.csv")
    e41_errors = dict(zip(e41_views["view"], e41_views["loocv_mae"]))
    frames.append(
        edge_rows_from_candidate_predictions(
            "movement_badaxis_geometry_selector_candidates.csv",
            "movement_badaxis_geometry",
            e41_errors,
            predicted_col="predicted_delta_vs_best",
        )
    )

    e42_views = read_csv("zero_anchor_selector_calibration_views.csv")
    e42_errors = dict(zip(e42_views["view"], e42_views["nonbaseline_loocv_mae"]))
    frames.append(
        edge_rows_from_candidate_predictions(
            "zero_anchor_selector_calibration_candidates.csv",
            "fixed_zero_anchor_axis",
            e42_errors,
            predicted_col="predicted_delta_vs_best",
        )
    )

    pair = read_csv("public_pairwise_order_selector_candidates.csv")
    pair_best_error = float(
        selector_df.loc[
            selector_df["selector"].eq("pairwise_public_order_models"), "best_error"
        ].iloc[0]
    )
    pair_keep = pair[
        [
            "file",
            "basename",
            "candidate_family",
            "pair_delta_vs_a2c8_p90",
            "pair_delta_vs_a2c8_mean",
            "pair_beats_a2c8_rate",
            "pair_submit_gate",
        ]
    ].copy()
    pair_keep = pair_keep.rename(
        columns={
            "basename": "name",
            "candidate_family": "role",
            "pair_delta_vs_a2c8_p90": "predicted_delta",
        }
    )
    pair_keep["view"] = "pair_p90"
    pair_keep["selector"] = "pairwise_public_order_models"
    pair_keep["predicted_public_lb"] = A2C8_LB + pair_keep["predicted_delta"]
    pair_keep["error_scale"] = pair_best_error
    pair_keep["edge_vs_a2c8"] = -pair_keep["predicted_delta"]
    pair_keep["edge_vs_raw05"] = RAW05_GAP - pair_keep["predicted_delta"]
    pair_keep["edge_vs_a2c8_to_error"] = pair_keep["edge_vs_a2c8"].apply(
        lambda x: ratio(x, pair_best_error)
    )
    pair_keep["edge_vs_raw05_to_error"] = pair_keep["edge_vs_raw05"].apply(
        lambda x: ratio(x, pair_best_error)
    )
    pair_keep["certified_better_than_a2c8"] = (
        pair_keep["predicted_delta"] + pair_best_error < 0
    )
    pair_keep["certified_better_than_raw05"] = (
        pair_keep["predicted_delta"] + pair_best_error < RAW05_GAP
    )
    frames.append(pair_keep)

    out = pd.concat([f for f in frames if len(f)], ignore_index=True, sort=False)
    out["public_edge_readable"] = (
        out["certified_better_than_a2c8"] | out["certified_better_than_raw05"]
    )
    return out.sort_values(
        ["public_edge_readable", "edge_vs_a2c8_to_error", "edge_vs_raw05_to_error"],
        ascending=[False, False, False],
    )


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_\n"
    show = df.copy()
    for col in show.columns:
        if pd.api.types.is_float_dtype(show[col]):
            show[col] = show[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            show[col] = show[col].map(lambda x: "" if pd.isna(x) else str(x))
    headers = list(show.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in show.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines) + "\n"


def write_report(selector_df: pd.DataFrame, edge_df: pd.DataFrame) -> None:
    out_path = OUT / "selector_resolution_boundary_audit_report.md"

    best_selector = selector_df.sort_values("best_error").iloc[0]
    certified_a2 = int(edge_df["certified_better_than_a2c8"].fillna(False).sum())
    certified_raw = int(edge_df["certified_better_than_raw05"].fillna(False).sum())
    readable = int(edge_df["public_edge_readable"].fillna(False).sum())

    top_edge = edge_df.head(12).copy()
    selector_show = selector_df[
        [
            "selector",
            "n_views",
            "best_error",
            "median_error",
            "best_l2o_error",
            "raw05_gap_to_best_error",
            "raw05_gap_to_best_l2o_error",
            "gate_count",
            "frontier_resolution_gate",
        ]
    ]

    with out_path.open("w", encoding="utf-8") as f:
        f.write("# E43 Selector Resolution Boundary Audit\n\n")
        f.write("## Observe\n\n")
        f.write(
            "E42 shows that nonbaseline rank can improve while frontier-scale candidate edges remain below selector error.\n\n"
        )
        f.write("## Wonder\n\n")
        f.write(
            "Is the 0.577439 plateau mainly a candidate-quality problem, or are current selectors simply unable to read edges at the raw05-A2C8 scale?\n\n"
        )
        f.write("## Hypothesis\n\n")
        f.write(
            "H42: if a local selector can justify a normal near-frontier submission, its known-anchor error must be below the raw05-A2C8 public gap and at least one unobserved candidate edge must exceed that selector error.\n\n"
        )
        f.write("## Method\n\n")
        f.write(
            f"- Raw05-A2C8 public gap: `{RAW05_GAP:.10f}`.\n"
            "- Collected pairwise public-order selector reliability, old hidden-subset reliability, OOF public-rank sanity, E40 movement fingerprints, E41 movement+axis geometry, and E42 fixed-zero axis calibration.\n"
            "- For candidate predictions, tested whether `predicted_delta + selector_error < 0` for A2C8 improvement and `< raw05_gap` for raw05 improvement.\n\n"
        )
        f.write("## Result\n\n")
        f.write(f"- selector frontier-resolution gates: `{int(selector_df['frontier_resolution_gate'].sum())}`.\n")
        f.write(f"- candidates certified better than A2C8 by error margin: `{certified_a2}`.\n")
        f.write(f"- candidates certified better than raw05 by error margin: `{certified_raw}`.\n")
        f.write(f"- public-edge-readable candidate rows: `{readable}`.\n")
        f.write(
            f"- best selector by error: `{best_selector['selector']}` with best error `{best_selector['best_error']:.9f}`, raw05-gap/error ratio `{best_selector['raw05_gap_to_best_error']:.6f}`.\n\n"
        )
        f.write("## Selector Resolution Summary\n\n")
        f.write(markdown_table(selector_show))
        f.write("\n\n")
        f.write("## Top Candidate Edge Rows\n\n")
        cols = [
            c
            for c in [
                "selector",
                "view",
                "name",
                "role",
                "predicted_delta",
                "error_scale",
                "edge_vs_a2c8_to_error",
                "edge_vs_raw05_to_error",
                "certified_better_than_a2c8",
                "certified_better_than_raw05",
            ]
            if c in top_edge.columns
        ]
        f.write(markdown_table(top_edge[cols]))
        f.write("\n\n")
        f.write("## Decision\n\n")
        f.write(
            "No audited selector has enough resolution to certify a near-frontier improvement. "
            "The best known-anchor selector error is still several times larger than the raw05-A2C8 public gap, and no candidate edge survives an error-margin test. "
            "This supports the bottleneck diagnosis: the current plateau is dominated by selector resolution/public-worldview uncertainty, not by lack of another small blend.\n\n"
        )
        f.write("## Outputs\n\n")
        f.write("- `analysis_outputs/selector_resolution_boundary_audit_selectors.csv`\n")
        f.write("- `analysis_outputs/selector_resolution_boundary_audit_candidate_edges.csv`\n")
        f.write("- `analysis_outputs/selector_resolution_boundary_audit_report.md`\n")


def main() -> None:
    selector_df = selector_resolution_table()
    edge_df = candidate_edge_table(selector_df)

    selector_df.to_csv(OUT / "selector_resolution_boundary_audit_selectors.csv", index=False)
    edge_df.to_csv(OUT / "selector_resolution_boundary_audit_candidate_edges.csv", index=False)
    write_report(selector_df, edge_df)

    print(
        "selectors=",
        len(selector_df),
        "frontier_gates=",
        int(selector_df["frontier_resolution_gate"].sum()),
        "certified_a2c8=",
        int(edge_df["certified_better_than_a2c8"].fillna(False).sum()),
        "certified_raw05=",
        int(edge_df["certified_better_than_raw05"].fillna(False).sum()),
    )


if __name__ == "__main__":
    main()
