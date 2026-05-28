from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from public_subset_sensitivity_audit import build_masks, ce_matrix, load_sub, row_score  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]

Q_SCENARIOS = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]
BASELINE_PRIOR = "submission_public2dblend_budget0p0.csv"
BASE_CANDIDATES = [
    BASELINE_PRIOR,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_projblend_cap0p0.csv",
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]


def candidate_files() -> list[str]:
    files = []
    for f in BASE_CANDIDATES:
        if (OUT / f).exists() and f not in files:
            files.append(f)
    selected_path = OUT / "public_entropy_targetmask_selected.csv"
    if selected_path.exists():
        for f in pd.read_csv(selected_path)["file"].tolist()[:24]:
            if (OUT / f).exists() and f not in files:
                files.append(f)
    ensemble_path = OUT / "public_minimax_ensemble_selected.csv"
    if ensemble_path.exists():
        for f in pd.read_csv(ensemble_path)["file"].tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    conservative_path = OUT / "public_conservative_frontier_selected.csv"
    if conservative_path.exists():
        for f in pd.read_csv(conservative_path)["file"].tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    maskaware_path = OUT / "public_maskaware_entropy_selected.csv"
    if maskaware_path.exists():
        for f in pd.read_csv(maskaware_path)["file"].tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    universe_path = OUT / "public_universe_minimax_selected.csv"
    if universe_path.exists():
        for f in pd.read_csv(universe_path)["file"].tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    maskplaus_path = OUT / "public_mask_plausibility_blend_selected.csv"
    if maskplaus_path.exists():
        for f in pd.read_csv(maskplaus_path)["file"].tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
    for path in sorted(OUT.glob("submission_rhythm_*.csv")):
        if path.name not in files:
            files.append(path.name)
    for path in sorted(OUT.glob("submission_mp_*.csv")):
        if path.name not in files:
            files.append(path.name)
    for path in sorted(OUT.glob("submission_q2_stage2safe_*.csv")):
        if path.name not in files:
            files.append(path.name)
    for path in sorted(OUT.glob("submission_q2_publicsafe_blend_*.csv")):
        if path.name not in files:
            files.append(path.name)
    for path in sorted(OUT.glob("submission_hiddenblock_*.csv")):
        if path.name not in files:
            files.append(path.name)
    return files


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    masks = build_masks(sample)
    files = candidate_files()
    pred = {f: load_sub(f)[TARGETS].to_numpy(dtype=float) for f in files}
    prior_pred = load_sub(BASELINE_PRIOR)[TARGETS].to_numpy(dtype=float)

    rows = []
    for q_file in Q_SCENARIOS:
        if not (OUT / q_file).exists():
            continue
        q = load_sub(q_file)[TARGETS].to_numpy(dtype=float)
        loss_by_file = {f: ce_matrix(q, p) for f, p in pred.items()}
        prior_loss = ce_matrix(q, prior_pred)
        for mask_rec in masks:
            mask = mask_rec["mask"]
            assert isinstance(mask, np.ndarray)
            prior_score = row_score(prior_loss, mask)
            scores = {f: row_score(loss, mask) for f, loss in loss_by_file.items()}
            best_score = min(scores.values())
            for f, score in scores.items():
                rows.append(
                    {
                        "q_scenario": q_file,
                        "file": f,
                        "mask_kind": mask_rec["mask_kind"],
                        "mask_name": mask_rec["mask_name"],
                        "rows": mask_rec["rows"],
                        "expected_loss": score,
                        "best_loss_for_scenario_mask": best_score,
                        "regret_vs_best": score - best_score,
                        "delta_vs_prior": score - prior_score,
                    }
                )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT / "public_posterior_scenario_robustness_detail.csv", index=False)

    eval_detail = detail[detail["mask_kind"] != "all"].copy()
    summary = (
        eval_detail.groupby("file")
        .agg(
            scenarios=("q_scenario", "nunique"),
            masks=("mask_name", "count"),
            mean_expected=("expected_loss", "mean"),
            p90_expected=("expected_loss", lambda s: float(s.quantile(0.90))),
            mean_regret=("regret_vs_best", "mean"),
            p90_regret=("regret_vs_best", lambda s: float(s.quantile(0.90))),
            p95_regret=("regret_vs_best", lambda s: float(s.quantile(0.95))),
            max_regret=("regret_vs_best", "max"),
            mean_delta_vs_prior=("delta_vs_prior", "mean"),
            p90_delta_vs_prior=("delta_vs_prior", lambda s: float(s.quantile(0.90))),
            win_rate_vs_prior=("delta_vs_prior", lambda s: float((s < 0).mean())),
        )
        .reset_index()
    )
    summary["scenario_robust_score"] = (
        summary["mean_expected"]
        + 2.0 * summary["mean_regret"]
        + 1.0 * summary["p90_regret"]
        + 0.25 * summary["p95_regret"]
        + 0.10 * np.maximum(summary["p90_delta_vs_prior"], 0.0)
        + 0.01 * np.maximum(0.80 - summary["win_rate_vs_prior"], 0.0)
    )
    summary = summary.sort_values(["scenario_robust_score", "mean_expected"]).reset_index(drop=True)
    summary.to_csv(OUT / "public_posterior_scenario_robustness_summary.csv", index=False)

    per_scenario = (
        eval_detail.groupby(["q_scenario", "file"])
        .agg(
            mean_expected=("expected_loss", "mean"),
            mean_regret=("regret_vs_best", "mean"),
            p90_regret=("regret_vs_best", lambda s: float(s.quantile(0.90))),
            win_rate_vs_prior=("delta_vs_prior", lambda s: float((s < 0).mean())),
        )
        .reset_index()
    )
    per_scenario.to_csv(OUT / "public_posterior_scenario_robustness_by_scenario.csv", index=False)

    report = []
    report.append("# Public Posterior Scenario Robustness\n")
    report.append(
        "This audit avoids scoring every candidate against only one posterior. It uses multiple public-constraint posterior scenarios and ranks candidates by subset regret.\n"
    )
    cols = [
        "file",
        "mean_expected",
        "mean_regret",
        "p90_regret",
        "p95_regret",
        "mean_delta_vs_prior",
        "p90_delta_vs_prior",
        "win_rate_vs_prior",
        "scenario_robust_score",
    ]
    report.append("\n## Top Scenario-Robust Candidates\n")
    report.append("```\n" + summary[cols].head(24).round(9).to_string(index=False) + "\n```")
    (OUT / "public_posterior_scenario_robustness_report.md").write_text("".join(report))

    print("[scenario robustness summary]")
    print(summary[cols].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
