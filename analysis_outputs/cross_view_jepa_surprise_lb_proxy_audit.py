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

import local_lb_proxy_validation as lbv  # noqa: E402
import public_lb_actual_anchor_ranker as ranker  # noqa: E402
from hidden_block_latent_audit import KEY, TARGETS, clip  # noqa: E402


RAW05_PUBLIC = 0.5775263072
STAGE2_PUBLIC = 0.5779449757

CVJEPA_FILES = [
    "submission_cvjepa_surprise_full_nonq2.csv",
    "submission_cvjepa_surprise_full_nonq2_w030.csv",
    "submission_cvjepa_surprise_core_q1_q3_s2_s4.csv",
    "submission_cvjepa_surprise_s_targets.csv",
    "submission_cvjepa_surprise_full_nonq2_w020.csv",
    "submission_cvjepa_surprise_q1_s2.csv",
    "submission_cvjepa_surprise_q_targets.csv",
]

CONTROL_FILES = [
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "submission_jepa_latent_residual_probe.csv",
    "submission_jepa_latent_q2_w0p45.csv",
]


def load_sample() -> pd.DataFrame:
    return (
        pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
        .sort_values(KEY)
        .reset_index(drop=True)
    )


def candidate_frame() -> pd.DataFrame:
    rows = []
    for rank, file_name in enumerate(CONTROL_FILES, start=1):
        rows.append({"file": file_name, "source": "known_control", "source_rank": rank})
    for rank, file_name in enumerate(CVJEPA_FILES, start=1):
        rows.append({"file": file_name, "source": "cvjepa_surprise", "source_rank": rank})
    out = pd.DataFrame(rows)
    missing = [f for f in out["file"].astype(str) if not ranker.exists(f)]
    if missing:
        raise FileNotFoundError(f"missing submissions: {missing}")
    return out


def score_ranker_candidates(candidates: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    masks = ranker.mask_matrix(sample)
    score_frames = []
    detail_frames = []
    for set_name, table in ranker.COMBO_TABLES.items():
        combo_path = OUT / table
        if not combo_path.exists():
            continue
        combo_df = pd.read_csv(combo_path)
        if combo_df.empty:
            continue
        scores, detail = ranker.score_combo_set(set_name, combo_df, candidates, sample, masks)
        score_frames.append(scores)
        detail_frames.append(detail)

    all_scores = pd.concat(score_frames, ignore_index=True)
    all_scores.to_csv(OUT / "cross_view_jepa_surprise_lb_proxy_by_set.csv", index=False)
    pd.concat(detail_frames, ignore_index=True).to_csv(OUT / "cross_view_jepa_surprise_lb_proxy_detail.csv", index=False)

    pivot = all_scores.pivot_table(
        index="file",
        columns="combo_set",
        values=["actual_anchor_score", "actual_anchor_mean", "actual_anchor_std"],
        aggfunc="first",
    )
    pivot.columns = ["__".join(col).strip() for col in pivot.columns.to_flat_index()]
    pivot = pivot.reset_index()
    merged = candidates.merge(pivot, on="file", how="left")

    score_cols = [c for c in merged.columns if c.startswith("actual_anchor_score__")]
    mean_cols = [c for c in merged.columns if c.startswith("actual_anchor_mean__")]
    merged["actual_anchor_score_final"] = merged[score_cols].mean(axis=1)
    merged["mean_actual_anchor"] = merged[mean_cols].mean(axis=1)
    merged["min_set_score"] = merged[score_cols].min(axis=1)
    merged["max_set_score"] = merged[score_cols].max(axis=1)

    axes = ranker.public_axes()
    axis_rows = []
    for row in merged.itertuples(index=False):
        pred = ranker.load_submission(str(row.file), sample)
        rec = {"file": row.file}
        rec.update(ranker.public_axis_features(pred, axes))
        axis_rows.append(rec)
    axis_df = pd.DataFrame(axis_rows)
    merged = merged.merge(axis_df, on="file", how="left")
    return merged, all_scores


def proxy_predict(ranker_scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    known, _, _ = lbv.load_known_and_candidates()
    model_scores, _ = lbv.build_model_scores(known)
    cand = lbv.add_derived_features(ranker_scores)
    pred = lbv.predict_candidates(known, model_scores, cand)
    pred["known_public"] = pred["file"].map(ranker.KNOWN_PUBLIC)
    return pred, model_scores


def target_movement(sample: pd.DataFrame, files: list[str]) -> pd.DataFrame:
    stage2 = ranker.load_submission("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", sample)
    raw05 = ranker.load_submission("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", sample)
    rows = []
    for file_name in files:
        pred = ranker.load_submission(file_name, sample)
        for j, target in enumerate(TARGETS):
            d_stage2 = pred[:, j] - stage2[:, j]
            d_raw05 = pred[:, j] - raw05[:, j]
            rows.append(
                {
                    "file": file_name,
                    "target": target,
                    "mean_delta_vs_stage2": float(d_stage2.mean()),
                    "mean_abs_delta_vs_stage2": float(np.abs(d_stage2).mean()),
                    "p95_abs_delta_vs_stage2": float(np.quantile(np.abs(d_stage2), 0.95)),
                    "mean_delta_vs_raw05": float(d_raw05.mean()),
                    "mean_abs_delta_vs_raw05": float(np.abs(d_raw05).mean()),
                    "p95_abs_delta_vs_raw05": float(np.quantile(np.abs(d_raw05), 0.95)),
                    "corr_vs_stage2": float(np.corrcoef(pred[:, j], stage2[:, j])[0, 1]),
                    "corr_vs_raw05": float(np.corrcoef(pred[:, j], raw05[:, j])[0, 1]),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "cross_view_jepa_surprise_lb_proxy_target_movement.csv", index=False)
    return out


def write_report(audit: pd.DataFrame, movement: pd.DataFrame, model_scores: pd.DataFrame) -> None:
    best_independent = (
        model_scores[~model_scores["kind"].eq("anchored_scenario_not_independent")]
        .sort_values("mae")
        .iloc[0]
    )
    cv = audit[audit["source"].eq("cvjepa_surprise")].copy()
    controls = audit[audit["source"].eq("known_control")].copy()
    keep = [
        "file",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "independent_lb_proxy_mean",
        "independent_lb_proxy_model_spread",
    ]
    ranked = cv.sort_values("available_raw05_relative_lb_proxy_mean")
    move_summary = (
        movement[movement["file"].isin(CVJEPA_FILES)]
        .groupby("file", as_index=False)
        .agg(
            mean_target_abs_move_vs_stage2=("mean_abs_delta_vs_stage2", "mean"),
            max_target_abs_move_vs_stage2=("mean_abs_delta_vs_stage2", "max"),
            mean_target_abs_move_vs_raw05=("mean_abs_delta_vs_raw05", "mean"),
            max_target_abs_move_vs_raw05=("mean_abs_delta_vs_raw05", "max"),
        )
        .sort_values("mean_target_abs_move_vs_raw05")
    )
    known_keep = [
        "file",
        "actual_anchor_score_final",
        "known_public",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
    ]
    if "known_public" not in controls.columns:
        controls["known_public"] = controls["file"].map(ranker.KNOWN_PUBLIC)

    lines = [
        "# Cross-View JEPA Surprise Local LB Proxy Audit",
        "",
        "This audits the new cross-view JEPA surprise submissions with the existing public-anchor ranker and LOOCV local LB proxy.",
        "",
        "## Proxy Resolution",
        "",
        f"- Best independent LOOCV proxy model: `{best_independent['model']}`.",
        f"- MAE/RMSE: `{best_independent['mae']:.10f}` / `{best_independent['rmse']:.10f}`.",
        "- Candidate gaps materially below this are not locally resolvable.",
        "",
        "## CVJEPA Candidates",
        "",
        "```csv",
        ranked[keep].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Movement Summary",
        "",
        "```csv",
        move_summary.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Known Controls",
        "",
        "```csv",
        controls[known_keep].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Read",
        "",
        "- These candidates are locally strong on OOF/subject-half/geometry, but their submission-space movement is much closer to stage2 than raw05.",
        "- The proxy therefore treats them as stage2-family structural probes, not raw05-compatible LB-safe replacements.",
        "- Use the proxy ranking as a risk screen; public LB is still needed to know whether this new JEPA signal transfers.",
    ]
    (OUT / "cross_view_jepa_surprise_lb_proxy_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sample()
    candidates = candidate_frame()
    ranker_scores, _ = score_ranker_candidates(candidates, sample)
    audit, model_scores = proxy_predict(ranker_scores)
    audit.to_csv(OUT / "cross_view_jepa_surprise_lb_proxy_audit.csv", index=False)
    movement = target_movement(sample, CVJEPA_FILES)
    write_report(audit, movement, model_scores)

    cols = [
        "file",
        "actual_anchor_score_final",
        "raw_axis_expected_public_vs_stage2",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
    ]
    print("[cvjepa local-lb proxy]")
    print(
        audit[audit["source"].eq("cvjepa_surprise")]
        .sort_values("available_raw05_relative_lb_proxy_mean")[cols]
        .round(10)
        .to_string(index=False)
    )
    print("wrote:", OUT / "cross_view_jepa_surprise_lb_proxy_audit.csv")
    print("wrote:", OUT / "cross_view_jepa_surprise_lb_proxy_report.md")


if __name__ == "__main__":
    main()
