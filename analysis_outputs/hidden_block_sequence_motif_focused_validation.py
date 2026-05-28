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
from public_posterior_scenario_robustness import Q_SCENARIOS  # noqa: E402
from public_mask_plausibility_reweight import (  # noqa: E402
    BASE_CANDIDATES as MASK_BASE_CANDIDATES,
    BASELINE_PRIOR,
    MASK_FAMILY_PROFILES,
    SCENARIO_PROFILES,
    TARGETS,
    KEY,
    ce_row_loss,
    evaluate_scores,
    load_diag_moves,
    make_mask_weights,
    mask_matrix_and_metadata,
    scenario_files,
    scenario_weight_vector,
)


EXPLICIT_REFS = [
    BASELINE_PRIOR,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "submission_hiddenblock_paretomix_w0.3_b7621063.csv",
    "submission_hiddenblock_paretomix_w0.4_0fcefee9.csv",
    "submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv",
    "submission_hiddenblock_rateprobe_neutral_95ebba6c.csv",
    "submission_hiddenblock_rateprobe_neutral_605de284.csv",
    "submission_hiddenblock_seqmotif_neutral_ebf79910.csv",
    "submission_hiddenblock_seqmotif_neutral_1501e8f9.csv",
    "submission_hiddenblock_seqmotif_neutral_d0ca7647.csv",
]


def add_file(files: list[str], name: str) -> None:
    if name and (OUT / name).exists() and name not in files:
        files.append(name)


def add_from_table(files: list[str], table: str, n: int, sort_cols: list[str] | None = None) -> None:
    path = OUT / table
    if not path.exists():
        return
    df = pd.read_csv(path)
    if "file" not in df.columns:
        return
    if sort_cols:
        existing_cols = [c for c in sort_cols if c in df.columns]
        if existing_cols:
            df = df.sort_values(existing_cols)
    for name in df["file"].head(n).tolist():
        add_file(files, str(name))


def candidate_files() -> list[str]:
    files: list[str] = []
    for name in MASK_BASE_CANDIDATES + EXPLICIT_REFS:
        add_file(files, name)

    add_from_table(files, "public_mask_plausibility_reweight_summary.csv", 96, ["mean_rank", "worst_rank"])
    add_from_table(files, "public_posterior_scenario_robustness_summary.csv", 96, ["scenario_robust_score"])
    add_from_table(files, "hidden_block_sequence_motif_shortlist.csv", 120, ["posterior_expected_public_vs_anchor"])
    add_from_table(
        files,
        "hidden_block_sequence_motif_cellgate_safe_scores.csv",
        220,
        ["posterior_expected_public_vs_anchor", "delta_vs_raw05_rawaxis"],
    )
    add_from_table(
        files,
        "hidden_block_sequence_motif_cellgate_safe_scores.csv",
        120,
        ["gated_posterior_delta", "delta_vs_raw05_rawaxis"],
    )
    add_from_table(
        files,
        "hidden_block_sequence_motif_cellgate_safe_scores.csv",
        120,
        ["delta_vs_raw05_rawaxis", "posterior_expected_public_vs_anchor"],
    )

    return files


def scenario_summary(files: list[str]) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    masks = [m for m in build_masks(sample) if m["mask_kind"] != "all"]
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
                        "expected_loss": score,
                        "regret_vs_best": score - best_score,
                        "delta_vs_prior": score - prior_score,
                    }
                )

    detail = pd.DataFrame(rows)
    summary = (
        detail.groupby("file")
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
        + summary["p90_regret"]
        + 0.25 * summary["p95_regret"]
        + 0.10 * np.maximum(summary["p90_delta_vs_prior"], 0.0)
        + 0.01 * np.maximum(0.80 - summary["win_rate_vs_prior"], 0.0)
    )
    summary = summary.sort_values(["scenario_robust_score", "mean_expected"]).reset_index(drop=True)
    summary.to_csv(OUT / "hidden_block_sequence_motif_focused_scenario_summary.csv", index=False)
    return summary


def mask_summary(files: list[str]) -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    q_files, q_groups = scenario_files()
    mask_mat, mask_meta = mask_matrix_and_metadata(sample)
    mask_meta = load_diag_moves(mask_meta)

    preds = {f: load_sub(f)[TARGETS].to_numpy(dtype=float) for f in files}
    prior_pred = load_sub(BASELINE_PRIOR)[TARGETS].to_numpy(dtype=float)
    q_scenarios = [load_sub(f)[TARGETS].to_numpy(dtype=float) for f in q_files]

    score_by_file = {f: [] for f in files}
    prior_scores_parts = []
    for q in q_scenarios:
        scenario_scores = []
        for f in files:
            scores = mask_mat @ ce_row_loss(q, preds[f])
            score_by_file[f].append(scores)
            scenario_scores.append(scores)
        prior_scores_parts.append(mask_mat @ ce_row_loss(q, prior_pred))
    file_scores = {f: np.concatenate(parts) for f, parts in score_by_file.items()}
    best_scores = np.vstack([file_scores[f] for f in files]).min(axis=0)
    prior_scores = np.concatenate(prior_scores_parts)

    profile_rows = []
    for mask_profile in MASK_FAMILY_PROFILES:
        mask_weights = make_mask_weights(mask_meta, mask_profile)
        family_weights = mask_meta.assign(mask_weight=mask_weights).groupby("family")["mask_weight"].sum().to_dict()
        for scenario_profile, scenario_profile_weights in SCENARIO_PROFILES.items():
            metric_weights = scenario_weight_vector(q_groups, scenario_profile_weights, mask_weights)
            rows = []
            for f in files:
                ev = evaluate_scores(file_scores[f], best_scores, prior_scores, metric_weights)
                ev.update(
                    {
                        "file": f,
                        "mask_profile": mask_profile,
                        "scenario_profile": scenario_profile,
                        "mask_family_weights": ";".join(
                            f"{k}={family_weights.get(k, 0.0):.3f}" for k in sorted(MASK_FAMILY_PROFILES[mask_profile])
                        ),
                    }
                )
                rows.append(ev)
            block = pd.DataFrame(rows).sort_values(["score", "weighted_expected"]).reset_index(drop=True)
            block["rank"] = np.arange(1, len(block) + 1)
            profile_rows.extend(block.to_dict("records"))

    profile_scores = pd.DataFrame(profile_rows)
    profile_scores.to_csv(OUT / "hidden_block_sequence_motif_focused_mask_profile_scores.csv", index=False)
    summary = (
        profile_scores.groupby("file")
        .agg(
            profile_count=("rank", "count"),
            best_rank=("rank", "min"),
            mean_rank=("rank", "mean"),
            worst_rank=("rank", "max"),
            top1_count=("rank", lambda s: int((s == 1).sum())),
            top3_count=("rank", lambda s: int((s <= 3).sum())),
            top10_count=("rank", lambda s: int((s <= 10).sum())),
            mean_score=("score", "mean"),
            worst_score=("score", "max"),
            mean_weighted_expected=("weighted_expected", "mean"),
            mean_weighted_regret=("weighted_regret", "mean"),
            mean_p90_regret=("p90_regret", "mean"),
            worst_max_regret=("max_regret", "max"),
            mean_delta_vs_prior=("weighted_delta_vs_prior", "mean"),
            min_win_rate_vs_prior=("win_rate_vs_prior", "min"),
        )
        .reset_index()
        .sort_values(["mean_rank", "worst_rank", "mean_score"])
        .reset_index(drop=True)
    )
    summary.to_csv(OUT / "hidden_block_sequence_motif_focused_mask_summary.csv", index=False)
    return summary


def main() -> None:
    files = candidate_files()
    pd.DataFrame({"file": files}).to_csv(OUT / "hidden_block_sequence_motif_focused_candidates.csv", index=False)
    print(f"[focused] candidates {len(files)}")

    scen = scenario_summary(files)
    mask = mask_summary(files)

    merged = scen.merge(mask, on="file", how="left", suffixes=("_scenario", "_mask"))
    merged["is_seqmotif_neutral"] = merged["file"].str.contains("seqmotif_neutral")
    merged["is_seqmotif_cellgate"] = merged["file"].str.contains("seqmotif_cellgate")
    merged["is_known_ref"] = merged["file"].isin(EXPLICIT_REFS)
    merged = merged.sort_values(["scenario_robust_score", "mean_rank", "mean_expected"]).reset_index(drop=True)
    merged.to_csv(OUT / "hidden_block_sequence_motif_focused_combined.csv", index=False)

    cols = [
        "file",
        "scenario_robust_score",
        "mean_expected",
        "mean_regret",
        "mean_rank",
        "worst_rank",
        "top3_count",
        "is_seqmotif_neutral",
        "is_seqmotif_cellgate",
    ]
    print("[focused scenario top]")
    print(scen[["file", "scenario_robust_score", "mean_expected", "mean_regret"]].head(20).round(9).to_string(index=False))
    print("\n[focused mask top]")
    print(mask[["file", "mean_rank", "worst_rank", "top3_count", "mean_score"]].head(20).round(9).to_string(index=False))
    print("\n[focused combined top]")
    print(merged[cols].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
