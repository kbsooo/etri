from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

RANKER = OUT / "public_lb_actual_anchor_ranker_scores.csv"
CALIBRATION = OUT / "public_lb_actual_anchor_ranker_calibration.csv"
PRIORITY = OUT / "final_jepa_candidate_priority_20260527.csv"
EXTRA_CANDIDATE_TABLES = [
    OUT / "raw05_jepa_lowbad_motif_search_shortlist.csv",
    OUT / "raw05_jepa_direct_constrained_search_shortlist.csv",
    OUT / "raw05_jepa_axislocal_posterior_sweep_shortlist.csv",
    OUT / "raw05_jepa_anchorrobust_motif_graft_shortlist.csv",
    OUT / "raw05_jepa_structural_constrained_refine_shortlist.csv",
    OUT / "raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv",
    OUT / "raw05_jepa_axisbridge_posterior_repair_shortlist.csv",
    OUT / "raw05_jepa_axisbudget_motif_bridge_shortlist.csv",
    OUT / "raw05_jepa_tangent_nullspace_refine_shortlist.csv",
    OUT / "raw05_jepa_blockcount_regularized_refine_shortlist.csv",
    OUT / "jepa_block_count_shift_actual_anchor_augmented.csv",
    OUT / "public_lb_actual_anchor_missing_candidate_augmented.csv",
    OUT / "raw05_jepa_public6_q3s4_axis_corrected_shortlist.csv",
    OUT / "raw05_jepa_public6_drift_microperturb_shortlist.csv",
    OUT / "raw05_jepa_compat_band_refine_shortlist.csv",
    OUT / "public_lb_six_anchor_entropy_projection_shortlist.csv",
]

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
RAW05_PUBLIC = 0.5775263072

KNOWN_OUT = OUT / "local_lb_proxy_validation_known.csv"
MODEL_OUT = OUT / "local_lb_proxy_validation_model_scores.csv"
CAND_OUT = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
REPORT_OUT = OUT / "local_lb_proxy_validation_report.md"


def as_float(frame: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=np.float64)
    return pd.to_numeric(frame[col], errors="coerce").fillna(default).astype(np.float64)


def add_derived_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["actual_anchor_score_final"] = as_float(out, "actual_anchor_score_final", np.nan)
    out["mean_actual_anchor"] = as_float(out, "mean_actual_anchor", np.nan)
    out["posterior_expected_public_vs_anchor"] = as_float(out, "posterior_expected_public_vs_anchor", np.nan)
    out["delta_vs_raw05_rawaxis"] = as_float(out, "delta_vs_raw05_rawaxis", 0.0)
    out["bad_residual_axis_ratio"] = as_float(out, "bad_residual_axis_ratio", 0.0)
    out["ordinal_axis_ratio"] = as_float(out, "ordinal_axis_ratio", 0.0)
    out["mean_abs_move_vs_raw05"] = as_float(out, "mean_abs_move_vs_raw05", 0.0)
    out["min_prob"] = as_float(out, "min_prob", np.nan)
    out["max_prob"] = as_float(out, "max_prob", np.nan)
    out["abs_delta_vs_raw05_rawaxis"] = out["delta_vs_raw05_rawaxis"].abs()
    out["abs_bad_residual_axis_ratio"] = out["bad_residual_axis_ratio"].abs()
    out["abs_ordinal_axis_ratio"] = out["ordinal_axis_ratio"].abs()
    out["actual_minus_mean_anchor"] = out["actual_anchor_score_final"] - out["mean_actual_anchor"]
    out["actual_gap_vs_raw05_public"] = out["actual_anchor_score_final"] - RAW05_PUBLIC
    out["posterior_gap_vs_raw05_public"] = out["posterior_expected_public_vs_anchor"] - RAW05_PUBLIC
    out["prob_span"] = out["max_prob"] - out["min_prob"]
    return out


def pairwise_accuracy(pred: np.ndarray, y: np.ndarray) -> float:
    ok = 0
    total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dp = pred[i] - pred[j]
            dy = y[i] - y[j]
            if abs(dp) < 1e-15 or abs(dy) < 1e-15:
                continue
            total += 1
            ok += int(dp * dy > 0)
    return float(ok / total) if total else float("nan")


def corr(frame: pd.DataFrame, pred_col: str) -> tuple[float, float]:
    sub = frame[[pred_col, "known_public"]].dropna()
    if len(sub) < 3:
        return float("nan"), float("nan")
    return (
        float(sub[pred_col].corr(sub["known_public"], method="spearman")),
        float(sub[pred_col].corr(sub["known_public"], method="kendall")),
    )


def design_matrix(frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    return frame[features].to_numpy(dtype=np.float64)


def fit_ridge_predict(
    train: pd.DataFrame,
    y: np.ndarray,
    pred: pd.DataFrame,
    features: list[str],
    alpha: float,
) -> np.ndarray:
    x = design_matrix(train, features)
    xp = design_matrix(pred, features)
    mu = np.nanmean(x, axis=0)
    sigma = np.nanstd(x, axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    x = np.nan_to_num((x - mu) / sigma)
    xp = np.nan_to_num((xp - mu) / sigma)

    x_aug = np.column_stack([np.ones(len(x)), x])
    xp_aug = np.column_stack([np.ones(len(xp)), xp])
    penalty = np.eye(x_aug.shape[1]) * float(alpha)
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ y
    return xp_aug @ beta


def loocv_ridge(frame: pd.DataFrame, features: list[str], alpha: float) -> np.ndarray:
    y = frame["known_public"].to_numpy(dtype=np.float64)
    pred = np.zeros(len(frame), dtype=np.float64)
    for holdout in range(len(frame)):
        train = frame.drop(frame.index[holdout])
        pred_row = frame.iloc[[holdout]]
        pred[holdout] = fit_ridge_predict(
            train,
            train["known_public"].to_numpy(dtype=np.float64),
            pred_row,
            features,
            alpha,
        )[0]
    return pred


def metric_record(name: str, pred: np.ndarray, y: np.ndarray, kind: str, notes: str) -> dict[str, object]:
    err = pred - y
    return {
        "model": name,
        "kind": kind,
        "features": "",
        "alpha": np.nan,
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
        "max_abs_error": float(np.max(np.abs(err))),
        "bias_mean_pred_minus_public": float(np.mean(err)),
        "pairwise_rank_accuracy": pairwise_accuracy(pred, y),
        "spearman": float(pd.Series(pred).corr(pd.Series(y), method="spearman")),
        "kendall": float(pd.Series(pred).corr(pd.Series(y), method="kendall")),
        "notes": notes,
    }


def build_model_scores(known: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = known["known_public"].to_numpy(dtype=np.float64)
    records: list[dict[str, object]] = []
    pred_cols: dict[str, np.ndarray] = {}

    direct_models = [
        ("identity_actual_anchor", "actual_anchor_score_final", "independent_proxy", "raw actual-anchor score without fitting"),
        ("identity_mean_anchor", "mean_actual_anchor", "independent_proxy", "raw weighted anchor mean without fitting"),
        (
            "identity_posterior_in_sample",
            "posterior_expected_public_vs_anchor",
            "anchored_scenario_not_independent",
            "public-anchor scenario axis; included only to expose in-sample fit",
        ),
    ]
    for name, col, kind, notes in direct_models:
        pred = known[col].to_numpy(dtype=np.float64)
        pred_cols[name] = pred
        records.append(metric_record(name, pred, y, kind, notes) | {"features": col})

    model_defs = [
        ("loocv_ridge_actual_a1", ["actual_anchor_score_final"], 1.0),
        ("loocv_ridge_mean_a1", ["mean_actual_anchor"], 1.0),
        (
            "loocv_ridge_anchor_gap_a1",
            ["actual_anchor_score_final", "actual_minus_mean_anchor", "mean_abs_move_vs_raw05"],
            1.0,
        ),
        (
            "loocv_ridge_abs_axes_a1",
            ["abs_delta_vs_raw05_rawaxis", "abs_bad_residual_axis_ratio", "mean_abs_move_vs_raw05"],
            1.0,
        ),
        (
            "loocv_ridge_anchor_abs_axes_a1",
            [
                "actual_anchor_score_final",
                "abs_delta_vs_raw05_rawaxis",
                "abs_bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
            ],
            1.0,
        ),
        (
            "loocv_ridge_signed_axes_a1",
            ["delta_vs_raw05_rawaxis", "bad_residual_axis_ratio", "ordinal_axis_ratio", "mean_abs_move_vs_raw05"],
            1.0,
        ),
        (
            "loocv_ridge_public_shape_a1",
            [
                "actual_anchor_score_final",
                "abs_delta_vs_raw05_rawaxis",
                "abs_bad_residual_axis_ratio",
                "abs_ordinal_axis_ratio",
                "prob_span",
            ],
            1.0,
        ),
    ]
    for name, features, alpha in model_defs:
        pred = loocv_ridge(known, features, alpha)
        pred_cols[name] = pred
        rec = metric_record(
            name,
            pred,
            y,
            "leave_one_anchor_out",
            "public label of held-out submission is not used for that prediction",
        )
        rec["features"] = ",".join(features)
        rec["alpha"] = alpha
        records.append(rec)

    known_pred = known.copy()
    for name, pred in pred_cols.items():
        known_pred[name] = pred
        known_pred[f"{name}_error"] = pred - known_pred["known_public"]

    model_scores = pd.DataFrame(records).sort_values(["kind", "mae", "rmse"]).reset_index(drop=True)
    return model_scores, known_pred


def predict_candidates(known: pd.DataFrame, models: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    model_features = {
        "fit_actual_a1": (["actual_anchor_score_final"], 1.0, "loocv_ridge_actual_a1"),
        "fit_mean_a1": (["mean_actual_anchor"], 1.0, "loocv_ridge_mean_a1"),
        "fit_anchor_gap_a1": (
            ["actual_anchor_score_final", "actual_minus_mean_anchor", "mean_abs_move_vs_raw05"],
            1.0,
            "loocv_ridge_anchor_gap_a1",
        ),
        "fit_abs_axes_a1": (
            ["abs_delta_vs_raw05_rawaxis", "abs_bad_residual_axis_ratio", "mean_abs_move_vs_raw05"],
            1.0,
            "loocv_ridge_abs_axes_a1",
        ),
        "fit_anchor_abs_axes_a1": (
            [
                "actual_anchor_score_final",
                "abs_delta_vs_raw05_rawaxis",
                "abs_bad_residual_axis_ratio",
                "mean_abs_move_vs_raw05",
            ],
            1.0,
            "loocv_ridge_anchor_abs_axes_a1",
        ),
        "fit_signed_axes_a1": (
            ["delta_vs_raw05_rawaxis", "bad_residual_axis_ratio", "ordinal_axis_ratio", "mean_abs_move_vs_raw05"],
            1.0,
            "loocv_ridge_signed_axes_a1",
        ),
    }
    y = known["known_public"].to_numpy(dtype=np.float64)
    out = candidates.copy()
    pred_names: list[str] = []
    loocv_mae_by_model: dict[str, float] = {}
    for model_name, (features, alpha, loocv_name) in model_features.items():
        pred = fit_ridge_predict(known, y, out, features, alpha)
        out[model_name] = pred
        pred_names.append(model_name)
        match = models[models["model"].eq(loocv_name)]
        loocv_mae_by_model[model_name] = float(match["mae"].iloc[0]) if len(match) else float("nan")

    weights = np.array(
        [1.0 / max(loocv_mae_by_model[name], 1e-8) for name in pred_names],
        dtype=np.float64,
    )
    weights /= weights.sum()
    pred_mat = out[pred_names].to_numpy(dtype=np.float64)
    out["independent_lb_proxy_mean"] = pred_mat @ weights
    out["independent_lb_proxy_min_model"] = np.nanmin(pred_mat, axis=1)
    out["independent_lb_proxy_max_model"] = np.nanmax(pred_mat, axis=1)
    out["independent_lb_proxy_model_spread"] = (
        out["independent_lb_proxy_max_model"] - out["independent_lb_proxy_min_model"]
    )
    out["independent_lb_proxy_weighted_mae"] = float(np.sum(weights * np.array([loocv_mae_by_model[n] for n in pred_names])))
    out["independent_lb_proxy_conservative_low"] = (
        out["independent_lb_proxy_mean"] - out["independent_lb_proxy_weighted_mae"]
    )
    out["independent_lb_proxy_conservative_high"] = (
        out["independent_lb_proxy_mean"] + out["independent_lb_proxy_weighted_mae"]
    )
    raw05_row = out[out["file"].astype(str).eq(RAW05_FILE)]
    if len(raw05_row) == 1:
        raw05_row = raw05_row.iloc[0]
        rel_names: list[str] = []
        for name in pred_names:
            rel_name = f"{name}_raw05_relative_public"
            out[rel_name] = RAW05_PUBLIC + (out[name] - float(raw05_row[name]))
            rel_names.append(rel_name)
        rel_mat = out[rel_names].to_numpy(dtype=np.float64)
        out["raw05_relative_lb_proxy_mean"] = rel_mat @ weights
        out["raw05_relative_delta_vs_raw05_public"] = out["raw05_relative_lb_proxy_mean"] - RAW05_PUBLIC
        out["raw05_relative_lb_proxy_min_model"] = np.nanmin(rel_mat, axis=1)
        out["raw05_relative_lb_proxy_max_model"] = np.nanmax(rel_mat, axis=1)
        out["raw05_relative_lb_proxy_model_spread"] = (
            out["raw05_relative_lb_proxy_max_model"] - out["raw05_relative_lb_proxy_min_model"]
        )
        out["raw05_relative_conservative_low"] = (
            out["raw05_relative_lb_proxy_mean"] - out["independent_lb_proxy_weighted_mae"]
        )
        out["raw05_relative_conservative_high"] = (
            out["raw05_relative_lb_proxy_mean"] + out["independent_lb_proxy_weighted_mae"]
        )

        axis_names = [name for name in ["fit_abs_axes_a1", "fit_signed_axes_a1"] if name in pred_names]
        axis_weights = np.array(
            [1.0 / max(loocv_mae_by_model[name], 1e-8) for name in axis_names],
            dtype=np.float64,
        )
        axis_weights /= axis_weights.sum()
        axis_mat = out[axis_names].to_numpy(dtype=np.float64)
        out["axis_only_lb_proxy_mean"] = axis_mat @ axis_weights
        out["axis_only_lb_proxy_min_model"] = np.nanmin(axis_mat, axis=1)
        out["axis_only_lb_proxy_max_model"] = np.nanmax(axis_mat, axis=1)
        out["axis_only_lb_proxy_model_spread"] = (
            out["axis_only_lb_proxy_max_model"] - out["axis_only_lb_proxy_min_model"]
        )
        out["axis_only_lb_proxy_weighted_mae"] = float(
            np.sum(axis_weights * np.array([loocv_mae_by_model[n] for n in axis_names]))
        )
        axis_rel_names: list[str] = []
        for name in axis_names:
            rel_name = f"{name}_axis_raw05_relative_public"
            out[rel_name] = RAW05_PUBLIC + (out[name] - float(raw05_row[name]))
            axis_rel_names.append(rel_name)
        axis_rel_mat = out[axis_rel_names].to_numpy(dtype=np.float64)
        out["axis_only_raw05_relative_lb_proxy_mean"] = axis_rel_mat @ axis_weights
        out["axis_only_raw05_relative_delta_vs_raw05_public"] = (
            out["axis_only_raw05_relative_lb_proxy_mean"] - RAW05_PUBLIC
        )
        out["axis_only_raw05_relative_lb_proxy_min_model"] = np.nanmin(axis_rel_mat, axis=1)
        out["axis_only_raw05_relative_lb_proxy_max_model"] = np.nanmax(axis_rel_mat, axis=1)
        out["axis_only_raw05_relative_lb_proxy_model_spread"] = (
            out["axis_only_raw05_relative_lb_proxy_max_model"] - out["axis_only_raw05_relative_lb_proxy_min_model"]
        )
        missing_anchor_features = out["actual_anchor_score_final"].isna() | out["mean_actual_anchor"].isna()
        out["available_raw05_relative_lb_proxy_mean"] = np.where(
            missing_anchor_features,
            out["axis_only_raw05_relative_lb_proxy_mean"],
            out["raw05_relative_lb_proxy_mean"],
        )
        out["available_raw05_relative_delta_vs_raw05_public"] = (
            out["available_raw05_relative_lb_proxy_mean"] - RAW05_PUBLIC
        )
        out["available_raw05_relative_model_spread"] = np.where(
            missing_anchor_features,
            out["axis_only_raw05_relative_lb_proxy_model_spread"],
            out["raw05_relative_lb_proxy_model_spread"],
        )
        out["available_proxy_model_family"] = np.where(missing_anchor_features, "axis_only", "full")
    else:
        out["raw05_relative_lb_proxy_mean"] = np.nan
        out["raw05_relative_delta_vs_raw05_public"] = np.nan
        out["raw05_relative_lb_proxy_model_spread"] = np.nan
        out["raw05_relative_conservative_low"] = np.nan
        out["raw05_relative_conservative_high"] = np.nan
        out["axis_only_lb_proxy_mean"] = np.nan
        out["axis_only_raw05_relative_lb_proxy_mean"] = np.nan
        out["axis_only_raw05_relative_delta_vs_raw05_public"] = np.nan
        out["axis_only_raw05_relative_lb_proxy_model_spread"] = np.nan
        out["available_raw05_relative_lb_proxy_mean"] = np.nan
        out["available_raw05_relative_delta_vs_raw05_public"] = np.nan
        out["available_raw05_relative_model_spread"] = np.nan
        out["available_proxy_model_family"] = "missing_raw05"
    out["posterior_scenario_not_independent"] = out["posterior_expected_public_vs_anchor"]
    sort_cols = [
        "available_raw05_relative_lb_proxy_mean",
        "raw05_relative_lb_proxy_mean",
        "independent_lb_proxy_mean",
        "independent_lb_proxy_model_spread",
        "actual_anchor_score_final",
    ]
    return out.sort_values(sort_cols).reset_index(drop=True)


def load_known_and_candidates() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ranker = add_derived_features(pd.read_csv(RANKER))
    calibration = pd.read_csv(CALIBRATION)
    known_files = set(calibration["file"].astype(str))
    known = ranker[ranker["file"].astype(str).isin(known_files)].copy()
    known = known.sort_values("known_public").reset_index(drop=True)
    if len(known) != len(known_files):
        missing = sorted(known_files - set(known["file"].astype(str)))
        raise ValueError(f"missing known files in ranker scores: {missing}")

    candidate_frames = [pd.read_csv(PRIORITY)]
    for path in EXTRA_CANDIDATE_TABLES:
        if path.exists():
            candidate_frames.append(pd.read_csv(path))
    priority = add_derived_features(pd.concat(candidate_frames, ignore_index=True, sort=False))
    priority = priority[priority["file"].notna()].copy()
    priority = priority.drop_duplicates("file").reset_index(drop=True)
    return known, priority, ranker


def write_report(model_scores: pd.DataFrame, known_pred: pd.DataFrame, cand: pd.DataFrame) -> None:
    independent = model_scores[~model_scores["kind"].eq("anchored_scenario_not_independent")].copy()
    best = independent.sort_values("mae").iloc[0]
    posterior = model_scores[model_scores["model"].eq("identity_posterior_in_sample")].iloc[0]
    direct = model_scores[model_scores["model"].eq("identity_actual_anchor")].iloc[0]
    cand_non_raw = cand[~cand["file"].astype(str).eq(RAW05_FILE)].copy()
    top_rel = cand_non_raw.sort_values("available_raw05_relative_lb_proxy_mean").head(1).iloc[0]

    known_cols = [
        "file",
        "known_public",
        "actual_anchor_score_final",
        "identity_actual_anchor_error",
        "posterior_expected_public_vs_anchor",
        "identity_posterior_in_sample_error",
        "loocv_ridge_anchor_abs_axes_a1",
        "loocv_ridge_anchor_abs_axes_a1_error",
    ]
    cand_cols = [
        "rank",
        "file",
        "tier",
        "actual_anchor_score_final",
        "posterior_scenario_not_independent",
        "independent_lb_proxy_mean",
        "independent_lb_proxy_model_spread",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_model_spread",
        "axis_only_raw05_relative_lb_proxy_mean",
        "axis_only_raw05_relative_delta_vs_raw05_public",
        "axis_only_raw05_relative_lb_proxy_model_spread",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_proxy_model_family",
        "independent_lb_proxy_conservative_low",
        "independent_lb_proxy_conservative_high",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
    ]
    lines = [
        "# Local Public-LB Proxy Validation",
        "",
        "Known public submissions are used as anchors only for this validation. The posterior scenario column is not treated as an independent predictor because it is calibrated to the same known public points.",
        "",
        "## Model Scores",
        "",
        "```csv",
        model_scores.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Main Read",
        "",
        f"- Best independent LOOCV MAE: `{best['mae']:.10f}` from `{best['model']}`.",
        f"- Raw `actual_anchor_score_final` MAE against known public: `{direct['mae']:.10f}`.",
        f"- Posterior scenario in-sample MAE: `{posterior['mae']:.10f}`; this is an anchored reconstruction, not a submit-before-LB validation.",
        f"- Best raw05-relative candidate in this pass: `{top_rel['file']}` at `{top_rel['available_raw05_relative_lb_proxy_mean']:.10f}`, delta `{top_rel['available_raw05_relative_delta_vs_raw05_public']:.10f}` versus raw05 public `{RAW05_PUBLIC:.10f}` using `{top_rel['available_proxy_model_family']}`.",
        f"- That relative delta is much smaller than the best independent LOOCV MAE `{best['mae']:.10f}` and even the within-candidate model spread `{top_rel['available_raw05_relative_model_spread']:.10f}`.",
        f"- Practical resolution: candidate gaps below about `{max(best['mae'], direct['mae']):.10f}` should be treated as indistinguishable locally.",
        "",
        "## Known Anchor Predictions",
        "",
        "```csv",
        known_pred[known_cols].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Current Candidate LB Bands",
        "",
        "```csv",
        cand[cand_cols].head(24).round(10).to_csv(index=False).strip(),
        "```",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known, priority, _ = load_known_and_candidates()
    model_scores, known_pred = build_model_scores(known)
    candidate_pred = predict_candidates(known, model_scores, priority)

    known_pred.to_csv(KNOWN_OUT, index=False)
    model_scores.to_csv(MODEL_OUT, index=False)
    candidate_pred.to_csv(CAND_OUT, index=False)
    write_report(model_scores, known_pred, candidate_pred)

    print("[model_scores]")
    print(model_scores.round(10).to_string(index=False))
    print("\n[candidate_predictions_top12]")
    keep = [
        "rank",
        "file",
        "tier",
        "actual_anchor_score_final",
        "posterior_scenario_not_independent",
        "independent_lb_proxy_mean",
        "independent_lb_proxy_model_spread",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_model_spread",
        "axis_only_raw05_relative_lb_proxy_mean",
        "axis_only_raw05_relative_delta_vs_raw05_public",
        "axis_only_raw05_relative_lb_proxy_model_spread",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_proxy_model_family",
        "independent_lb_proxy_conservative_low",
        "independent_lb_proxy_conservative_high",
    ]
    print(candidate_pred[keep].head(12).round(10).to_string(index=False))
    print(f"\nwrote: {KNOWN_OUT}")
    print(f"wrote: {MODEL_OUT}")
    print(f"wrote: {CAND_OUT}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
