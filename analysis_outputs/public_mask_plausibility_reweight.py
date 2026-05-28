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

from public_subset_sensitivity_audit import build_masks, load_sub  # noqa: E402
from public_universe_minimax_optimizer import (  # noqa: E402
    BASELINE_PRIOR,
    CONSERVATIVE_Q,
    CORE_Q,
    MASK_Q,
    PROFILES as SCENARIO_PROFILES,
    TARGETS,
    KEY,
    ce_row_loss,
    weighted_quantile,
)


BASE_CANDIDATES = [
    BASELINE_PRIOR,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "submission_projblend_cap0p0.csv",
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
    "submission_public_minimaxens_r01_a6_h422045.csv",
    "submission_public_minimaxens_r05_a10_h506746.csv",
    "submission_public_maskaware_t80_r11_544844af.csv",
]

SELECTION_TABLES = [
    ("public_posterior_scenario_robustness_summary.csv", 96),
    ("public_minimax_ensemble_selected.csv", 16),
    ("public_universe_minimax_selected.csv", 32),
    ("public_entropy_targetmask_selected.csv", 48),
    ("public_maskaware_entropy_selected.csv", 32),
    ("public_conservative_frontier_selected.csv", 32),
    ("public_subset_sensitivity_summary.csv", 48),
    ("public_mask_plausibility_blend_selected.csv", 10),
]

MASK_FAMILY_PROFILES: dict[str, dict[str, float]] = {
    "mask_equal": {
        "global": -1.0,
        "rowmod": -1.0,
        "subject_order": -1.0,
        "subject_contig": -1.0,
        "random": -1.0,
        "single_subject": -1.0,
    },
    "diag_plaus_soft": {
        "global": 0.08,
        "rowmod": 0.15,
        "subject_order": 0.18,
        "subject_contig": 0.27,
        "random": 0.27,
        "single_subject": 0.05,
    },
    "diag_plaus_sharp": {
        "global": 0.06,
        "rowmod": 0.16,
        "subject_order": 0.19,
        "subject_contig": 0.30,
        "random": 0.25,
        "single_subject": 0.04,
    },
    "subject_heavy": {
        "global": 0.04,
        "rowmod": 0.08,
        "subject_order": 0.22,
        "subject_contig": 0.36,
        "random": 0.25,
        "single_subject": 0.05,
    },
    "random_heavy": {
        "global": 0.05,
        "rowmod": 0.16,
        "subject_order": 0.08,
        "subject_contig": 0.21,
        "random": 0.45,
        "single_subject": 0.05,
    },
    "no_global_no_single": {
        "global": 0.00,
        "rowmod": 0.17,
        "subject_order": 0.18,
        "subject_contig": 0.35,
        "random": 0.30,
        "single_subject": 0.00,
    },
}

SIGMA_BY_PROFILE = {
    "mask_equal": None,
    "diag_plaus_soft": 0.010,
    "diag_plaus_sharp": 0.0045,
    "subject_heavy": 0.0065,
    "random_heavy": 0.0065,
    "no_global_no_single": 0.0065,
}


def candidate_files() -> list[str]:
    files: list[str] = []
    for f in BASE_CANDIDATES:
        if (OUT / f).exists() and f not in files:
            files.append(f)
    for table_name, n in SELECTION_TABLES:
        path = OUT / table_name
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" not in df.columns:
            continue
        for f in df["file"].head(n).tolist():
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


def scenario_files() -> tuple[list[str], list[str]]:
    files: list[str] = []
    groups: list[str] = []
    for group, members in [("core", CORE_Q), ("mask", MASK_Q), ("conservative", CONSERVATIVE_Q)]:
        for f in members:
            if (OUT / f).exists() and f not in files:
                files.append(f)
                groups.append(group)
    return files, groups


def scenario_weight_vector(groups: list[str], profile: dict[str, float], mask_weights: np.ndarray) -> np.ndarray:
    counts = {g: groups.count(g) for g in sorted(set(groups))}
    weights: list[float] = []
    for g in groups:
        scenario_weight = profile[g] / max(1, counts[g])
        weights.extend((scenario_weight * mask_weights).tolist())
    out = np.asarray(weights, dtype=np.float64)
    return out / out.sum()


def canonical_mask_key(mask_kind: str, mask_name: str) -> tuple[str, str]:
    if mask_kind == "global_order":
        if mask_name.startswith("prefix_frac"):
            return "global", "prefix_" + mask_name.removeprefix("prefix_frac")
        if mask_name.startswith("suffix_frac"):
            return "global", "suffix_" + mask_name.removeprefix("suffix_frac")
        if mask_name.startswith("rowmod"):
            return "rowmod", "mod" + mask_name.removeprefix("rowmod")
    if mask_kind == "subject_order":
        if mask_name.startswith("per_subject_prefix_frac"):
            return "subject_order", "subj_prefix_" + mask_name.removeprefix("per_subject_prefix_frac")
        if mask_name.startswith("per_subject_suffix_frac"):
            return "subject_order", "subj_suffix_" + mask_name.removeprefix("per_subject_suffix_frac")
    if mask_kind == "subject_contiguous":
        frac_rep = mask_name.removeprefix("frac")
        frac, rep = frac_rep.split("_rep", 1)
        return "subject_contig", f"subj_contig_{frac}_{rep}"
    if mask_kind == "random_rows":
        frac_rep = mask_name.removeprefix("frac")
        frac, rep = frac_rep.split("_rep", 1)
        return "random", f"random_{frac}_{rep}"
    if mask_kind == "single_subject":
        return "single_subject", mask_name
    return mask_kind, mask_name


def mask_matrix_and_metadata(sample: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    records = [m for m in build_masks(sample) if m["mask_kind"] != "all"]
    mat = np.zeros((len(records), len(sample)), dtype=np.float64)
    rows = []
    for i, rec in enumerate(records):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
        family, diag_name = canonical_mask_key(str(rec["mask_kind"]), str(rec["mask_name"]))
        rows.append(
            {
                "mask_index": i,
                "mask_kind": rec["mask_kind"],
                "mask_name": rec["mask_name"],
                "rows": rec["rows"],
                "family": family,
                "diag_name": diag_name,
            }
        )
    return mat, pd.DataFrame(rows)


def load_diag_moves(mask_meta: pd.DataFrame) -> pd.DataFrame:
    path = OUT / "public_maskaware_projection_public_mask_diagnostics.csv"
    if not path.exists():
        out = mask_meta.copy()
        out["diag_mean_probability_move"] = np.nan
        return out

    diag = pd.read_csv(path)
    key_move = {
        (str(r.family), str(r.mask_name)): float(r.mean_probability_move)
        for r in diag.itertuples(index=False)
    }
    family_mean = diag.groupby("family")["mean_probability_move"].mean().to_dict()
    family_mean["single_subject"] = family_mean.get("subject_contig", diag["mean_probability_move"].mean())
    all_move = float(diag.loc[diag["family"] == "all", "mean_probability_move"].iloc[0])

    moves = []
    matched = []
    for row in mask_meta.itertuples(index=False):
        move = key_move.get((row.family, row.diag_name))
        if move is None:
            move = float(family_mean.get(row.family, all_move))
            matched.append(False)
        else:
            matched.append(True)
        moves.append(move)
    out = mask_meta.copy()
    out["diag_mean_probability_move"] = moves
    out["diag_exact_match"] = matched
    out["all_mean_probability_move"] = all_move
    return out


def make_mask_weights(mask_meta: pd.DataFrame, profile_name: str) -> np.ndarray:
    priors = MASK_FAMILY_PROFILES[profile_name]
    if profile_name == "mask_equal":
        w = np.ones(len(mask_meta), dtype=np.float64)
        return w / w.sum()

    all_move = float(mask_meta["all_mean_probability_move"].iloc[0])
    sigma = float(SIGMA_BY_PROFILE[profile_name])
    raw = np.zeros(len(mask_meta), dtype=np.float64)
    for family, prior in priors.items():
        idx = np.flatnonzero(mask_meta["family"].to_numpy() == family)
        if len(idx) == 0 or prior <= 0.0:
            continue
        moves = mask_meta.iloc[idx]["diag_mean_probability_move"].to_numpy(dtype=np.float64)
        plaus = np.exp(-0.5 * ((moves - all_move) / sigma) ** 2)
        plaus = np.maximum(plaus, 1e-4)
        plaus = plaus / plaus.sum()
        raw[idx] = prior * plaus
    raw = raw / raw.sum()
    return raw


def evaluate_scores(
    scores: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
    weights: np.ndarray,
) -> dict[str, float]:
    regret = scores - best_scores
    delta_prior = scores - prior_scores
    weighted_expected = float(np.sum(weights * scores))
    weighted_regret = float(np.sum(weights * regret))
    p90_expected = weighted_quantile(scores, weights, 0.90)
    p90_regret = weighted_quantile(regret, weights, 0.90)
    p95_regret = weighted_quantile(regret, weights, 0.95)
    max_regret = float(regret.max())
    weighted_delta_vs_prior = float(np.sum(weights * delta_prior))
    p90_delta_vs_prior = weighted_quantile(delta_prior, weights, 0.90)
    win_rate_vs_prior = float(np.sum(weights[delta_prior < 0.0]))
    score = (
        weighted_expected
        + 1.75 * weighted_regret
        + 0.85 * p90_regret
        + 0.25 * p95_regret
        + 0.04 * max_regret
        + 0.10 * max(p90_delta_vs_prior, 0.0)
        + 0.01 * max(0.80 - win_rate_vs_prior, 0.0)
    )
    return {
        "score": score,
        "weighted_expected": weighted_expected,
        "p90_expected": p90_expected,
        "weighted_regret": weighted_regret,
        "p90_regret": p90_regret,
        "p95_regret": p95_regret,
        "max_regret": max_regret,
        "weighted_delta_vs_prior": weighted_delta_vs_prior,
        "p90_delta_vs_prior": p90_delta_vs_prior,
        "win_rate_vs_prior": win_rate_vs_prior,
    }


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    files = candidate_files()
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

    mask_weight_rows = []
    profile_rows = []
    for mask_profile in MASK_FAMILY_PROFILES:
        mask_weights = make_mask_weights(mask_meta, mask_profile)
        weight_meta = mask_meta.copy()
        weight_meta["mask_profile"] = mask_profile
        weight_meta["mask_weight"] = mask_weights
        mask_weight_rows.extend(weight_meta.to_dict("records"))

        family_weights = weight_meta.groupby("family")["mask_weight"].sum().to_dict()
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
                        "scenario_weights": ";".join(f"{k}={v:.2f}" for k, v in scenario_profile_weights.items()),
                        "mask_family_weights": ";".join(f"{k}={family_weights.get(k, 0.0):.3f}" for k in sorted(MASK_FAMILY_PROFILES[mask_profile])),
                    }
                )
                rows.append(ev)
            block = pd.DataFrame(rows).sort_values(["score", "weighted_expected"]).reset_index(drop=True)
            block["rank"] = np.arange(1, len(block) + 1)
            profile_rows.extend(block.to_dict("records"))

    profile_scores = pd.DataFrame(profile_rows)
    profile_scores.to_csv(OUT / "public_mask_plausibility_reweight_profile_scores.csv", index=False)

    mask_weights_df = pd.DataFrame(mask_weight_rows)
    mask_weights_df.to_csv(OUT / "public_mask_plausibility_mask_weights.csv", index=False)

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
    summary.to_csv(OUT / "public_mask_plausibility_reweight_summary.csv", index=False)

    refs = [
        "submission_public_minimaxens_r05_a10_h506746.csv",
        "submission_public_minimaxens_r01_a6_h422045.csv",
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        BASELINE_PRIOR,
    ]
    reference = summary[summary["file"].isin(refs)]
    reference.to_csv(OUT / "public_mask_plausibility_reference_rows.csv", index=False)

    top_by_profile = (
        profile_scores.sort_values(["mask_profile", "scenario_profile", "rank"])
        .groupby(["mask_profile", "scenario_profile"])
        .head(5)
        .reset_index(drop=True)
    )
    top_by_profile.to_csv(OUT / "public_mask_plausibility_top_by_profile.csv", index=False)

    report = []
    report.append("# Public Mask Plausibility Reweight\n")
    report.append(
        "Re-ranks existing submissions by crossing posterior-scenario profiles with explicit public-mask plausibility priors. "
        "`mask_equal` reproduces the old equal-mask assumption; the other profiles downweight global prefix/suffix masks whose public projection requires much larger probability movement than the all-row solution.\n"
    )
    cols = [
        "file",
        "best_rank",
        "mean_rank",
        "worst_rank",
        "top1_count",
        "top3_count",
        "mean_score",
        "mean_weighted_expected",
        "mean_weighted_regret",
        "mean_delta_vs_prior",
    ]
    report.append("\n## Consensus Ranking\n")
    report.append("```\n" + summary[cols].head(24).round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Reference Rows\n")
    report.append("```\n" + reference[cols].round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Top Candidate Per Profile\n")
    top1 = top_by_profile[top_by_profile["rank"] == 1][
        ["mask_profile", "scenario_profile", "file", "score", "weighted_expected", "weighted_regret", "p90_regret"]
    ]
    report.append("```\n" + top1.round(9).to_string(index=False) + "\n```")
    (OUT / "public_mask_plausibility_report.md").write_text("".join(report))

    print("[mask plausibility consensus]")
    print(summary[cols].head(30).round(9).to_string(index=False))
    print("\n[reference rows]")
    print(reference[cols].round(9).to_string(index=False))
    print("\n[top1 per profile]")
    print(top1.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
