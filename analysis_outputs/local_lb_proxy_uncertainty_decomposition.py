from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

RAW05_PUBLIC = 0.5775263072
RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

KNOWN_PATH = OUT / "local_lb_proxy_validation_known.csv"
MODEL_PATH = OUT / "local_lb_proxy_validation_model_scores.csv"
CANDIDATE_PATH = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
ANCHOR_ROBUST_PATH = OUT / "local_lb_anchor_robustness_predictions.csv"
STRUCTURAL_PATH = OUT / "local_lb_structural_candidate_predictions.csv"

KNOWN_ERROR_OUT = OUT / "local_lb_proxy_uncertainty_known_errors.csv"
ERROR_CORR_OUT = OUT / "local_lb_proxy_uncertainty_error_correlations.csv"
CANDIDATE_RISK_OUT = OUT / "local_lb_proxy_uncertainty_candidate_risk.csv"
FAMILY_SUMMARY_OUT = OUT / "local_lb_proxy_uncertainty_family_summary.csv"
REPORT_OUT = OUT / "local_lb_proxy_uncertainty_report.md"

FOCUS_FILES = [
    RAW05_FILE,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv",
    "submission_raw05_jepa_lowbadcon_71601b5f.csv",
    "submission_raw05_jepa_lowbadcon_2240eb29.csv",
    "submission_raw05_jepa_directcon_a903806a.csv",
    "submission_raw05_jepa_directcon_ff079802.csv",
    "submission_public6entropy_raw05_q3s4_g250_b19cb905.csv",
    "submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv",
]

ANCHOR_FEATURES = [
    "actual_anchor_score_final",
    "mean_actual_anchor",
    "abs_delta_vs_raw05_rawaxis",
    "abs_bad_residual_axis_ratio",
    "abs_ordinal_axis_ratio",
    "mean_abs_move_vs_raw05",
    "prob_span",
]


def num(frame: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=np.float64)
    return pd.to_numeric(frame[col], errors="coerce").astype(np.float64)


def best_loocv_mae(model_scores: pd.DataFrame) -> tuple[str, float, float]:
    loocv = model_scores[model_scores["kind"].astype(str).eq("leave_one_anchor_out")].copy()
    loocv = loocv.sort_values(["mae", "rmse"]).reset_index(drop=True)
    row = loocv.iloc[0]
    return str(row["model"]), float(row["mae"]), float(row["rmse"])


def add_optional_tables(candidates: pd.DataFrame) -> pd.DataFrame:
    out = candidates.copy()
    if ANCHOR_ROBUST_PATH.exists():
        robust_cols = [
            "file",
            "anchor_robust_delta_mean",
            "anchor_robust_delta_p90",
            "anchor_robust_delta_max",
            "anchor_robust_std",
            "anchor_robust_spread",
            "anchor_robust_beat_raw05_rate",
            "anchor_robust_selection_score",
        ]
        robust = pd.read_csv(ANCHOR_ROBUST_PATH, usecols=lambda c: c in robust_cols)
        robust = robust.drop_duplicates("file")
        out = out.merge(robust, on="file", how="left")

    if STRUCTURAL_PATH.exists():
        structural_cols = [
            "file",
            "structural_raw05_relative_delta_vs_raw05_public",
            "structural_raw05_relative_model_spread",
            "q3s4_motif_proj",
            "q3s4_motif_cos",
            "q3s4_motif_orth_ratio",
            "q3s4_to_ctx_ratio_capped",
            "sv1_frac",
            "rank_entropy",
        ]
        structural = pd.read_csv(STRUCTURAL_PATH, usecols=lambda c: c in structural_cols)
        structural = structural.drop_duplicates("file")
        out = out.merge(structural, on="file", how="left", suffixes=("", "_struct"))
    return out


def decompose_known_errors(known: pd.DataFrame, best_model: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    loocv_error_cols = [
        c for c in known.columns if c.startswith("loocv_ridge_") and c.endswith("_error")
    ]
    out = known.copy()
    error_abs = out[loocv_error_cols].abs()
    out["loocv_error_abs_mean"] = error_abs.mean(axis=1)
    out["loocv_error_abs_max"] = error_abs.max(axis=1)
    out["loocv_error_signed_mean"] = out[loocv_error_cols].mean(axis=1)
    out["worst_loocv_model"] = error_abs.idxmax(axis=1).str.replace("_error", "", regex=False)
    out["worst_loocv_error"] = [
        float(out.loc[i, f"{model}_error"]) if f"{model}_error" in out.columns else np.nan
        for i, model in out["worst_loocv_model"].items()
    ]
    best_col = f"{best_model}_error"
    if best_col in out.columns:
        out["best_model_error"] = out[best_col]
        out["best_model_abs_error"] = out[best_col].abs()
    else:
        out["best_model_error"] = np.nan
        out["best_model_abs_error"] = np.nan

    keep = [
        "file",
        "known_public",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "actual_gap_vs_raw05_public",
        "posterior_gap_vs_raw05_public",
        "abs_delta_vs_raw05_rawaxis",
        "abs_bad_residual_axis_ratio",
        "abs_ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "prob_span",
        "best_model_error",
        "best_model_abs_error",
        "loocv_error_abs_mean",
        "loocv_error_abs_max",
        "loocv_error_signed_mean",
        "worst_loocv_model",
        "worst_loocv_error",
    ]
    keep = [c for c in keep if c in out.columns]
    known_errors = out[keep].sort_values("best_model_abs_error", ascending=False)

    rows = []
    for err_col in loocv_error_cols:
        for feat in ANCHOR_FEATURES:
            if feat not in out.columns:
                continue
            sub = out[[err_col, feat]].dropna()
            if len(sub) < 4 or sub[feat].nunique() < 2:
                continue
            rows.append(
                {
                    "model": err_col.replace("_error", ""),
                    "error_feature": "abs_error",
                    "anchor_feature": feat,
                    "spearman_abs_error": float(sub[err_col].abs().corr(sub[feat], method="spearman")),
                    "pearson_abs_error": float(sub[err_col].abs().corr(sub[feat], method="pearson")),
                }
            )
    corr = pd.DataFrame(rows)
    if len(corr):
        corr["abs_spearman"] = corr["spearman_abs_error"].abs()
        corr = corr.sort_values(["abs_spearman", "model"], ascending=[False, True]).reset_index(drop=True)
    return known_errors, corr


def anchor_feature_distance(known: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=candidates.index)
    used = [c for c in ANCHOR_FEATURES if c in known.columns and c in candidates.columns]
    if not used:
        out["anchor_feature_zdist"] = np.nan
        out["anchor_feature_max_abs_z"] = np.nan
        out["anchor_feature_hull_violations"] = np.nan
        out["anchor_feature_hull_severity"] = np.nan
        return out

    z_parts = []
    violation_parts = []
    severity_parts = []
    for col in used:
        known_col = num(known, col)
        cand_col = num(candidates, col)
        center = float(known_col.median())
        scale = float(known_col.std(ddof=0))
        if not np.isfinite(scale) or scale < 1e-12:
            scale = max(float(known_col.max() - known_col.min()), 1e-12)
        filled = cand_col.fillna(center)
        z = (filled - center) / scale
        z_parts.append(z.to_numpy(dtype=np.float64))

        lo = float(known_col.min())
        hi = float(known_col.max())
        margin = max((hi - lo) * 0.10, scale * 0.10, 1e-12)
        below = np.maximum((lo - margin) - filled, 0.0)
        above = np.maximum(filled - (hi + margin), 0.0)
        exceed = below + above
        violation_parts.append((exceed > 0).astype(np.float64).to_numpy())
        severity_parts.append((exceed / scale).to_numpy(dtype=np.float64))

    z_mat = np.vstack(z_parts).T
    out["anchor_feature_zdist"] = np.sqrt(np.nanmean(z_mat**2, axis=1))
    out["anchor_feature_max_abs_z"] = np.nanmax(np.abs(z_mat), axis=1)
    out["anchor_feature_hull_violations"] = np.vstack(violation_parts).T.sum(axis=1)
    out["anchor_feature_hull_severity"] = np.vstack(severity_parts).T.sum(axis=1)
    return out


def classify_candidate_risk(
    row: pd.Series,
    best_mae: float,
    micro_floor: float,
) -> tuple[str, str]:
    if str(row.get("file", "")) == RAW05_FILE:
        return "raw05_baseline", "raw05_baseline"

    flags: list[str] = []
    delta = float(row.get("available_raw05_relative_delta_vs_raw05_public", np.nan))
    spread = float(row.get("available_raw05_relative_model_spread", np.nan))
    edge = -delta if np.isfinite(delta) else np.nan
    agreement = float(row.get("relative_model_improve_rate", np.nan))
    rel_max = float(row.get("relative_model_delta_max", np.nan))
    zdist = float(row.get("anchor_feature_zdist", np.nan))
    hull = float(row.get("anchor_feature_hull_violations", np.nan))
    robust_max = float(row.get("anchor_robust_delta_max", np.nan))
    robust_p90 = float(row.get("anchor_robust_delta_p90", np.nan))
    structural_delta = float(row.get("structural_raw05_relative_delta_vs_raw05_public", np.nan))

    if np.isfinite(delta) and delta < 0:
        flags.append("proxy_mean_below_raw05")
    if np.isfinite(agreement) and agreement >= 0.999:
        flags.append("all_relative_models_improve")
    elif np.isfinite(agreement) and agreement < 0.67:
        flags.append("model_sign_disagreement")
    if np.isfinite(edge) and edge < micro_floor:
        flags.append("below_5pct_best_mae")
    if np.isfinite(spread) and np.isfinite(edge) and edge < spread:
        flags.append("edge_smaller_than_model_spread")
    if np.isfinite(rel_max) and rel_max > 0:
        flags.append("some_model_worse_than_raw05")
    if np.isfinite(robust_p90) and robust_p90 > 0:
        flags.append("anchor_drop_p90_positive_tail")
    if np.isfinite(robust_max) and robust_max > 0:
        flags.append("anchor_drop_max_positive_tail")
    if np.isfinite(structural_delta) and structural_delta > 0:
        flags.append("structural_proxy_worse_than_raw05")
    if np.isfinite(zdist) and zdist > 4.0:
        flags.append("far_from_known_anchor_feature_center")
    if np.isfinite(hull) and hull >= 2:
        flags.append("outside_known_anchor_hull")

    raw_axis = abs(float(row.get("delta_vs_raw05_rawaxis", np.nan)))
    bad_axis = abs(float(row.get("bad_residual_axis_ratio", np.nan)))
    motif_cos = float(row.get("q3s4_motif_cos", row.get("q3s4_motif_cos_struct", np.nan)))
    motif_orth = float(row.get("q3s4_motif_orth_ratio", row.get("q3s4_motif_orth_ratio_struct", np.nan)))
    if (
        np.isfinite(raw_axis)
        and raw_axis < 2e-7
        and np.isfinite(bad_axis)
        and bad_axis < 2e-4
        and (not np.isfinite(motif_cos) or motif_cos > 0.9999)
        and (not np.isfinite(motif_orth) or motif_orth < 0.02)
    ):
        flags.append("strict_raw05_motif_guard")

    if (
        np.isfinite(delta)
        and delta < -0.25 * best_mae
        and np.isfinite(agreement)
        and agreement >= 0.999
        and np.isfinite(rel_max)
        and rel_max < 0
        and (not np.isfinite(robust_max) or robust_max < 0)
    ):
        tier = "resolved_local_gain"
    elif np.isfinite(zdist) and zdist > 6.0:
        tier = "out_of_domain_proxy"
    elif np.isfinite(delta) and delta < 0 and np.isfinite(edge) and edge < micro_floor:
        tier = "below_proxy_resolution"
    elif np.isfinite(robust_max) and robust_max > 0:
        tier = "anchor_tail_risk"
    elif np.isfinite(agreement) and agreement < 0.67:
        tier = "model_disagreement"
    elif np.isfinite(delta) and delta < 0:
        tier = "weak_local_consensus"
    else:
        tier = "no_local_edge"

    return tier, "|".join(flags)


def build_candidate_risk(
    known: pd.DataFrame,
    model_scores: pd.DataFrame,
    candidates: pd.DataFrame,
    best_mae: float,
) -> pd.DataFrame:
    out = add_optional_tables(candidates)
    out = out.drop_duplicates("file").reset_index(drop=True)

    rel_cols = [
        c
        for c in out.columns
        if c.startswith("fit_")
        and c.endswith("_raw05_relative_public")
        and "_axis_raw05_relative_public" not in c
    ]
    axis_rel_cols = [
        c for c in out.columns if c.startswith("fit_") and c.endswith("_axis_raw05_relative_public")
    ]

    full_delta = out[rel_cols].apply(pd.to_numeric, errors="coerce") - RAW05_PUBLIC if rel_cols else pd.DataFrame(index=out.index)
    axis_delta = out[axis_rel_cols].apply(pd.to_numeric, errors="coerce") - RAW05_PUBLIC if axis_rel_cols else pd.DataFrame(index=out.index)

    use_axis = out.get("available_proxy_model_family", "").astype(str).eq("axis_only")
    model_delta_rows = []
    for i in out.index:
        vals = axis_delta.loc[i].dropna() if bool(use_axis.loc[i]) and len(axis_delta.columns) else full_delta.loc[i].dropna()
        if vals.empty and len(full_delta.columns):
            vals = full_delta.loc[i].dropna()
        model_delta_rows.append(vals.to_numpy(dtype=np.float64))

    out["relative_model_count"] = [len(v) for v in model_delta_rows]
    out["relative_model_delta_min"] = [float(np.min(v)) if len(v) else np.nan for v in model_delta_rows]
    out["relative_model_delta_max"] = [float(np.max(v)) if len(v) else np.nan for v in model_delta_rows]
    out["relative_model_delta_mean_unweighted"] = [float(np.mean(v)) if len(v) else np.nan for v in model_delta_rows]
    out["relative_model_delta_std"] = [float(np.std(v)) if len(v) else np.nan for v in model_delta_rows]
    out["relative_model_improve_rate"] = [float(np.mean(v < 0)) if len(v) else np.nan for v in model_delta_rows]

    out = pd.concat([out, anchor_feature_distance(known, out)], axis=1)

    best_model = model_scores[
        model_scores["kind"].astype(str).eq("leave_one_anchor_out")
    ].sort_values("mae").iloc[0]
    best_model_error_col = f"{best_model['model']}_error"
    known_best_abs = num(known, best_model_error_col, np.nan).abs().dropna()
    p80_abs_error = float(known_best_abs.quantile(0.80)) if len(known_best_abs) else best_mae
    micro_floor = max(0.05 * best_mae, 5e-6)

    out["edge_vs_raw05"] = -num(out, "available_raw05_relative_delta_vs_raw05_public")
    out["edge_to_best_mae"] = out["edge_vs_raw05"] / max(best_mae, 1e-12)
    out["edge_to_best_p80_abs_error"] = out["edge_vs_raw05"] / max(p80_abs_error, 1e-12)
    out["edge_to_model_spread"] = out["edge_vs_raw05"] / np.maximum(
        num(out, "available_raw05_relative_model_spread").abs(), 1e-12
    )
    out["positive_anchor_p90_tail"] = np.maximum(num(out, "anchor_robust_delta_p90", 0.0), 0.0)
    out["positive_anchor_max_tail"] = np.maximum(num(out, "anchor_robust_delta_max", 0.0), 0.0)
    out["positive_structural_delta"] = np.maximum(
        num(out, "structural_raw05_relative_delta_vs_raw05_public", 0.0), 0.0
    )
    out["uncertainty_load"] = (
        best_mae
        + np.maximum(num(out, "available_raw05_relative_model_spread", 0.0), 0.0)
        + out["positive_anchor_p90_tail"]
        + 0.5 * out["positive_structural_delta"]
        + 5e-5 * num(out, "anchor_feature_hull_violations", 0.0)
        + 2e-5 * num(out, "anchor_feature_hull_severity", 0.0)
    )
    out["edge_to_uncertainty_load"] = out["edge_vs_raw05"] / np.maximum(out["uncertainty_load"], 1e-12)
    out["submit_risk_score"] = (
        num(out, "available_raw05_relative_delta_vs_raw05_public", 0.0)
        + 0.25 * np.maximum(num(out, "available_raw05_relative_model_spread", 0.0), 0.0)
        + 0.50 * out["positive_anchor_p90_tail"]
        + 0.25 * out["positive_structural_delta"]
        + 2e-5 * num(out, "anchor_feature_hull_severity", 0.0)
    )

    tiers_flags = [classify_candidate_risk(row, best_mae, micro_floor) for _, row in out.iterrows()]
    out["local_uncertainty_tier"] = [x[0] for x in tiers_flags]
    out["local_uncertainty_flags"] = [x[1] for x in tiers_flags]
    out["is_focus_candidate"] = out["file"].astype(str).isin(FOCUS_FILES)

    keep = [
        "file",
        "rank",
        "tier",
        "family",
        "metric_source",
        "local_uncertainty_tier",
        "local_uncertainty_flags",
        "is_focus_candidate",
        "available_proxy_model_family",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "relative_model_count",
        "relative_model_improve_rate",
        "relative_model_delta_min",
        "relative_model_delta_max",
        "edge_vs_raw05",
        "edge_to_best_mae",
        "edge_to_best_p80_abs_error",
        "edge_to_model_spread",
        "edge_to_uncertainty_load",
        "uncertainty_load",
        "submit_risk_score",
        "anchor_robust_delta_mean",
        "anchor_robust_delta_p90",
        "anchor_robust_delta_max",
        "anchor_robust_beat_raw05_rate",
        "structural_raw05_relative_delta_vs_raw05_public",
        "structural_raw05_relative_model_spread",
        "anchor_feature_zdist",
        "anchor_feature_max_abs_z",
        "anchor_feature_hull_violations",
        "anchor_feature_hull_severity",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "lejepa_residual_health",
        "lejepa_combined_rank",
    ]
    keep = [c for c in keep if c in out.columns]
    return out[keep].sort_values(["submit_risk_score", "available_raw05_relative_delta_vs_raw05_public"]).reset_index(drop=True)


def family_summary(risk: pd.DataFrame) -> pd.DataFrame:
    fam_col = "family" if "family" in risk.columns else "tier"
    tmp = risk.copy()
    tmp[fam_col] = tmp[fam_col].fillna("unknown").astype(str)
    rows = []
    for fam, g in tmp.groupby(fam_col, dropna=False):
        rows.append(
            {
                "family": fam,
                "n": len(g),
                "best_submit_risk_score": float(g["submit_risk_score"].min()),
                "best_available_delta": float(g["available_raw05_relative_delta_vs_raw05_public"].min()),
                "median_edge_to_mae": float(g["edge_to_best_mae"].median()),
                "median_model_improve_rate": float(g["relative_model_improve_rate"].median()),
                "median_anchor_tail_max": float(num(g, "anchor_robust_delta_max").median()),
                "median_structural_delta": float(num(g, "structural_raw05_relative_delta_vs_raw05_public").median()),
                "focus_count": int(g["is_focus_candidate"].sum()),
                "top_file": str(g.sort_values("submit_risk_score").iloc[0]["file"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["best_submit_risk_score", "best_available_delta"]).reset_index(drop=True)


def markdown_table(frame: pd.DataFrame, cols: list[str], n: int = 20, digits: int = 10) -> str:
    cols = [c for c in cols if c in frame.columns]
    return frame[cols].head(n).round(digits).to_csv(index=False).strip()


def write_report(
    model_scores: pd.DataFrame,
    known_errors: pd.DataFrame,
    error_corr: pd.DataFrame,
    risk: pd.DataFrame,
    family: pd.DataFrame,
    best_model: str,
    best_mae: float,
    best_rmse: float,
) -> None:
    best_abs = known_errors["best_model_abs_error"].dropna()
    p50 = float(best_abs.quantile(0.50)) if len(best_abs) else np.nan
    p80 = float(best_abs.quantile(0.80)) if len(best_abs) else np.nan
    p90 = float(best_abs.quantile(0.90)) if len(best_abs) else np.nan
    max_abs = float(best_abs.max()) if len(best_abs) else np.nan
    raw05_known = known_errors[known_errors["file"].astype(str).eq(RAW05_FILE)]
    raw05_err = float(raw05_known["best_model_error"].iloc[0]) if len(raw05_known) else np.nan

    focus = risk[risk["is_focus_candidate"]].copy()
    if len(focus):
        focus["focus_order"] = focus["file"].map({name: i for i, name in enumerate(FOCUS_FILES)})
        focus = focus.sort_values("focus_order")

    unresolved = risk[
        risk["available_raw05_relative_delta_vs_raw05_public"].lt(0)
        & risk["edge_to_best_mae"].lt(0.05)
    ]
    resolved = risk[risk["local_uncertainty_tier"].eq("resolved_local_gain")]

    lines = [
        "# Local LB Proxy Uncertainty Decomposition",
        "",
        "This report tests how much the local public-LB proxy can really resolve from the six known public submissions.",
        "It should be read as a submission-risk diagnostic, not as a ground-truth replacement for public LB.",
        "",
        "## Resolution",
        "",
        f"- Best leave-one-public-anchor model: `{best_model}`.",
        f"- LOOCV MAE/RMSE: `{best_mae:.10f}` / `{best_rmse:.10f}`.",
        f"- Best-model absolute error p50/p80/p90/max over known anchors: `{p50:.10f}` / `{p80:.10f}` / `{p90:.10f}` / `{max_abs:.10f}`.",
        f"- Raw05 is over/under-predicted by the best model by `{raw05_err:.10f}`.",
        f"- Candidates with raw05-relative edge below `0.05 * MAE = {0.05 * best_mae:.10f}` are below this proxy's practical resolution.",
        f"- Negative-delta candidates below that 5% resolution floor: `{len(unresolved)}` / `{len(risk)}`.",
        f"- Locally resolved candidates under the strict rule: `{len(resolved)}`.",
        "",
        "## Known Anchor Error Decomposition",
        "",
        "```csv",
        markdown_table(
            known_errors,
            [
                "file",
                "known_public",
                "actual_anchor_score_final",
                "abs_delta_vs_raw05_rawaxis",
                "abs_bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
                "best_model_error",
                "best_model_abs_error",
                "loocv_error_abs_mean",
                "worst_loocv_model",
            ],
            n=10,
        ),
        "```",
        "",
        "## Strongest Error Correlations",
        "",
        "```csv",
        markdown_table(
            error_corr,
            ["model", "anchor_feature", "spearman_abs_error", "pearson_abs_error"],
            n=18,
            digits=6,
        ),
        "```",
        "",
        "## Focus Candidate Risk",
        "",
        "```csv",
        markdown_table(
            focus,
            [
                "file",
                "rank",
                "tier",
                "local_uncertainty_tier",
                "available_raw05_relative_delta_vs_raw05_public",
                "available_raw05_relative_model_spread",
                "relative_model_improve_rate",
                "edge_to_best_mae",
                "edge_to_model_spread",
                "anchor_robust_delta_p90",
                "anchor_robust_delta_max",
                "structural_raw05_relative_delta_vs_raw05_public",
                "anchor_feature_zdist",
                "submit_risk_score",
                "local_uncertainty_flags",
            ],
            n=30,
            digits=10,
        ),
        "```",
        "",
        "## Best Raw Risk Scores",
        "",
        "```csv",
        markdown_table(
            risk,
            [
                "file",
                "rank",
                "tier",
                "family",
                "local_uncertainty_tier",
                "available_raw05_relative_delta_vs_raw05_public",
                "available_raw05_relative_model_spread",
                "relative_model_improve_rate",
                "edge_to_best_mae",
                "edge_to_uncertainty_load",
                "anchor_robust_delta_max",
                "structural_raw05_relative_delta_vs_raw05_public",
                "anchor_feature_zdist",
                "submit_risk_score",
            ],
            n=24,
            digits=10,
        ),
        "```",
        "",
        "## Family Summary",
        "",
        "```csv",
        markdown_table(
            family,
            [
                "family",
                "n",
                "best_submit_risk_score",
                "best_available_delta",
                "median_edge_to_mae",
                "median_model_improve_rate",
                "median_anchor_tail_max",
                "median_structural_delta",
                "focus_count",
                "top_file",
            ],
            n=30,
            digits=10,
        ),
        "```",
        "",
        "## Practical Read",
        "",
        "- The proxy can rank coarse regimes, but it cannot prove the 1e-6 to 1e-5 differences among raw05-compatible JEPA micro-candidates.",
        "- The e40/lowbad/direct candidates are therefore local-structure probes, not locally verified LB improvements.",
        "- Larger negative local deltas from public6entropy-style rows are not automatically better because they carry structural/anchor-tail risk outside the JEPA guardrails.",
        "- Submit order should keep a conservative structural candidate first, then use lowbad/direct variants as information probes only if public LB budget allows.",
        "",
        "## Files",
        "",
        f"- `{KNOWN_ERROR_OUT.name}`",
        f"- `{ERROR_CORR_OUT.name}`",
        f"- `{CANDIDATE_RISK_OUT.name}`",
        f"- `{FAMILY_SUMMARY_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known = pd.read_csv(KNOWN_PATH)
    model_scores = pd.read_csv(MODEL_PATH)
    candidates = pd.read_csv(CANDIDATE_PATH)

    best_model, best_mae, best_rmse = best_loocv_mae(model_scores)
    known_errors, error_corr = decompose_known_errors(known, best_model)
    risk = build_candidate_risk(known, model_scores, candidates, best_mae)
    fam = family_summary(risk)

    known_errors.to_csv(KNOWN_ERROR_OUT, index=False)
    error_corr.to_csv(ERROR_CORR_OUT, index=False)
    risk.to_csv(CANDIDATE_RISK_OUT, index=False)
    fam.to_csv(FAMILY_SUMMARY_OUT, index=False)
    write_report(model_scores, known_errors, error_corr, risk, fam, best_model, best_mae, best_rmse)

    print(f"best_model={best_model} mae={best_mae:.10f} rmse={best_rmse:.10f}")
    print("\n[focus]")
    focus = risk[risk["is_focus_candidate"]].copy()
    if len(focus):
        focus["focus_order"] = focus["file"].map({name: i for i, name in enumerate(FOCUS_FILES)})
        focus = focus.sort_values("focus_order")
        cols = [
            "file",
            "rank",
            "tier",
            "local_uncertainty_tier",
            "available_raw05_relative_delta_vs_raw05_public",
            "available_raw05_relative_model_spread",
            "relative_model_improve_rate",
            "edge_to_best_mae",
            "anchor_robust_delta_p90",
            "anchor_robust_delta_max",
            "structural_raw05_relative_delta_vs_raw05_public",
            "anchor_feature_zdist",
            "submit_risk_score",
        ]
        print(focus[[c for c in cols if c in focus.columns]].round(10).to_string(index=False))
    print("\n[top risk scores]")
    cols = [
        "file",
        "rank",
        "tier",
        "family",
        "local_uncertainty_tier",
        "available_raw05_relative_delta_vs_raw05_public",
        "edge_to_best_mae",
        "edge_to_uncertainty_load",
        "submit_risk_score",
    ]
    print(risk[[c for c in cols if c in risk.columns]].head(16).round(10).to_string(index=False))
    print(f"\nwrote: {KNOWN_ERROR_OUT}")
    print(f"wrote: {ERROR_CORR_OUT}")
    print(f"wrote: {CANDIDATE_RISK_OUT}")
    print(f"wrote: {FAMILY_SUMMARY_OUT}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
