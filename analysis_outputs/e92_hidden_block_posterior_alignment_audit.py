#!/usr/bin/env python3
"""E92 hidden-block posterior alignment audit.

E91 rejects known-public movement regression as a post-mixmin selector. This
audit asks a different question: do E86/E90/E89 differ in how their
mixmin-relative movement aligns with the hidden-block posterior geometry that
was built before the E72 public miss?
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import TARGETS, KEY, clip, logit, sample_block_ids  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCORES_OUT = OUT / "e92_hidden_block_posterior_alignment_scores.csv"
BLOCK_DETAIL_OUT = OUT / "e92_hidden_block_posterior_alignment_block_detail.csv"
REPORT_OUT = OUT / "e92_hidden_block_posterior_alignment_report.md"

TARGET_GROUPS = {
    "all": TARGETS,
    "Q": ["Q1", "Q2", "Q3"],
    "S": ["S1", "S2", "S3", "S4"],
    "Q2S3": ["Q2", "S3"],
    "S123": ["S1", "S2", "S3"],
}

CANDIDATES = [
    ("frontier", "submission_mixmin_0c916bb4.csv"),
    ("failed_e72", "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"),
    ("conservative_e85", "submission_e85_inverse_conflict_pruned_58b23ed1.csv"),
    ("max_upside_e86", "submission_e86_e85_consensus_a3f7c96f.csv"),
    ("noq2_contrast", "submission_e87_noq2_source_consensus_a85c4e39.csv"),
    ("balanced_e90", "submission_e90_e72pareto_28925de5.csv"),
    ("min_contam_e89", "submission_e89_e72decontam_00d7807f.csv"),
]


def bce(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64)
    p = clip(p)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def target_idx(names: list[str]) -> list[int]:
    return [TARGETS.index(name) for name in names]


def ce_delta(q: np.ndarray, candidate: np.ndarray, base: np.ndarray, names: list[str]) -> float:
    idx = target_idx(names)
    return float(np.mean(bce(q[:, idx], candidate[:, idx]) - bce(q[:, idx], base[:, idx])))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 1.0e-18:
        return 0.0
    return float(np.dot(aa, bb) / denom)


def mass_agreement(delta: np.ndarray, direction: np.ndarray, eps: float = 1.0e-6) -> float:
    d = np.asarray(delta, dtype=np.float64)
    r = np.asarray(direction, dtype=np.float64)
    mask = np.abs(r) > eps
    if not np.any(mask):
        return 0.0
    mass = np.abs(d[mask])
    denom = float(mass.sum())
    if denom <= 1.0e-18:
        return 0.0
    return float(mass[(d[mask] * r[mask]) > 0.0].sum() / denom)


def block_target_r2(delta: np.ndarray, block_ids: np.ndarray) -> float:
    values: list[float] = []
    groups: list[str] = []
    for row_idx, block_id in enumerate(block_ids):
        for target_idx_, target in enumerate(TARGETS):
            values.append(float(delta[row_idx, target_idx_]))
            groups.append(f"{block_id}__{target}")
    frame = pd.DataFrame({"value": values, "group": groups})
    x = frame["value"].to_numpy(dtype=np.float64)
    total = float(np.sum((x - x.mean()) ** 2))
    if total <= 1.0e-18:
        return 0.0
    grouped = frame.groupby("group", sort=False)["value"]
    between = float(sum(len(v) * (float(v.mean()) - float(x.mean())) ** 2 for _, v in grouped))
    return between / total


def movement_mass_stats(delta: np.ndarray, block_ids: np.ndarray, block_meta: pd.DataFrame) -> dict[str, float]:
    mass_by_block = pd.DataFrame(
        {
            "hidden_block_id": block_ids,
            "row_mass": np.abs(delta).sum(axis=1),
        }
    ).groupby("hidden_block_id", sort=False)["row_mass"].sum()
    total_mass = float(mass_by_block.sum())
    if total_mass <= 1.0e-18:
        return {
            "movement_entropy_norm": 0.0,
            "top5_block_mass_frac": 0.0,
            "blocks_for_80pct_mass": 0.0,
            "posterior_shift_topquartile_mass_lift": 0.0,
        }

    probs = (mass_by_block / total_mass).to_numpy(dtype=np.float64)
    entropy = -float(np.sum(probs * np.log(np.clip(probs, 1.0e-18, 1.0))))
    entropy_norm = entropy / np.log(max(len(probs), 2))
    sorted_mass = np.sort(probs)[::-1]
    blocks_for_80 = int(np.searchsorted(np.cumsum(sorted_mass), 0.80, side="left") + 1)
    top5 = float(sorted_mass[:5].sum())

    meta = block_meta.set_index("hidden_block_id")
    q75 = float(meta["posterior_mean_abs_shift"].quantile(0.75))
    top_shift_blocks = set(meta[meta["posterior_mean_abs_shift"] >= q75].index.astype(str))
    mass_top_shift = float(mass_by_block[mass_by_block.index.astype(str).isin(top_shift_blocks)].sum() / total_mass)
    row_frac_top_shift = float((pd.Series(block_ids).astype(str).isin(top_shift_blocks)).mean())
    lift = mass_top_shift / max(row_frac_top_shift, 1.0e-12)
    return {
        "movement_entropy_norm": entropy_norm,
        "top5_block_mass_frac": top5,
        "blocks_for_80pct_mass": float(blocks_for_80),
        "posterior_shift_topquartile_mass_lift": lift,
    }


def block_detail(
    role: str,
    file_name: str,
    candidate: np.ndarray,
    base: np.ndarray,
    posterior: np.ndarray,
    block_ids: np.ndarray,
    block_meta: pd.DataFrame,
) -> pd.DataFrame:
    delta = logit(candidate) - logit(base)
    rows = []
    for block_id in pd.unique(block_ids):
        mask = block_ids == block_id
        meta = block_meta[block_meta["hidden_block_id"].eq(str(block_id))].iloc[0].to_dict()
        rec: dict[str, Any] = {
            "role": role,
            "file": file_name,
            "hidden_block_id": str(block_id),
            "n_rows": int(mask.sum()),
            "mean_abs_logit_move": float(np.mean(np.abs(delta[mask]))),
            "posterior_ce_delta_vs_mixmin": float(np.mean(bce(posterior[mask], candidate[mask]) - bce(posterior[mask], base[mask]))),
            "posterior_direction_agreement": mass_agreement(delta[mask], logit(posterior[mask]) - logit(base[mask])),
            "posterior_mean_abs_shift": float(meta.get("posterior_mean_abs_shift", np.nan)),
            "raw05_mean_abs_shift_vs_stage2": float(meta.get("raw05_mean_abs_shift_vs_stage2", np.nan)),
        }
        for target in TARGETS:
            j = TARGETS.index(target)
            rec[f"move_abs_{target}"] = float(np.mean(np.abs(delta[mask, j])))
            rec[f"posterior_ce_delta_{target}"] = float(
                np.mean(bce(posterior[mask, [j]], candidate[mask, [j]]) - bce(posterior[mask, [j]], base[mask, [j]]))
            )
        rows.append(rec)
    return pd.DataFrame(rows)


def local_stress_lookup() -> dict[str, dict[str, float]]:
    scan = pd.read_csv(OUT / "e89_e86_e72_decontamination_scan.csv")
    e90 = pd.read_csv(OUT / "e90_e89_pareto_knee_scores.csv")
    rows: dict[str, pd.Series] = {}
    rows["max_upside_e86"] = scan[(scan["strategy"].eq("control")) & (scan["source"].eq("e86"))].iloc[0]
    rows["conservative_e85"] = scan[(scan["strategy"].eq("control")) & (scan["source"].eq("e85"))].iloc[0]
    rows["noq2_contrast"] = scan[(scan["strategy"].eq("control")) & (scan["source"].eq("noq2"))].iloc[0]
    rows["min_contam_e89"] = scan[scan["materialized_submission"].fillna(False).astype(bool)].iloc[0]
    e90_tag = str(e90[e90["materialized_submission"].astype(bool)]["tag"].iloc[0])
    rows["balanced_e90"] = scan[scan["tag"].eq(e90_tag)].iloc[0]

    keep = [
        "all_delta_vs_mixmin",
        "e72_failed_contamination_index",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "mixmin_reversal_index",
    ]
    out: dict[str, dict[str, float]] = {}
    for role, rec in rows.items():
        out[role] = {col: float(rec[col]) for col in keep}
    return out


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    block_ids = sample_block_ids(train, sample)
    block_meta = pd.read_csv(OUT / "hidden_block_posterior_block_summary.csv")
    if set(pd.unique(block_ids).astype(str)) - set(block_meta["hidden_block_id"].astype(str)):
        missing = sorted(set(pd.unique(block_ids).astype(str)) - set(block_meta["hidden_block_id"].astype(str)))
        raise ValueError(f"missing hidden block metadata: {missing[:5]}")

    meta_by_row = block_meta.set_index("hidden_block_id").loc[pd.Series(block_ids).astype(str)].reset_index(drop=True)
    posterior = np.column_stack([meta_by_row[f"posterior_rate_{target}"].to_numpy(dtype=np.float64) for target in TARGETS])
    endpoint = np.column_stack([meta_by_row[f"endpoint_rate_{target}"].to_numpy(dtype=np.float64) for target in TARGETS])
    prior = np.column_stack([meta_by_row[f"prior_rate_{target}"].to_numpy(dtype=np.float64) for target in TARGETS])
    endpoint = np.where(np.isfinite(endpoint), endpoint, prior)

    base = load_sub("submission_mixmin_0c916bb4.csv").sort_values(KEY).reset_index(drop=True)[TARGETS].to_numpy(dtype=np.float64)
    e72 = load_sub("submission_e72_topabs50_q2s3_gate_4e48cba2.csv").sort_values(KEY).reset_index(drop=True)[TARGETS].to_numpy(dtype=np.float64)
    e72_delta = logit(e72) - logit(base)
    posterior_direction = logit(posterior) - logit(base)
    endpoint_direction = logit(endpoint) - logit(base)

    local = local_stress_lookup()
    score_rows: list[dict[str, Any]] = []
    block_frames: list[pd.DataFrame] = []
    for role, file_name in CANDIDATES:
        pred = load_sub(file_name).sort_values(KEY).reset_index(drop=True)[TARGETS].to_numpy(dtype=np.float64)
        delta = logit(pred) - logit(base)
        rec: dict[str, Any] = {
            "role": role,
            "file": file_name,
            "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(delta))),
            "posterior_direction_cosine": cosine(delta, posterior_direction),
            "endpoint_direction_cosine": cosine(delta, endpoint_direction),
            "e72_failed_direction_cosine": cosine(delta, e72_delta),
            "posterior_direction_mass_agree": mass_agreement(delta, posterior_direction),
            "endpoint_direction_mass_agree": mass_agreement(delta, endpoint_direction),
            "e72_direction_mass_agree": mass_agreement(delta, e72_delta),
            "block_target_r2": block_target_r2(delta, block_ids),
            "s_target_mass_frac": float(np.abs(delta[:, target_idx(TARGET_GROUPS["S"])]).sum() / max(np.abs(delta).sum(), 1.0e-18)),
            "q2s3_mass_frac": float(np.abs(delta[:, target_idx(TARGET_GROUPS["Q2S3"])]).sum() / max(np.abs(delta).sum(), 1.0e-18)),
            "s123_mass_frac": float(np.abs(delta[:, target_idx(TARGET_GROUPS["S123"])]).sum() / max(np.abs(delta).sum(), 1.0e-18)),
        }
        for group_name, targets in TARGET_GROUPS.items():
            rec[f"posterior_ce_delta_{group_name}_vs_mixmin"] = ce_delta(posterior, pred, base, targets)
            rec[f"endpoint_ce_delta_{group_name}_vs_mixmin"] = ce_delta(endpoint, pred, base, targets)
        rec.update(movement_mass_stats(delta, block_ids, block_meta))
        rec.update({f"local_{k}": v for k, v in local.get(role, {}).items()})
        score_rows.append(rec)
        block_frames.append(block_detail(role, file_name, pred, base, posterior, block_ids, block_meta))

    scores = pd.DataFrame(score_rows)
    # Diagnostic score only: it combines independent hidden-block alignment with
    # already-local E89/E90 stress. It is not a public LB regression.
    scores["hidden_block_alignment_score"] = (
        -2.0e4 * scores["posterior_ce_delta_all_vs_mixmin"].fillna(0.0)
        + 0.80 * scores["posterior_direction_mass_agree"].fillna(0.0)
        + 0.35 * scores["block_target_r2"].fillna(0.0)
        + 0.20 * scores["posterior_shift_topquartile_mass_lift"].fillna(0.0)
        - 0.55 * scores["e72_direction_mass_agree"].fillna(0.0)
    )
    scores = scores.sort_values("hidden_block_alignment_score", ascending=False).reset_index(drop=True)
    detail = pd.concat(block_frames, ignore_index=True)

    scores.to_csv(SCORES_OUT, index=False)
    detail.to_csv(BLOCK_DETAIL_OUT, index=False)
    write_report(scores, detail)
    print(
        {
            "candidates": int(len(scores)),
            "top_role": str(scores.iloc[0]["role"]),
            "top_score": float(scores.iloc[0]["hidden_block_alignment_score"]),
            "best_posterior_ce_role": str(scores.sort_values("posterior_ce_delta_all_vs_mixmin").iloc[0]["role"]),
            "best_block_r2_role": str(scores.sort_values("block_target_r2", ascending=False).iloc[0]["role"]),
            "report": str(REPORT_OUT),
        }
    )


def write_report(scores: pd.DataFrame, detail: pd.DataFrame) -> None:
    top_cols = [
        "role",
        "file",
        "hidden_block_alignment_score",
        "posterior_ce_delta_all_vs_mixmin",
        "endpoint_ce_delta_all_vs_mixmin",
        "posterior_direction_mass_agree",
        "block_target_r2",
        "posterior_shift_topquartile_mass_lift",
        "e72_direction_mass_agree",
        "local_all_delta_vs_mixmin",
        "local_e72_failed_contamination_index",
        "local_hidden_q2s3_mean_minus_base",
        "local_world_support_minus_base",
    ]
    compare = scores[scores["role"].isin(["max_upside_e86", "balanced_e90", "min_contam_e89", "conservative_e85", "noq2_contrast"])]
    pair = compare.sort_values("hidden_block_alignment_score", ascending=False)[top_cols]
    by_block = (
        detail[detail["role"].isin(["max_upside_e86", "balanced_e90", "min_contam_e89"])]
        .sort_values(["role", "posterior_ce_delta_vs_mixmin"])
        .groupby("role", sort=False)
        .head(5)
    )
    block_cols = [
        "role",
        "hidden_block_id",
        "n_rows",
        "posterior_ce_delta_vs_mixmin",
        "posterior_direction_agreement",
        "mean_abs_logit_move",
        "posterior_mean_abs_shift",
    ]

    leader = str(scores.iloc[0]["role"])
    best_ce = str(scores.sort_values("posterior_ce_delta_all_vs_mixmin").iloc[0]["role"])
    best_r2 = str(scores.sort_values("block_target_r2", ascending=False).iloc[0]["role"])
    e90 = scores[scores["role"].eq("balanced_e90")].iloc[0]
    e86 = scores[scores["role"].eq("max_upside_e86")].iloc[0]
    e89 = scores[scores["role"].eq("min_contam_e89")].iloc[0]

    if leader == "failed_e72":
        decision = (
            "H87 is not supported as a selector. The hidden-block posterior representation prefers the known public-negative E72 file, so this posterior is E72-tainted for submission ranking. "
            "Use it as a representation diagnostic, not as a public-safe target."
        )
    elif leader == "balanced_e90":
        decision = (
            "E92 supports E90 as the best next balanced sensor under hidden-block posterior geometry. "
            "This does not certify LB improvement, but it gives E90 an independent reason beyond E72-contamination arithmetic."
        )
    elif leader == "max_upside_e86":
        decision = (
            "E92 keeps E86 as the strongest hidden-block alignment bet. The E72-contamination warning remains, but block/posterior geometry does not justify demoting E86."
        )
    elif leader == "min_contam_e89":
        decision = (
            "E92 favors the minimum-contamination E89 repair, meaning hidden-block posterior alignment also rewards aggressive E72 cleanup."
        )
    else:
        decision = (
            "E92 does not promote a new public file. It acts as a diagnostic lens over E86/E90/E89 rather than a standalone selector."
        )

    lines = [
        "# E92 Hidden-Block Posterior Alignment Audit",
        "",
        "## Observe",
        "",
        "E91 killed the known-public movement proxy as a submission selector. The remaining E86/E90/E89 choice is not score forecast but hidden-world interpretation: maximum structural retention, row-coherent decontamination, or minimum E72 contamination.",
        "",
        "## Wonder",
        "",
        "If hidden blocks are part of the true data-generating process, do the post-mixmin candidates move toward the block posterior representation or only optimize local combo stress?",
        "",
        "## Hypothesis",
        "",
        "H87: E90's row-coherent repair should preserve more hidden-block posterior alignment than E89 while reducing E72 failed-direction agreement versus E86.",
        "",
        "## Method",
        "",
        "- Use `hidden_block_posterior_block_summary.csv` as the target representation, not as a public-LB label.",
        "- For each candidate, compare its probabilities against mixmin using row-repeated block posterior rates and endpoint rates.",
        "- Measure posterior CE delta, posterior-direction mass agreement, hidden-block/target R2 of logit movement, movement concentration in high-posterior-shift blocks, and agreement with the failed E72 direction.",
        "- Join the existing E89/E90 local stress metrics only as context; no public score regression is fit.",
        "",
        "## Candidate Scores",
        "",
        e56.markdown_table(scores[top_cols]),
        "",
        "## E86/E90/E89/E85 Lens",
        "",
        e56.markdown_table(pair),
        "",
        "## Best Posterior-Aligned Blocks",
        "",
        e56.markdown_table(by_block[block_cols]),
        "",
        "## Falsification Read",
        "",
        f"- Overall hidden-block alignment leader: `{leader}`.",
        f"- Best posterior CE delta: `{best_ce}`.",
        f"- Highest block-target movement R2: `{best_r2}`.",
        "- Since `failed_e72` is a known public-negative anchor, any representation score that ranks it first is not public-safe as a selector.",
        f"- E86 posterior CE delta `{float(e86['posterior_ce_delta_all_vs_mixmin']):+.9f}`, E72 mass agreement `{float(e86['e72_direction_mass_agree']):.6f}`.",
        f"- E90 posterior CE delta `{float(e90['posterior_ce_delta_all_vs_mixmin']):+.9f}`, E72 mass agreement `{float(e90['e72_direction_mass_agree']):.6f}`.",
        f"- E89 posterior CE delta `{float(e89['posterior_ce_delta_all_vs_mixmin']):+.9f}`, E72 mass agreement `{float(e89['e72_direction_mass_agree']):.6f}`.",
        "",
        "## Decision",
        "",
        decision,
        "",
        "No E92 submission is materialized. This audit updates the ordering rationale for already materialized E86/E90/E89 sensors.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
