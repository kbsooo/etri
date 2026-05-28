from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import KEY, TARGETS, logit  # noqa: E402
from raw05_anchor_jepa_micro_injection import locate, read_submission  # noqa: E402


RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
MOTIF_FILE = "submission_raw05_jepa_axisbridge_45f2ba5a.csv"
RAW05_PUBLIC = 0.5775263072

CALIBRATION = OUT / "public_lb_actual_anchor_ranker_calibration.csv"
LOCAL_PROXY = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
PRIORITY = OUT / "final_jepa_candidate_priority_20260527.csv"

OUT_FEATURES = OUT / "local_lb_structural_features.csv"
OUT_MODELS = OUT / "local_lb_structural_feature_model_scores.csv"
OUT_CAND = OUT / "local_lb_structural_candidate_predictions.csv"
OUT_CONSTRAINED = OUT / "local_lb_structural_constrained_shortlist.csv"
OUT_REPORT = OUT / "local_lb_structural_feature_probe_report.md"

GROUPS = {
    "all": TARGETS,
    "q": ["Q1", "Q2", "Q3"],
    "s": ["S1", "S2", "S3", "S4"],
    "q3s4": ["Q3", "S4"],
    "q3": ["Q3"],
    "s4": ["S4"],
    "ctx": ["Q1", "Q2", "S1", "S2", "S3"],
}


MODEL_DEFS = [
    (
        "struct_stage_position_a10",
        ["raw05_stage2_blend_pos"],
        10.0,
        "where the submission sits on the observed raw05->stage2 logit line",
    ),
    (
        "struct_distance_a10",
        ["all_mae_raw05", "stage2_mae"],
        10.0,
        "global logit distance from raw05 and stage2",
    ),
    (
        "struct_axis_shape_a10",
        ["all_mae_raw05", "sv1_frac", "rank_entropy"],
        10.0,
        "global movement size plus residual anisotropy",
    ),
    (
        "struct_q3s4_motif_a10",
        ["q3s4_motif_proj", "q3s4_motif_orth_ratio"],
        10.0,
        "projection onto the discovered Q3/S4 motif and off-motif residual",
    ),
    (
        "struct_q3s4_balance_a10",
        ["q3s4_to_ctx_ratio_capped", "q3s4_rough_ratio"],
        10.0,
        "target/context concentration and sequence roughness of the Q3/S4 move",
    ),
    (
        "struct_compact_jepa_a10",
        ["raw05_stage2_blend_pos", "sv1_frac", "q3s4_motif_cos"],
        10.0,
        "compact JEPA-style structural descriptor: anchor line, collapse, motif direction",
    ),
]


def candidate_tables() -> list[Path]:
    return [
        PRIORITY,
        LOCAL_PROXY,
        OUT / "raw05_jepa_lowbad_motif_search_shortlist.csv",
        OUT / "raw05_jepa_direct_constrained_search_shortlist.csv",
        OUT / "raw05_jepa_axislocal_posterior_sweep_shortlist.csv",
        OUT / "raw05_jepa_anchorrobust_motif_graft_shortlist.csv",
        OUT / "raw05_jepa_structural_constrained_refine_shortlist.csv",
        OUT / "raw05_jepa_axisrepair_tradeoff_direct_shortlist.csv",
        OUT / "raw05_jepa_axisrepair_tradeoff_direct_scored.csv",
        OUT / "raw05_jepa_axisbridge_posterior_repair_shortlist.csv",
        OUT / "raw05_jepa_axisbudget_motif_bridge_shortlist.csv",
        OUT / "raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv",
        OUT / "raw05_jepa_sigreg_gated_microrefine_shortlist.csv",
        OUT / "raw05_jepa_energyfront_microrefine_shortlist.csv",
        OUT / "raw05_jepa_energy_constrained_frontier_shortlist.csv",
    ]


def existing_file_names() -> list[str]:
    names: list[str] = [
        RAW05_FILE,
        STAGE2_FILE,
        "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "submission_jepa_latent_q2_w0p45.csv",
        "submission_jepa_latent_residual_probe.csv",
    ]
    for path in candidate_tables():
        if not path.exists():
            continue
        frame = pd.read_csv(path, usecols=lambda c: c == "file")
        if "file" in frame.columns:
            names.extend(frame["file"].dropna().astype(str).tolist())

    out: list[str] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        try:
            locate(name)
        except FileNotFoundError:
            continue
        seen.add(name)
        out.append(name)
    return out


def align_submission(file_name: str, ref_key: pd.DataFrame) -> pd.DataFrame:
    frame = read_submission(file_name)
    if not frame[KEY].reset_index(drop=True).equals(ref_key.reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return frame


def sequence_roughness(sample: pd.DataFrame, values: np.ndarray) -> float:
    frame = sample[KEY].copy()
    frame["_value"] = values
    rough: list[float] = []
    for _sid, group in frame.sort_values(["subject_id", "sleep_date"]).groupby("subject_id", sort=False):
        diff = np.diff(group["_value"].to_numpy(dtype=np.float64))
        if len(diff):
            rough.append(float(np.mean(np.abs(diff))))
    return float(np.mean(rough)) if rough else 0.0


def residual_features(
    file_name: str,
    sample: pd.DataFrame,
    raw05_logit: np.ndarray,
    stage2_logit: np.ndarray,
    motif_logit_delta: np.ndarray,
) -> dict[str, object]:
    frame = align_submission(file_name, sample[KEY])
    pred_logit = logit(frame[TARGETS].to_numpy(dtype=np.float64))
    delta = pred_logit - raw05_logit
    delta_stage2 = pred_logit - stage2_logit

    row: dict[str, object] = {"file": file_name}
    target_index = {target: i for i, target in enumerate(TARGETS)}

    for group_name, targets in GROUPS.items():
        cols = [target_index[target] for target in targets]
        group_delta = delta[:, cols]
        group_motif = motif_logit_delta[:, cols]

        mae = float(np.mean(np.abs(group_delta)))
        rms = float(np.sqrt(np.mean(group_delta * group_delta)))
        signed = float(np.mean(group_delta))
        rough = sequence_roughness(sample, np.mean(np.abs(group_delta), axis=1))

        motif_denom = float(np.sum(group_motif * group_motif))
        if motif_denom > 1e-12:
            motif_proj = float(np.sum(group_delta * group_motif) / motif_denom)
            motif_norm = float(np.sqrt(np.sum(group_delta * group_delta)) * np.sqrt(motif_denom))
            motif_cos = float(np.sum(group_delta * group_motif) / max(motif_norm, 1e-12))
            motif_orth = float(
                np.sqrt(np.mean((group_delta - motif_proj * group_motif) ** 2))
            )
        else:
            motif_proj = 0.0
            motif_cos = 0.0
            motif_orth = 0.0

        row[f"{group_name}_mae_raw05"] = mae
        row[f"{group_name}_rms_raw05"] = rms
        row[f"{group_name}_signed_raw05"] = signed
        row[f"{group_name}_rough"] = rough
        row[f"{group_name}_rough_ratio"] = rough / max(mae, 1e-12)
        row[f"{group_name}_motif_proj"] = motif_proj
        row[f"{group_name}_motif_cos"] = motif_cos
        row[f"{group_name}_motif_orth"] = motif_orth
        row[f"{group_name}_motif_orth_ratio"] = motif_orth / max(mae, 1e-12)

    row["stage2_mae"] = float(np.mean(np.abs(delta_stage2)))
    stage_direction = stage2_logit - raw05_logit
    row["raw05_stage2_blend_pos"] = float(
        np.sum(delta * stage_direction) / max(np.sum(stage_direction * stage_direction), 1e-12)
    )
    row["q3s4_to_ctx_ratio"] = float(
        row["q3s4_mae_raw05"] / max(row["ctx_mae_raw05"], 1e-12)
    )
    row["q3s4_to_ctx_ratio_capped"] = float(
        min(row["q3s4_mae_raw05"] / max(row["ctx_mae_raw05"], 1e-4), 25.0)
    )
    row["q3s4_to_all_ratio"] = float(
        row["q3s4_mae_raw05"] / max(row["all_mae_raw05"], 1e-12)
    )
    row["target_context_signed_gap"] = float(row["q3s4_signed_raw05"] - row["ctx_signed_raw05"])

    centered = delta - delta.mean(axis=0, keepdims=True)
    singular = np.linalg.svd(centered, compute_uv=False)
    energy = singular * singular
    energy = energy / max(float(np.sum(energy)), 1e-12)
    row["sv1_frac"] = float(energy[0]) if len(energy) else 0.0
    row["rank_entropy"] = float(-np.sum(energy * np.log(energy + 1e-12))) if len(energy) else 0.0
    row["row_l2_mean"] = float(np.mean(np.sqrt(np.sum(delta * delta, axis=1))))
    row["row_l2_p95_ratio"] = float(
        np.quantile(np.sqrt(np.sum(delta * delta, axis=1)), 0.95) / max(row["row_l2_mean"], 1e-12)
    )
    row["min_prob_struct"] = float(frame[TARGETS].min().min())
    row["max_prob_struct"] = float(frame[TARGETS].max().max())
    return row


def fit_ridge_predict(
    train: pd.DataFrame,
    pred: pd.DataFrame,
    features: list[str],
    alpha: float,
) -> np.ndarray:
    y = train["known_public"].to_numpy(dtype=np.float64)
    x = train[features].to_numpy(dtype=np.float64)
    xp = pred[features].to_numpy(dtype=np.float64)
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


def pairwise_accuracy(pred: np.ndarray, y: np.ndarray) -> float:
    ok = 0
    total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            if abs(pred[i] - pred[j]) < 1e-15 or abs(y[i] - y[j]) < 1e-15:
                continue
            total += 1
            ok += int((pred[i] - pred[j]) * (y[i] - y[j]) > 0.0)
    return float(ok / total) if total else float("nan")


def loocv_model(known: pd.DataFrame, features: list[str], alpha: float) -> np.ndarray:
    pred = np.zeros(len(known), dtype=np.float64)
    for holdout in range(len(known)):
        train = known.drop(known.index[holdout])
        row = known.iloc[[holdout]]
        pred[holdout] = fit_ridge_predict(train, row, features, alpha)[0]
    return pred


def model_scores(known: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = known["known_public"].to_numpy(dtype=np.float64)
    rows: list[dict[str, object]] = []
    known_pred = known[["file", "known_public"]].copy()

    for name, features, alpha, notes in MODEL_DEFS:
        pred = loocv_model(known, features, alpha)
        err = pred - y
        known_pred[name] = pred
        known_pred[f"{name}_error"] = err
        rows.append(
            {
                "model": name,
                "features": ",".join(features),
                "alpha": alpha,
                "mae": float(np.mean(np.abs(err))),
                "rmse": float(np.sqrt(np.mean(err * err))),
                "max_abs_error": float(np.max(np.abs(err))),
                "bias_mean_pred_minus_public": float(np.mean(err)),
                "pairwise_rank_accuracy": pairwise_accuracy(pred, y),
                "spearman": float(pd.Series(pred).corr(pd.Series(y), method="spearman")),
                "kendall": float(pd.Series(pred).corr(pd.Series(y), method="kendall")),
                "notes": notes,
            }
        )

    return pd.DataFrame(rows).sort_values(["mae", "rmse"]).reset_index(drop=True), known_pred


def predict_candidates(
    known: pd.DataFrame,
    features: pd.DataFrame,
    scores: pd.DataFrame,
) -> pd.DataFrame:
    out = features.copy()
    pred_cols: list[str] = []
    mae_by_model: dict[str, float] = {}
    usable_scores = scores[
        scores["mae"].le(0.00125)
        & scores["pairwise_rank_accuracy"].ge(0.40)
    ].copy()
    usable_names = set(usable_scores["model"].astype(str))
    if not usable_names:
        usable_names = {str(scores.sort_values("mae").iloc[0]["model"])}

    for name, feature_csv, alpha, _notes in MODEL_DEFS:
        feature_list = feature_csv
        out[name] = fit_ridge_predict(known, out, feature_list, alpha)
        if name not in usable_names:
            continue
        pred_cols.append(name)
        mae_by_model[name] = float(scores.loc[scores["model"].eq(name), "mae"].iloc[0])

    raw05_row = out[out["file"].eq(RAW05_FILE)]
    if len(raw05_row) != 1:
        raise RuntimeError("raw05 row missing from structural feature table")
    raw05_row = raw05_row.iloc[0]

    weights = np.asarray([1.0 / max(mae_by_model[name], 1e-8) for name in pred_cols], dtype=np.float64)
    weights /= weights.sum()
    pred_mat = out[pred_cols].to_numpy(dtype=np.float64)
    out["structural_lb_proxy_mean"] = pred_mat @ weights
    out["structural_lb_proxy_min_model"] = np.nanmin(pred_mat, axis=1)
    out["structural_lb_proxy_max_model"] = np.nanmax(pred_mat, axis=1)
    out["structural_lb_proxy_model_spread"] = (
        out["structural_lb_proxy_max_model"] - out["structural_lb_proxy_min_model"]
    )
    out["structural_lb_proxy_weighted_mae"] = float(
        np.sum(weights * np.asarray([mae_by_model[name] for name in pred_cols], dtype=np.float64))
    )

    rel_cols: list[str] = []
    for name in pred_cols:
        rel_name = f"{name}_raw05_relative"
        out[rel_name] = RAW05_PUBLIC + (out[name] - float(raw05_row[name]))
        rel_cols.append(rel_name)
    rel_mat = out[rel_cols].to_numpy(dtype=np.float64)
    out["structural_raw05_relative_lb_proxy_mean"] = rel_mat @ weights
    out["structural_raw05_relative_delta_vs_raw05_public"] = (
        out["structural_raw05_relative_lb_proxy_mean"] - RAW05_PUBLIC
    )
    out["structural_raw05_relative_min_model"] = np.nanmin(rel_mat, axis=1)
    out["structural_raw05_relative_max_model"] = np.nanmax(rel_mat, axis=1)
    out["structural_raw05_relative_model_spread"] = (
        out["structural_raw05_relative_max_model"] - out["structural_raw05_relative_min_model"]
    )
    return out.sort_values(
        [
            "structural_raw05_relative_lb_proxy_mean",
            "structural_raw05_relative_model_spread",
            "file",
        ]
    ).reset_index(drop=True)


def structural_constrained_shortlist(candidates: pd.DataFrame) -> pd.DataFrame:
    local = pd.read_csv(LOCAL_PROXY) if LOCAL_PROXY.exists() else pd.DataFrame()
    if local.empty:
        return pd.DataFrame()
    merge_cols = [
        col
        for col in [
            "file",
            "rank",
            "tier",
            "actual_anchor_score_final",
            "posterior_expected_public_vs_anchor",
            "delta_vs_raw05_rawaxis",
            "bad_residual_axis_ratio",
            "available_raw05_relative_delta_vs_raw05_public",
            "lejepa_residual_health",
            "lejepa_combined_rank",
            "target_motif_retention",
        ]
        if col in local.columns
    ]
    merged = candidates.merge(local[merge_cols].drop_duplicates("file"), on="file", how="left")
    mask = (
        merged["file"].astype(str).str.contains("structrefine|axistrade|axisrepair|axisbridge", regex=True, na=False)
        & merged["q3s4_motif_cos"].ge(0.9999)
        & merged["q3s4_motif_orth_ratio"].le(0.01)
        & merged["posterior_expected_public_vs_anchor"].le(0.576905)
        & merged["delta_vs_raw05_rawaxis"].le(1.0e-7)
        & merged["bad_residual_axis_ratio"].abs().le(0.00012)
    )
    return merged[mask].sort_values(
        [
            "available_raw05_relative_delta_vs_raw05_public",
            "structural_raw05_relative_delta_vs_raw05_public",
            "structural_raw05_relative_model_spread",
        ]
    ).reset_index(drop=True)


def write_report(
    scores: pd.DataFrame,
    known_pred: pd.DataFrame,
    candidates: pd.DataFrame,
    constrained: pd.DataFrame,
) -> None:
    selected_files = [
        RAW05_FILE,
        "submission_raw05_jepa_structrefine_04ad10f8.csv",
        "submission_raw05_jepa_structrefine_90e28f7d.csv",
        "submission_raw05_jepa_axistrade_80fd659c.csv",
        "submission_raw05_jepa_axistrade_931a03a1.csv",
        "submission_raw05_jepa_axisrepair_2a20d67f.csv",
        "submission_raw05_jepa_axisrepair_78029f2c.csv",
        "submission_raw05_jepa_siganchor_3644a42f.csv",
        "submission_raw05_jepa_siggate_fd0e9622.csv",
    ]
    selected = candidates[candidates["file"].isin(selected_files)].copy()
    local = pd.read_csv(LOCAL_PROXY) if LOCAL_PROXY.exists() else pd.DataFrame()
    if not local.empty:
        merge_cols = [
            col
            for col in [
                "file",
                "rank",
                "tier",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "available_raw05_relative_delta_vs_raw05_public",
            ]
            if col in local.columns
        ]
        selected = selected.merge(local[merge_cols].drop_duplicates("file"), on="file", how="left")

    model_cols = [
        "model",
        "mae",
        "rmse",
        "max_abs_error",
        "pairwise_rank_accuracy",
        "features",
        "notes",
    ]
    known_cols = [
        "file",
        "known_public",
        "struct_stage_position_a10",
        "struct_axis_shape_a10",
        "struct_q3s4_motif_a10",
        "struct_compact_jepa_a10",
    ]
    cand_cols = [
        "file",
        "rank",
        "tier",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "available_raw05_relative_delta_vs_raw05_public",
        "structural_raw05_relative_delta_vs_raw05_public",
        "structural_raw05_relative_model_spread",
        "q3s4_motif_proj",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "q3s4_to_ctx_ratio",
        "q3s4_to_ctx_ratio_capped",
        "sv1_frac",
        "rank_entropy",
    ]
    top_cols = [
        "file",
        "structural_raw05_relative_lb_proxy_mean",
        "structural_raw05_relative_delta_vs_raw05_public",
        "structural_raw05_relative_model_spread",
        "q3s4_motif_proj",
        "q3s4_motif_cos",
        "sv1_frac",
        "rank_entropy",
    ]
    constrained_cols = [
        "file",
        "rank",
        "tier",
        "available_raw05_relative_delta_vs_raw05_public",
        "structural_raw05_relative_delta_vs_raw05_public",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "target_motif_retention",
        "q3s4_motif_proj",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "lejepa_residual_health",
        "lejepa_combined_rank",
    ]
    best = scores.iloc[0]
    lines = [
        "# Local LB Structural Feature Probe",
        "",
        "This probe recomputes submission-level logit residual features directly from CSV files. It is designed as a diagnostic guardrail, not a replacement for the anchored public-LB proxy, because only six public anchors are available.",
        "",
        "## Model Scores",
        "",
        "```csv",
        scores[model_cols].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Main Read",
        "",
        f"- Best structural LOOCV MAE: `{best['mae']:.10f}` from `{best['model']}`.",
        "- Compare this against the current best public-anchor local proxy MAE `0.0003184931`; a worse structural MAE means the feature should be used only as a diagnostic/risk descriptor.",
        "- The structural models deliberately use compact feature sets and ridge `alpha=10` to avoid fitting arbitrary combinations to six anchors.",
        "",
        "## Known Anchor Predictions",
        "",
        "```csv",
        known_pred[known_cols].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Selected Candidate Diagnostics",
        "",
        "```csv",
        selected[[col for col in cand_cols if col in selected.columns]].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Structural Top Candidates",
        "",
        "```csv",
        candidates[top_cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Structural Constraint Hit List",
        "",
        "Filter: family in structrefine/axistrade/axisrepair/axisbridge, `q3s4_motif_cos >= 0.9999`, `q3s4_motif_orth_ratio <= 0.01`, posterior `<= 0.576905`, raw-axis `<= 1e-7`, and `abs(bad-axis) <= 0.00012`.",
        "",
        "```csv",
        constrained[[col for col in constrained_cols if col in constrained.columns]]
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = read_submission(RAW05_FILE)
    raw05_logit = logit(sample[TARGETS].to_numpy(dtype=np.float64))
    stage2 = align_submission(STAGE2_FILE, sample[KEY])
    stage2_logit = logit(stage2[TARGETS].to_numpy(dtype=np.float64))
    motif = align_submission(MOTIF_FILE, sample[KEY])
    motif_logit_delta = logit(motif[TARGETS].to_numpy(dtype=np.float64)) - raw05_logit

    files = existing_file_names()
    rows = [
        residual_features(file_name, sample, raw05_logit, stage2_logit, motif_logit_delta)
        for file_name in files
    ]
    features = pd.DataFrame(rows)
    calibration = pd.read_csv(CALIBRATION)[["file", "known_public"]]
    features = features.merge(calibration, on="file", how="left")

    known = features[features["known_public"].notna()].copy().reset_index(drop=True)
    scores, known_pred = model_scores(known)
    cand = predict_candidates(known, features, scores)
    constrained = structural_constrained_shortlist(cand)

    features.to_csv(OUT_FEATURES, index=False)
    scores.to_csv(OUT_MODELS, index=False)
    cand.to_csv(OUT_CAND, index=False)
    constrained.to_csv(OUT_CONSTRAINED, index=False)
    write_report(scores, known_pred, cand, constrained)

    print("[structural_model_scores]")
    print(scores.round(10).to_string(index=False))
    print("\n[selected_candidates]")
    selected = [
        RAW05_FILE,
        "submission_raw05_jepa_structrefine_04ad10f8.csv",
        "submission_raw05_jepa_structrefine_90e28f7d.csv",
        "submission_raw05_jepa_axistrade_80fd659c.csv",
        "submission_raw05_jepa_axistrade_931a03a1.csv",
        "submission_raw05_jepa_axisrepair_2a20d67f.csv",
        "submission_raw05_jepa_axisrepair_78029f2c.csv",
        "submission_raw05_jepa_siganchor_3644a42f.csv",
        "submission_raw05_jepa_siggate_fd0e9622.csv",
    ]
    keep = [
        "file",
        "structural_raw05_relative_delta_vs_raw05_public",
        "structural_raw05_relative_model_spread",
        "q3s4_motif_proj",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "q3s4_to_ctx_ratio",
        "q3s4_to_ctx_ratio_capped",
        "sv1_frac",
    ]
    print(cand[cand["file"].isin(selected)][keep].round(10).to_string(index=False))
    print(f"\nwrote: {OUT_FEATURES}")
    print(f"wrote: {OUT_MODELS}")
    print(f"wrote: {OUT_CAND}")
    print(f"wrote: {OUT_CONSTRAINED}")
    print(f"wrote: {OUT_REPORT}")


if __name__ == "__main__":
    main()
