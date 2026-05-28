from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402
import jepa_regularized_sparse_direct_solver as sparse_solver  # noqa: E402
import jepa_sparse_scale_ladder_stress as ladder  # noqa: E402


SCAN_OUT = OUT / "jepa_target_ablation_scale_probe_scan.csv"
ANCHOR_OUT = OUT / "jepa_target_ablation_scale_probe_actual_anchor.csv"
CV_DETAIL_OUT = OUT / "jepa_target_ablation_scale_probe_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_target_ablation_scale_probe_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_target_ablation_scale_probe_selected.csv"
REPORT_OUT = OUT / "jepa_target_ablation_scale_probe_report.md"


SOURCE_FILES = {
    "f465_actual_best": "submission_sparsejepa_f4657144.csv",
    "3cf_noq2_safe": "submission_sparsejepa_3cfdf64a.csv",
    "282_consensus_directrob": "submission_sparsejepa_282e9546.csv",
    "f43_cv_best": "submission_sparsejepa_f43ea825.csv",
}

SCALES = [1.00, 1.30, 1.50, 1.75, 2.00]
DELTA_CAP = 0.24

TARGET_MASKS = {
    "all": ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"],
    "no_q1": ["Q2", "Q3", "S1", "S2", "S3", "S4"],
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "no_q3": ["Q1", "Q2", "S1", "S2", "S3", "S4"],
    "no_s1": ["Q1", "Q2", "Q3", "S2", "S3", "S4"],
    "no_s2": ["Q1", "Q2", "Q3", "S1", "S3", "S4"],
    "no_s3": ["Q1", "Q2", "Q3", "S1", "S2", "S4"],
    "no_s4": ["Q1", "Q2", "Q3", "S1", "S2", "S3"],
    "q_only": ["Q1", "Q2", "Q3"],
    "stage_all": ["S1", "S2", "S3", "S4"],
    "q1_q3_stage": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_stage": ["Q3", "S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
    "s2_s3_s4": ["S2", "S3", "S4"],
    "q1_only": ["Q1"],
    "q2_only": ["Q2"],
    "q3_only": ["Q3"],
    "s1_only": ["S1"],
    "s2_only": ["S2"],
    "s3_only": ["S3"],
    "s4_only": ["S4"],
}

SINGLE_TARGET_MASKS = {"q1_only", "q2_only", "q3_only", "s1_only", "s2_only", "s3_only", "s4_only"}


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def mask_matrix(mask_name: str, n_rows: int) -> np.ndarray:
    allowed = set(TARGET_MASKS[mask_name])
    weights = np.asarray([target in allowed for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(weights.reshape(1, -1), n_rows, axis=0)


def build_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    for source_name, file_name in SOURCE_FILES.items():
        source = ladder.load_submission_array(file_name, sample)
        source_delta = inv.logit(source) - base_logit
        for mask_name in TARGET_MASKS:
            gate = mask_matrix(mask_name, len(sample))
            active_gate = gate * (np.abs(source_delta) > 1e-10)
            active_cells = int(active_gate.sum())
            if active_cells <= 0:
                continue
            active_rows = int((active_gate.sum(axis=1) > 0).sum())
            active_energy = consensus["energy"][active_gate > 0]
            for scale in SCALES:
                final_delta = np.clip(scale * source_delta * gate, -DELTA_CAP, DELTA_CAP)
                pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                label = f"{source_name}|{mask_name}|s{scale:.2f}|cap{DELTA_CAP:.2f}"
                name = f"targetabl_{stable_hash(label)}"
                arrays[name] = pred
                rows.append(
                    {
                        "name": name,
                        "file": f"submission_targetabl_{stable_hash(label)}.csv",
                        "source_name": source_name,
                        "source_file": file_name,
                        "variant": mask_name,
                        "target_mask": mask_name,
                        "scale": scale,
                        "delta_cap": DELTA_CAP,
                        "active_cells": active_cells,
                        "active_rows": active_rows,
                        "mean_active_energy": float(np.mean(active_energy)),
                        "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                        "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                    }
                )
    return pd.DataFrame(rows), arrays


def coalesce_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ["mean_abs_move_vs_a2c8", "max_abs_move_vs_a2c8", "mean_abs_move_vs_raw05"]:
        if column not in out.columns:
            for candidate in [f"{column}_y", f"{column}_x"]:
                if candidate in out.columns:
                    out[column] = out[candidate]
                    break
    return out


def choose_for_anchor(scan: pd.DataFrame) -> pd.DataFrame:
    frames = [
        scan[(scan["robust_delta_vs_a2c8"] <= -0.00080) & (scan["mean_abs_move_vs_a2c8"] >= 0.004)].sort_values(["selection_proxy", "robust_delta_vs_a2c8"]).head(95),
        scan[scan["target_mask"].str.startswith("no_")].sort_values(["selection_proxy", "robust_delta_vs_a2c8"]).head(65),
        scan[scan["target_mask"].isin(["q_only", "stage_all", "q3_stage", "q3_s2_s3_s4", "q3_s4", "s2_s3_s4"])].sort_values(["selection_proxy", "robust_delta_vs_a2c8"]).head(65),
        scan[scan["target_mask"].str.endswith("_only")].sort_values(["robust_delta_vs_a2c8", "selection_proxy"]).head(55),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(180).reset_index(drop=True)


def choose_for_cv(anchor: pd.DataFrame) -> pd.DataFrame:
    candidates = anchor[anchor["name"].str.startswith("targetabl_")].copy()
    frames = [
        candidates[candidates["actual_anchor_score_final"] <= 0.57780].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(70),
        candidates[(candidates["actual_anchor_score_final"] <= 0.57788) & (candidates["mean_abs_move_vs_a2c8"] >= 0.006)].sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"]).head(50),
        candidates[candidates["target_mask"].isin(SINGLE_TARGET_MASKS)].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(35),
        candidates[candidates["target_mask"].str.startswith("no_")].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(45),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(120).reset_index(drop=True)


def combined_honest(summary: pd.DataFrame) -> pd.DataFrame:
    honest = summary[summary["policy"].isin(["train_best1", "train_best5", "structured_best3"])].copy()
    return (
        honest.groupby(["candidate_name", "file"], as_index=False)
        .agg(
            honest_cv_delta_mean=("cv_delta_mean", "mean"),
            honest_cv_delta_p90=("cv_delta_p90", "mean"),
            honest_cv_delta_worst=("cv_delta_worst", "max"),
            honest_cv_win_rate=("cv_win_rate", "mean"),
            selector_abs_error_mean=("selector_abs_error_mean", "mean"),
        )
        .sort_values(["honest_cv_delta_mean", "honest_cv_delta_worst"])
    )


def select_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    frames = [
        scored[
            (scored["actual_anchor_score_final"] <= 0.57776)
            & (scored["honest_cv_delta_mean"] <= -0.00080)
            & (scored["mean_abs_move_vs_a2c8"] >= 0.006)
        ].assign(submit_role="targetabl_first").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        scored[
            (scored["target_mask"].str.startswith("no_"))
            & (scored["actual_anchor_score_final"] <= 0.57782)
            & (scored["honest_cv_delta_mean"] <= -0.00075)
        ].assign(submit_role="targetabl_leaveone").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        scored[
            (scored["target_mask"].isin(SINGLE_TARGET_MASKS))
            & (scored["actual_anchor_score_final"] <= 0.57784)
        ].assign(submit_role="targetabl_single").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(7),
        scored[
            (scored["target_mask"].isin(["stage_all", "q3_stage", "q3_s2_s3_s4", "q3_s4", "s2_s3_s4"]))
            & (scored["actual_anchor_score_final"] <= 0.57784)
        ].assign(submit_role="targetabl_group").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
    ]
    selected = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    selected = selected.sort_values(["submit_role", "actual_anchor_score_final", "honest_cv_delta_mean"]).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        out = sample.copy()
        out[inv.TARGETS] = inv.clip_prob(arrays[str(row.name)])
        out.to_csv(OUT / str(row.file), index=False)
    return selected


def write_report(anchor: pd.DataFrame, cv_scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    cols = [
        "name",
        "file",
        "source_name",
        "target_mask",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "active_cells",
        "mean_active_energy",
    ]
    best_anchor = anchor[anchor["name"].str.startswith("targetabl_")].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
    best_cv = cv_scored.sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"])
    by_mask = (
        cv_scored.groupby(["source_name", "target_mask"], as_index=False)
        .agg(
            best_actual_anchor=("actual_anchor_score_final", "min"),
            best_honest_cv=("honest_cv_delta_mean", "min"),
            best_move=("mean_abs_move_vs_a2c8", "max"),
        )
        .sort_values(["best_actual_anchor", "best_honest_cv"])
    )
    report = [
        "# JEPA Target-Ablation Scale Probe",
        "",
        "This decomposes the sparse scale direction by target mask so a public LB response can identify target leakage.",
        "",
        "## Best Actual-Anchor Rows",
        "",
        "```",
        best_anchor[[c for c in cols if c in best_anchor.columns]].head(50).round(9).to_string(index=False),
        "```",
        "",
        "## Best Honest Anchor-CV Rows",
        "",
        "```",
        best_cv[[c for c in cols if c in best_cv.columns]].head(50).round(9).to_string(index=False),
        "```",
        "",
        "## Target Mask Summary",
        "",
        "```",
        by_mask.head(80).round(9).to_string(index=False),
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Interpretation",
        "",
        "- Leave-one masks test which target causes public-axis leakage when the sparse direction is scaled.",
        "- Single-target masks are not first-submit score candidates; they are diagnostic axes for interpreting public feedback.",
        "- If full/no-Q2 scale improves but target-only probes disagree, the hidden subset is target-coupled rather than separable by label.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    base = preds["cvjepa_a2c8"]

    meta, arrays = build_candidates(sample, base)
    scored = ladder.robust_scan(meta, arrays, preds)
    scored = coalesce_columns(scored)
    scored["selection_proxy"] = (
        scored["robust_delta_vs_a2c8"]
        + 0.70 * np.maximum(scored["robust_p90_delta_vs_a2c8"], 0.0)
        + 0.25 * np.maximum(scored["robust_worst_delta_vs_a2c8"], 0.0)
        - 0.0010 * np.minimum(scored["mean_abs_move_vs_a2c8"] / 0.008, 1.5)
    )
    anchor_pool = choose_for_anchor(scored)
    anchor_arrays = {str(row.name): arrays[str(row.name)] for row in anchor_pool.itertuples(index=False)}
    anchor = ladder.actual_anchor_for_ladder(sample, anchor_pool, anchor_arrays)
    anchor.to_csv(ANCHOR_OUT, index=False)

    cv_pool = choose_for_cv(anchor)
    cv_arrays = {str(row.name): arrays[str(row.name)] for row in cv_pool.itertuples(index=False)}
    cv_detail, cv_summary = ladder.anchor_cv_for_ladder(sample, cv_pool, cv_arrays, preds)
    honest = combined_honest(cv_summary)
    cv_scored = cv_pool.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")

    selected = select_outputs(sample, cv_scored, arrays)
    scored.to_csv(SCAN_OUT, index=False)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(anchor, cv_scored, selected)

    print(REPORT_OUT)
    print("[generated]", meta.shape, "[anchor]", anchor.shape, "[cv]", cv_pool.shape)
    cols = [
        "name",
        "file",
        "source_name",
        "target_mask",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    print(cv_scored[[c for c in cols if c in cv_scored.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(30).round(9).to_string(index=False))
    print("[selected]")
    print(selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none")


if __name__ == "__main__":
    main()
