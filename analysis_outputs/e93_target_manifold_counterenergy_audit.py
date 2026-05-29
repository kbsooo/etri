#!/usr/bin/env python3
"""E93 target-manifold counter-energy audit.

E92 found that hidden-block posterior alignment prefers the known
public-negative E72 candidate. This audit asks whether the target dependency
manifold learned from train labels supplies a counter-energy that rejects that
E72-like movement.

This is deliberately not a public-LB regression. The output is a diagnostic:
if the target manifold also likes E72, H11 remains a weak selector; if it
separates E72 from E86/E90/E89, it becomes a useful gate energy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import TARGETS, KEY, clip, logit  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub, locate  # noqa: E402


SCORES_OUT = OUT / "e93_target_manifold_counterenergy_scores.csv"
TARGET_DETAIL_OUT = OUT / "e93_target_manifold_counterenergy_target_detail.csv"
PAIR_DETAIL_OUT = OUT / "e93_target_manifold_counterenergy_pair_detail.csv"
REPORT_OUT = OUT / "e93_target_manifold_counterenergy_report.md"


@dataclass(frozen=True)
class Candidate:
    role: str
    file: str
    public_lb: float | None = None
    family: str = "post_mixmin"


CANDIDATES = [
    Candidate("frontier_mixmin", "submission_mixmin_0c916bb4.csv", 0.5763066405, "known_public"),
    Candidate("failed_e72", "submission_e72_topabs50_q2s3_gate_4e48cba2.csv", 0.5764077772, "known_public"),
    Candidate("previous_a2c8", "submission_frontier_cvjepa_refine_a2c8d2c8.csv", 0.5774393210, "known_public"),
    Candidate("raw05", "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", 0.5775263072, "known_public"),
    Candidate("stage2", "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", 0.5779449757, "known_public"),
    Candidate("ordinal_q", "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv", 0.5783033652, "known_public"),
    Candidate("final9", "submission_hybrid_0p578_logit_after_subject_final9_strict.csv", 0.5784273528, "known_public"),
    Candidate("bad_q2_jepa", "submission_jepa_latent_q2_w0p45.csv", 0.5798012862, "known_public"),
    Candidate("bad_lejepa", "submission_lejepa_targetwise_strict_best_scale0p5.csv", 0.5802468192, "known_public"),
    Candidate("bad_residual_jepa", "submission_jepa_latent_residual_probe.csv", 0.5812273278, "known_public"),
    Candidate("conservative_e85", "submission_e85_inverse_conflict_pruned_58b23ed1.csv", None, "live"),
    Candidate("max_upside_e86", "submission_e86_e85_consensus_a3f7c96f.csv", None, "live"),
    Candidate("noq2_contrast", "submission_e87_noq2_source_consensus_a85c4e39.csv", None, "live"),
    Candidate("balanced_e90", "submission_e90_e72pareto_28925de5.csv", None, "live"),
    Candidate("min_contam_e89", "submission_e89_e72decontam_00d7807f.csv", None, "live"),
]


def bce(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64)
    p = clip(p)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def logsumexp(a: np.ndarray, axis: int = 0) -> np.ndarray:
    a = np.asarray(a, dtype=np.float64)
    m = np.max(a, axis=axis, keepdims=True)
    return np.squeeze(m, axis=axis) + np.log(np.sum(np.exp(a - m), axis=axis))


def locate_required(file_name: str) -> Path:
    path = locate(file_name)
    if path is None:
        alt = JEPA / file_name
        if alt.exists():
            return alt
        raise FileNotFoundError(file_name)
    return path


def read_pred(file_name: str, sample: pd.DataFrame) -> pd.DataFrame:
    path = locate_required(file_name)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEY).reset_index(drop=True)
    if not df[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {file_name}")
    return df


def fit_conditional_models(y: np.ndarray) -> dict[str, LogisticRegression]:
    models: dict[str, LogisticRegression] = {}
    for j, target in enumerate(TARGETS):
        x = np.delete(y, j, axis=1)
        clf = LogisticRegression(C=0.35, solver="liblinear", max_iter=1000)
        clf.fit(x, y[:, j])
        models[target] = clf
    return models


def conditional_rates(models: dict[str, LogisticRegression], p: np.ndarray) -> np.ndarray:
    out = np.zeros_like(p, dtype=np.float64)
    for j, target in enumerate(TARGETS):
        x = np.delete(p, j, axis=1)
        out[:, j] = models[target].predict_proba(x)[:, 1]
    return clip(out)


def empirical_pattern_stats(y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    labels, counts = np.unique(y.astype(int), axis=0, return_counts=True)
    weights = counts.astype(np.float64) / float(counts.sum())
    log_weights = np.log(weights)
    return labels.astype(np.float64), weights, log_weights


def pattern_mixture_nll(p: np.ndarray, patterns: np.ndarray, log_weights: np.ndarray) -> np.ndarray:
    p = clip(p)
    # rows x patterns x targets Bernoulli likelihood.
    logp = np.log(p)
    log1p = np.log(1.0 - p)
    ll = np.einsum("rt,pt->rp", logp, patterns) + np.einsum("rt,pt->rp", log1p, 1.0 - patterns)
    return -logsumexp(ll + log_weights[None, :], axis=1)


def nearest_pattern_nll(p: np.ndarray, patterns: np.ndarray) -> np.ndarray:
    p = clip(p)
    logp = np.log(p)
    log1p = np.log(1.0 - p)
    ll = np.einsum("rt,pt->rp", logp, patterns) + np.einsum("rt,pt->rp", log1p, 1.0 - patterns)
    return -np.max(ll, axis=1)


def corr_from_binary(y: np.ndarray) -> np.ndarray:
    corr = np.corrcoef(y.astype(np.float64), rowvar=False)
    return np.nan_to_num(corr, nan=0.0)


def corr_from_probs(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    mean = p.mean(axis=0)
    second = (p[:, :, None] * p[:, None, :]).mean(axis=0)
    cov = second - mean[:, None] * mean[None, :]
    var = np.mean(p * (1.0 - p), axis=0) + np.diag(cov)
    denom = np.sqrt(np.maximum(var[:, None] * var[None, :], 1.0e-12))
    corr = cov / denom
    np.fill_diagonal(corr, 1.0)
    return np.nan_to_num(corr, nan=0.0)


def upper_values(mat: np.ndarray) -> np.ndarray:
    idx = np.triu_indices_from(mat, k=1)
    return mat[idx]


def pair_corr_detail(role: str, file_name: str, corr: np.ndarray, train_corr: np.ndarray, base_corr: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, left in enumerate(TARGETS):
        for j, right in enumerate(TARGETS):
            if i >= j:
                continue
            rows.append(
                {
                    "role": role,
                    "file": file_name,
                    "left": left,
                    "right": right,
                    "pred_corr": float(corr[i, j]),
                    "train_corr": float(train_corr[i, j]),
                    "mixmin_corr": float(base_corr[i, j]),
                    "abs_gap_to_train": float(abs(corr[i, j] - train_corr[i, j])),
                    "abs_gap_delta_vs_mixmin": float(abs(corr[i, j] - train_corr[i, j]) - abs(base_corr[i, j] - train_corr[i, j])),
                }
            )
    return rows


def stress_lookup() -> pd.DataFrame:
    e92_path = OUT / "e92_hidden_block_posterior_alignment_scores.csv"
    if e92_path.exists():
        e92 = pd.read_csv(e92_path)
        keep = [
            "role",
            "posterior_ce_delta_all_vs_mixmin",
            "e72_direction_mass_agree",
            "block_target_r2",
            "hidden_block_alignment_score",
        ]
        return e92[[c for c in keep if c in e92.columns]].copy()
    return pd.DataFrame({"role": []})


def target_detail_rows(
    role: str,
    file_name: str,
    p: np.ndarray,
    base: np.ndarray,
    cond: np.ndarray,
    base_cond: np.ndarray,
) -> list[dict[str, Any]]:
    rows = []
    for j, target in enumerate(TARGETS):
        resid = logit(p[:, j]) - logit(cond[:, j])
        base_resid = logit(base[:, j]) - logit(base_cond[:, j])
        rows.append(
            {
                "role": role,
                "file": file_name,
                "target": target,
                "mean_prob": float(p[:, j].mean()),
                "mean_prob_delta_vs_mixmin": float(p[:, j].mean() - base[:, j].mean()),
                "conditional_bce": float(np.mean(bce(cond[:, [j]], p[:, [j]]))),
                "conditional_bce_delta_vs_mixmin": float(np.mean(bce(cond[:, [j]], p[:, [j]]) - bce(base_cond[:, [j]], base[:, [j]]))),
                "conditional_logit_resid_rms": float(np.sqrt(np.mean(resid**2))),
                "conditional_logit_resid_rms_delta_vs_mixmin": float(np.sqrt(np.mean(resid**2)) - np.sqrt(np.mean(base_resid**2))),
                "movement_abs_logit_vs_mixmin": float(np.mean(np.abs(logit(p[:, [j]]) - logit(base[:, [j]])))),
            }
        )
    return rows


def signed_rank(values: pd.Series, ascending: bool = True) -> pd.Series:
    return values.rank(method="average", ascending=ascending)


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    rows = []
    for rec in frame.to_dict("records"):
        row = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                row.append("")
            elif isinstance(value, (float, np.floating)):
                row.append(format(float(value), floatfmt))
            else:
                row.append(str(value))
        rows.append(row)
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)
    models = fit_conditional_models(y)
    patterns, _weights, log_weights = empirical_pattern_stats(y)
    train_corr = corr_from_binary(y)

    base = read_pred("submission_mixmin_0c916bb4.csv", sample)[TARGETS].to_numpy(dtype=np.float64)
    base_cond = conditional_rates(models, base)
    base_corr = corr_from_probs(base)
    base_pattern = pattern_mixture_nll(base, patterns, log_weights)
    base_nearest = nearest_pattern_nll(base, patterns)
    base_cond_bce = float(np.mean(bce(base_cond, base)))
    base_cond_rms = float(np.sqrt(np.mean((logit(base) - logit(base_cond)) ** 2)))
    base_corr_gap = float(np.mean(np.abs(upper_values(base_corr) - upper_values(train_corr))))
    base_pattern_nll = float(np.mean(base_pattern))
    base_nearest_nll = float(np.mean(base_nearest))

    scores: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    for cand in CANDIDATES:
        if locate(cand.file) is None and not (JEPA / cand.file).exists():
            continue
        frame = read_pred(cand.file, sample)
        p = frame[TARGETS].to_numpy(dtype=np.float64)
        cond = conditional_rates(models, p)
        corr = corr_from_probs(p)
        pattern_nll = pattern_mixture_nll(p, patterns, log_weights)
        nearest_nll = nearest_pattern_nll(p, patterns)
        cond_bce = float(np.mean(bce(cond, p)))
        cond_rms = float(np.sqrt(np.mean((logit(p) - logit(cond)) ** 2)))
        corr_gap = float(np.mean(np.abs(upper_values(corr) - upper_values(train_corr))))
        mean_abs_move = float(np.mean(np.abs(logit(p) - logit(base))))
        move_entropy = float(np.mean(-(p * np.log(clip(p)) + (1.0 - p) * np.log(clip(1.0 - p)))))

        rec: dict[str, Any] = {
            "role": cand.role,
            "file": cand.file,
            "family": cand.family,
            "public_lb": cand.public_lb,
            "public_delta_vs_mixmin": None if cand.public_lb is None else cand.public_lb - 0.5763066405,
            "mean_abs_logit_move_vs_mixmin": mean_abs_move,
            "mean_prob": float(p.mean()),
            "prediction_entropy": move_entropy,
            "conditional_bce": cond_bce,
            "conditional_bce_delta_vs_mixmin": cond_bce - base_cond_bce,
            "conditional_logit_resid_rms": cond_rms,
            "conditional_logit_resid_rms_delta_vs_mixmin": cond_rms - base_cond_rms,
            "pattern_mixture_nll": float(np.mean(pattern_nll)),
            "pattern_mixture_nll_delta_vs_mixmin": float(np.mean(pattern_nll) - base_pattern_nll),
            "nearest_pattern_nll": float(np.mean(nearest_nll)),
            "nearest_pattern_nll_delta_vs_mixmin": float(np.mean(nearest_nll) - base_nearest_nll),
            "pair_corr_l1_gap": corr_gap,
            "pair_corr_l1_gap_delta_vs_mixmin": corr_gap - base_corr_gap,
            "pair_corr_max_abs_gap_delta_vs_mixmin": float(
                np.max(np.abs(upper_values(corr) - upper_values(train_corr)) - np.abs(upper_values(base_corr) - upper_values(train_corr)))
            ),
        }
        # Lower is better for the three direct target-manifold energies.
        rec["target_manifold_delta_mean"] = float(
            np.mean(
                [
                    rec["conditional_logit_resid_rms_delta_vs_mixmin"],
                    rec["pattern_mixture_nll_delta_vs_mixmin"],
                    rec["pair_corr_l1_gap_delta_vs_mixmin"],
                ]
            )
        )
        scores.append(rec)
        target_rows.extend(target_detail_rows(cand.role, cand.file, p, base, cond, base_cond))
        pair_rows.extend(pair_corr_detail(cand.role, cand.file, corr, train_corr, base_corr))

    score_df = pd.DataFrame(scores)
    e92 = stress_lookup()
    if not e92.empty:
        score_df = score_df.merge(e92, on="role", how="left")

    # Convert target-manifold energies into a diagnostic rank. This is not used
    # as a public forecast; it only exposes whether E72 is separable.
    for col in [
        "conditional_bce_delta_vs_mixmin",
        "conditional_logit_resid_rms_delta_vs_mixmin",
        "pattern_mixture_nll_delta_vs_mixmin",
        "nearest_pattern_nll_delta_vs_mixmin",
        "pair_corr_l1_gap_delta_vs_mixmin",
        "target_manifold_delta_mean",
    ]:
        score_df[f"rank_{col}"] = signed_rank(score_df[col], ascending=True)

    live = score_df[score_df["family"].eq("live")].copy()
    known = score_df[score_df["public_lb"].notna()].copy()
    # Spearman with public LB is only a sanity check. A strong positive value
    # would mean worse target-manifold energy tracks worse known LB.
    sanity_rows = []
    if len(known) >= 4:
        for col in [
            "conditional_logit_resid_rms",
            "pattern_mixture_nll",
            "pair_corr_l1_gap",
            "target_manifold_delta_mean",
        ]:
            sanity_rows.append((col, float(known[[col, "public_lb"]].corr(method="spearman").iloc[0, 1])))
    sanity = pd.DataFrame(sanity_rows, columns=["metric", "spearman_public_lb"])

    sort_cols = ["target_manifold_delta_mean", "conditional_logit_resid_rms_delta_vs_mixmin", "pair_corr_l1_gap_delta_vs_mixmin"]
    score_df = score_df.sort_values(sort_cols, ascending=True).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows).sort_values(["role", "target"]).reset_index(drop=True)
    pair_df = pd.DataFrame(pair_rows).sort_values(["role", "abs_gap_delta_vs_mixmin"]).reset_index(drop=True)

    score_df.to_csv(SCORES_OUT, index=False)
    target_df.to_csv(TARGET_DETAIL_OUT, index=False)
    pair_df.to_csv(PAIR_DETAIL_OUT, index=False)

    failed_e72 = score_df[score_df["role"].eq("failed_e72")].iloc[0]
    mixmin = score_df[score_df["role"].eq("frontier_mixmin")].iloc[0]
    live_sorted = live.sort_values(sort_cols, ascending=True)
    known_sorted = known.sort_values("public_lb", ascending=True)
    target_sorted = target_df[target_df["role"].eq("failed_e72")].sort_values("conditional_logit_resid_rms_delta_vs_mixmin", ascending=False)

    if float(failed_e72["target_manifold_delta_mean"]) <= float(mixmin["target_manifold_delta_mean"]):
        decision = (
            "Target-manifold energy does not reject E72; H11 cannot be promoted "
            "to a public-safe selector."
        )
    elif live_sorted.iloc[0]["role"] in {"balanced_e90", "min_contam_e89", "conservative_e85"}:
        decision = (
            "Target-manifold energy separates E72 and prefers a decontaminated or "
            "conservative live candidate; keep it as an E72 counter-energy gate."
        )
    else:
        decision = (
            "Target-manifold energy rejects E72 but does not cleanly favor the "
            "risk-controlled live candidates; keep it diagnostic, not decisive."
        )

    lines = [
        "# E93 Target-Manifold Counter-Energy Audit",
        "",
        "## Question",
        "",
        "E92 showed that hidden-block posterior alignment ranks the known public-negative E72 file first. "
        "E93 asks whether the train target-dependency manifold supplies the missing counter-energy.",
        "",
        "## Method",
        "",
        "- Fit seven logistic conditional models `target_j ~ other six targets` on the train labels.",
        "- Score each submission by conditional self-consistency, empirical label-pattern mixture NLL, nearest-pattern NLL, and pair-correlation gap to train.",
        "- Compare known public anchors and live E85/E86/noQ2/E90/E89 candidates against mixmin.",
        "- Use public LB only as a sanity check for known anchors, not as a fitted objective.",
        "",
        "## Decision",
        "",
        decision,
        "",
        "## Known Public Anchor Snapshot",
        "",
        md_table(known_sorted[
            [
                "role",
                "public_lb",
                "target_manifold_delta_mean",
                "conditional_logit_resid_rms_delta_vs_mixmin",
                "pattern_mixture_nll_delta_vs_mixmin",
                "pair_corr_l1_gap_delta_vs_mixmin",
            ]
        ]),
        "",
        "## Live Candidate Snapshot",
        "",
        md_table(live_sorted[
            [
                "role",
                "target_manifold_delta_mean",
                "conditional_logit_resid_rms_delta_vs_mixmin",
                "pattern_mixture_nll_delta_vs_mixmin",
                "pair_corr_l1_gap_delta_vs_mixmin",
                "posterior_ce_delta_all_vs_mixmin",
                "e72_direction_mass_agree",
            ]
        ]),
        "",
        "## E72 Target-Level Drivers",
        "",
        md_table(target_sorted[
            [
                "target",
                "mean_prob_delta_vs_mixmin",
                "conditional_bce_delta_vs_mixmin",
                "conditional_logit_resid_rms_delta_vs_mixmin",
                "movement_abs_logit_vs_mixmin",
            ]
        ]),
        "",
        "## Public-LB Sanity Correlation",
        "",
        md_table(sanity, floatfmt=".6f") if not sanity.empty else "Not enough known anchors.",
        "",
        "## Interpretation",
        "",
        "- If E72 is better than mixmin on these energies, target dependency is another E72-tainted representation and must not gate submissions.",
        "- If E72 is worse while decontaminated candidates improve, target-manifold energy is a useful LeJEPA-style health check.",
        "- Either way, this audit should not create a submission by itself; it only decides whether H11 gets promoted or demoted.",
        "",
        "## Outputs",
        "",
        f"- `{SCORES_OUT.name}`",
        f"- `{TARGET_DETAIL_OUT.name}`",
        f"- `{PAIR_DETAIL_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")

    print(
        {
            "rows": int(len(score_df)),
            "e72_target_manifold_delta": float(failed_e72["target_manifold_delta_mean"]),
            "best_live_role": str(live_sorted.iloc[0]["role"]),
            "best_live_target_manifold_delta": float(live_sorted.iloc[0]["target_manifold_delta_mean"]),
            "decision": decision,
            "report": str(REPORT_OUT),
        }
    )


if __name__ == "__main__":
    main()
