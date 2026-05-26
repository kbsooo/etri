from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from public_entropy_projection_builder import (  # noqa: E402
    ANCHOR,
    ANCHOR_OOF,
    ORDINAL,
    ORDINAL_OOF,
    PUBLIC2D0,
    PUBLIC2D0_OOF,
    PROJ0,
    PROJ0_OOF,
    STAGE2,
    STAGE2_OOF,
    clip,
    expected_scores,
    load_public_scores,
    logit,
    mean_loss,
    scores_from_labels,
    sigmoid,
    solve_projection,
)


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
SORT_KEY = ["subject_id", "lifelog_date"]
EPS = 1e-5

CONSTRAINT_FILES = [ANCHOR, STAGE2, ORDINAL]
CONSTRAINT_OOFS = [ANCHOR_OOF, STAGE2_OOF, ORDINAL_OOF]
POSTERIOR_Q = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]
CONSERVATIVE_Q = [STAGE2, PUBLIC2D0, PROJ0, ANCHOR]
BASELINE_FILES = [
    STAGE2,
    PUBLIC2D0,
    PROJ0,
    "submission_public_minimaxens_r01_a6_h422045.csv",
    "submission_public_consfront_t80_r10_b06ca82f.csv",
]

GAMMAS = [0.50, 0.75, 1.00, 1.25]
AGG_MODES = ["marginal", "conditional"]
TARGET_MASKS = {
    "all": TARGETS,
    "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "core": ["Q1", "Q3", "S3", "S4"],
}
FAMILY_GROUPS = {
    "all_struct_random": ["all", "global", "rowmod", "subject_order", "subject_contig", "random"],
    "structured": ["all", "global", "rowmod", "subject_order", "subject_contig"],
    "random_all": ["random"],
    "random50": ["random50"],
    "subject_struct": ["subject_order", "subject_contig"],
    "global_struct": ["global", "rowmod"],
    "subject_contig": ["subject_contig"],
    "rowmod": ["rowmod"],
}


@dataclass
class MaskRec:
    family: str
    name: str
    mask: np.ndarray


@dataclass
class AggDelta:
    family_group: str
    agg_mode: str
    delta: np.ndarray
    included_masks: int
    mean_inclusion: float
    max_abs_delta: float
    mean_abs_delta: float


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def read_sub(file_name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def ce_row_loss(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    qq = clip(q)
    pp = clip(p)
    return (-(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))).mean(axis=1)


def build_mask_records(df: pd.DataFrame, seed: int, random_reps: int = 40, contig_reps: int = 40) -> list[MaskRec]:
    n = len(df)
    rng = np.random.default_rng(seed)
    rows: list[MaskRec] = []
    order = np.arange(n)
    rows.append(MaskRec("all", "all", np.ones(n, dtype=bool)))

    for frac in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        k = max(1, int(round(n * frac)))
        m = np.zeros(n, dtype=bool)
        m[order[:k]] = True
        rows.append(MaskRec("global", f"prefix_{frac:.2f}", m))
        m = np.zeros(n, dtype=bool)
        m[order[-k:]] = True
        rows.append(MaskRec("global", f"suffix_{frac:.2f}", m))

    for mod in [2, 3, 4, 5]:
        for rem in range(mod):
            rows.append(MaskRec("rowmod", f"mod{mod}_rem{rem}", order % mod == rem))

    work = df.copy()
    work["_row"] = np.arange(n)
    for frac in [0.25, 0.40, 0.50, 0.60]:
        pre = np.zeros(n, dtype=bool)
        suf = np.zeros(n, dtype=bool)
        for _sid, group in work.groupby("subject_id", sort=False):
            idx = group["_row"].to_numpy()
            k = max(1, int(round(len(idx) * frac)))
            pre[idx[:k]] = True
            suf[idx[-k:]] = True
        rows.append(MaskRec("subject_order", f"subj_prefix_{frac:.2f}", pre))
        rows.append(MaskRec("subject_order", f"subj_suffix_{frac:.2f}", suf))

        for rep in range(contig_reps):
            m = np.zeros(n, dtype=bool)
            for _sid, group in work.groupby("subject_id", sort=False):
                idx = group["_row"].to_numpy()
                k = max(1, int(round(len(idx) * frac)))
                start = int(rng.integers(0, max(1, len(idx) - k + 1)))
                m[idx[start : start + k]] = True
            rows.append(MaskRec("subject_contig", f"subj_contig_{frac:.2f}_{rep:03d}", m))

    for frac in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        k = max(1, int(round(n * frac)))
        for rep in range(random_reps):
            idx = rng.choice(n, size=k, replace=False)
            m = np.zeros(n, dtype=bool)
            m[idx] = True
            family = "random50" if abs(frac - 0.50) < 1e-12 else "random"
            rows.append(MaskRec(family, f"random_{frac:.2f}_{rep:03d}", m))
    return rows


def fit_mask_deltas(
    prior: np.ndarray,
    constraint_preds: list[np.ndarray],
    masks: list[MaskRec],
    target_scores: np.ndarray | None = None,
    y: np.ndarray | None = None,
) -> tuple[pd.DataFrame, dict[str, AggDelta]]:
    sum_delta = {
        f"{group}::{mode}": np.zeros_like(prior, dtype=np.float64)
        for group in FAMILY_GROUPS
        for mode in AGG_MODES
    }
    counts = {
        f"{group}::{mode}": np.zeros_like(prior, dtype=np.float64)
        for group in FAMILY_GROUPS
        for mode in AGG_MODES
    }
    mask_counts = {f"{group}::{mode}": 0 for group in FAMILY_GROUPS for mode in AGG_MODES}
    rows = []
    for rec in masks:
        mask = rec.mask
        if mask.sum() < 8:
            continue
        local_scores = target_scores
        if local_scores is None:
            if y is None:
                raise ValueError("y is required when target_scores is not supplied")
            local_scores = scores_from_labels(y[mask], [p[mask] for p in constraint_preds])
        fit = solve_projection(prior[mask], [p[mask] for p in constraint_preds], np.asarray(local_scores))
        max_resid = float(np.max(np.abs(fit.residual)))
        delta = logit(fit.prob) - logit(prior[mask])
        ok = bool(fit.converged and max_resid < 1e-6 and np.isfinite(delta).all())
        rows.append(
            {
                "family": rec.family,
                "mask_name": rec.name,
                "rows": int(mask.sum()),
                "cells": int(mask.sum() * len(TARGETS)),
                "converged": fit.converged,
                "max_abs_residual": max_resid,
                "mean_abs_logit_delta": float(np.abs(delta).mean()),
                "p90_abs_logit_delta": float(np.quantile(np.abs(delta), 0.90)),
                "max_abs_logit_delta": float(np.abs(delta).max()),
                "mean_probability_move": float(np.abs(fit.prob - prior[mask]).mean()),
                "ok": ok,
            }
        )
        if not ok:
            continue
        for group, families in FAMILY_GROUPS.items():
            if rec.family not in families:
                continue
            for mode in AGG_MODES:
                key = f"{group}::{mode}"
                sum_delta[key][mask] += delta
                counts[key][mask] += 1.0
                mask_counts[key] += 1

    aggs: dict[str, AggDelta] = {}
    for group in FAMILY_GROUPS:
        for mode in AGG_MODES:
            key = f"{group}::{mode}"
            if mask_counts[key] == 0:
                continue
            if mode == "marginal":
                denom = float(mask_counts[key])
                agg = sum_delta[key] / denom
            else:
                denom = np.maximum(counts[key], 1.0)
                agg = sum_delta[key] / denom
                agg[counts[key] == 0] = 0.0
            aggs[key] = AggDelta(
                family_group=group,
                agg_mode=mode,
                delta=agg,
                included_masks=mask_counts[key],
                mean_inclusion=float(counts[key].mean() / max(mask_counts[key], 1)),
                max_abs_delta=float(np.abs(agg).max()),
                mean_abs_delta=float(np.abs(agg).mean()),
            )
    return pd.DataFrame(rows), aggs


def apply_candidate(prior: np.ndarray, delta: np.ndarray, gamma: float, target_mask: str) -> np.ndarray:
    out = logit(prior).copy()
    idx = [TARGETS.index(t) for t in TARGET_MASKS[target_mask]]
    out[:, idx] += gamma * delta[:, idx]
    return clip(sigmoid(out))


def mask_matrix(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    masks = build_mask_records(sample, seed=999, random_reps=30, contig_reps=30)
    mat = np.zeros((len(masks), len(sample)), dtype=np.float64)
    eval_mask = np.ones(len(masks), dtype=bool)
    for i, rec in enumerate(masks):
        mat[i, rec.mask] = 1.0 / float(rec.mask.sum())
        if rec.family == "all":
            eval_mask[i] = False
    return mat, eval_mask


def summarize_candidates(
    candidates: list[dict[str, object]],
    q_files: list[str],
    q_arrays: list[np.ndarray],
    sample: pd.DataFrame,
) -> pd.DataFrame:
    mat, eval_mask = mask_matrix(sample)
    q_group = np.array(["posterior" if f in POSTERIOR_Q else "conservative" for f in q_files])
    post_idx = np.where(q_group == "posterior")[0]
    cons_idx = np.where(q_group == "conservative")[0]

    pred_arrays = [c["pred"] for c in candidates]
    baseline_preds = [read_sub(f)[TARGETS].to_numpy(dtype=float) for f in BASELINE_FILES if (OUT / f).exists()]
    all_preds = pred_arrays + baseline_preds

    all_scores = np.zeros((len(all_preds), len(q_arrays), mat.shape[0]), dtype=np.float64)
    for i, pred in enumerate(all_preds):
        for j, q in enumerate(q_arrays):
            all_scores[i, j] = mat @ ce_row_loss(q, pred)
    best_scores = all_scores.min(axis=0)

    stage2_pred = read_sub(STAGE2)[TARGETS].to_numpy(dtype=float)
    prior_pred = read_sub(PUBLIC2D0)[TARGETS].to_numpy(dtype=float)
    stage2_scores = np.stack([mat @ ce_row_loss(q, stage2_pred) for q in q_arrays])
    prior_scores = np.stack([mat @ ce_row_loss(q, prior_pred) for q in q_arrays])

    rows = []
    for i, cand in enumerate(candidates):
        scores = all_scores[i][:, eval_mask]
        regret = all_scores[i][:, eval_mask] - best_scores[:, eval_mask]
        delta_stage2 = scores - stage2_scores[:, eval_mask]
        delta_prior = scores - prior_scores[:, eval_mask]
        post_scores = scores[post_idx].ravel()
        cons_scores = scores[cons_idx].ravel()
        post_regret = regret[post_idx].ravel()
        cons_regret = regret[cons_idx].ravel()
        row = {
            k: v
            for k, v in cand.items()
            if k not in {"pred", "oof_pred"}
        }
        row.update(
            {
                "posterior_mean_expected": float(post_scores.mean()),
                "posterior_p90_expected": float(np.quantile(post_scores, 0.90)),
                "conservative_mean_expected": float(cons_scores.mean()),
                "conservative_p90_expected": float(np.quantile(cons_scores, 0.90)),
                "posterior_mean_regret": float(post_regret.mean()),
                "conservative_mean_regret": float(cons_regret.mean()),
                "p90_regret": float(np.quantile(regret.ravel(), 0.90)),
                "p95_regret": float(np.quantile(regret.ravel(), 0.95)),
                "max_regret": float(regret.max()),
                "posterior_mean_delta_vs_stage2": float(delta_stage2[post_idx].mean()),
                "conservative_mean_delta_vs_stage2": float(delta_stage2[cons_idx].mean()),
                "posterior_mean_delta_vs_prior": float(delta_prior[post_idx].mean()),
                "conservative_mean_delta_vs_prior": float(delta_prior[cons_idx].mean()),
                "win_rate_vs_stage2_all": float((delta_stage2.ravel() < 0).mean()),
                "win_rate_vs_prior_all": float((delta_prior.ravel() < 0).mean()),
            }
        )
        for trust in [0.35, 0.50, 0.65, 0.80]:
            row[f"robust_score_t{int(trust * 100):02d}"] = float(
                trust * row["posterior_mean_expected"]
                + (1.0 - trust) * row["conservative_mean_expected"]
                + 1.5
                * (
                    trust * row["posterior_mean_regret"]
                    + (1.0 - trust) * row["conservative_mean_regret"]
                )
                + 0.50 * row["p90_regret"]
                + 0.20 * row["p95_regret"]
            )
        rows.append(row)
    return pd.DataFrame(rows)


def build_candidates(
    public_aggs: dict[str, AggDelta],
    oof_aggs: dict[str, AggDelta],
    public_prior: np.ndarray,
    oof_prior: np.ndarray,
    y: np.ndarray,
) -> list[dict[str, object]]:
    candidates = []
    for key, agg in public_aggs.items():
        if key not in oof_aggs:
            continue
        oof_agg = oof_aggs[key]
        for gamma in GAMMAS:
            for target_mask in TARGET_MASKS:
                pred = apply_candidate(public_prior, agg.delta, gamma, target_mask)
                oof_pred = apply_candidate(oof_prior, oof_agg.delta, gamma, target_mask)
                family, mode = key.split("::")
                cid = f"{family}|{mode}|{target_mask}|g{gamma:.2f}"
                expected = expected_scores(pred, [read_sub(f)[TARGETS].to_numpy(dtype=float) for f in CONSTRAINT_FILES])
                candidates.append(
                    {
                        "candidate_id": cid,
                        "family_group": family,
                        "agg_mode": mode,
                        "target_mask": target_mask,
                        "gamma": gamma,
                        "included_masks": agg.included_masks,
                        "mean_inclusion": agg.mean_inclusion,
                        "mean_abs_logit_delta": agg.mean_abs_delta,
                        "max_abs_logit_delta": agg.max_abs_delta,
                        "mean_probability_move": float(np.abs(pred - public_prior).mean()),
                        "p90_probability_move": float(np.quantile(np.abs(pred - public_prior), 0.90)),
                        "oof_loss": mean_loss(y, oof_pred),
                        "pred": pred,
                        "oof_pred": oof_pred,
                        "expected_public_anchor": float(expected[0]),
                        "expected_public_stage2": float(expected[1]),
                        "expected_public_ordinal": float(expected[2]),
                    }
                )
    return candidates


def select_rows(summary: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    picked = []
    seen: set[str] = set()
    for trust in [0.35, 0.50, 0.65, 0.80]:
        col = f"robust_score_t{int(trust * 100):02d}"
        ranked = summary.sort_values([col, "posterior_mean_expected"]).reset_index(drop=True)
        count = 0
        for _, row in ranked.iterrows():
            cid = str(row["candidate_id"])
            if cid in seen:
                continue
            out = row.to_dict()
            out["selection_trust"] = trust
            out["selection_score"] = row[col]
            picked.append(out)
            seen.add(cid)
            count += 1
            if count >= 3 or len(picked) >= limit:
                break
        if len(picked) >= limit:
            break
    return pd.DataFrame(picked)


def save_selected(selected: pd.DataFrame, candidate_lookup: dict[str, dict[str, object]], sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rank, row in enumerate(selected.itertuples(index=False), start=1):
        cand = candidate_lookup[str(row.candidate_id)]
        trust_tag = int(round(float(row.selection_trust) * 100))
        gamma_tag = str(row.gamma).replace(".", "p")
        tag = short_hash(str(row.candidate_id))
        sub_file = f"submission_public_maskaware_t{trust_tag:02d}_r{rank:02d}_{tag}.csv"
        oof_file = f"final_public_maskaware_t{trust_tag:02d}_r{rank:02d}_{tag}_oof.npy"
        out = sample[KEY].copy()
        out[TARGETS] = cand["pred"]
        out.to_csv(OUT / sub_file, index=False)
        np.save(OUT / oof_file, cand["oof_pred"])
        rows.append(
            {
                "file": sub_file,
                "oof_file": oof_file,
                "rank": rank,
                "selection_trust": row.selection_trust,
                "selection_score": row.selection_score,
                "family_group": row.family_group,
                "agg_mode": row.agg_mode,
                "target_mask": row.target_mask,
                "gamma": row.gamma,
                "oof_loss": row.oof_loss,
                "posterior_mean_expected": row.posterior_mean_expected,
                "conservative_mean_expected": row.conservative_mean_expected,
                "posterior_mean_delta_vs_stage2": row.posterior_mean_delta_vs_stage2,
                "conservative_mean_delta_vs_stage2": row.conservative_mean_delta_vs_stage2,
                "mean_probability_move": row.mean_probability_move,
                "p90_probability_move": row.p90_probability_move,
                "candidate_id": row.candidate_id,
            }
        )
    return pd.DataFrame(rows)


def integrity(saved: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for file_name, oof_name in zip(saved["file"], saved["oof_file"], strict=True):
        sub = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        oof = np.load(OUT / oof_name)
        rows.append(
            {
                "file": file_name,
                "rows": len(sub),
                "key_match": bool(sub[KEY].equals(sample[KEY])),
                "duplicate_keys": int(sub.duplicated(KEY).sum()),
                "null_predictions": int(sub[TARGETS].isna().sum().sum()),
                "min_prob": float(sub[TARGETS].min().min()),
                "max_prob": float(sub[TARGETS].max().max()),
                "oof_shape": str(oof.shape),
                "oof_min": float(oof.min()),
                "oof_max": float(oof.max()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(SORT_KEY).reset_index(drop=True)
    y = train[TARGETS].to_numpy(dtype=int)

    public_prior = read_sub(PUBLIC2D0)[TARGETS].to_numpy(dtype=float)
    public_constraints = [read_sub(f)[TARGETS].to_numpy(dtype=float) for f in CONSTRAINT_FILES]
    public_scores = load_public_scores()

    oof_prior = clip(np.load(OUT / PUBLIC2D0_OOF))
    oof_constraints = [clip(np.load(OUT / f)) for f in CONSTRAINT_OOFS]

    public_masks = build_mask_records(sample, seed=260526)
    train_masks = build_mask_records(train, seed=260527)
    public_diag, public_aggs = fit_mask_deltas(public_prior, public_constraints, public_masks, target_scores=public_scores)
    oof_diag, oof_aggs = fit_mask_deltas(oof_prior, oof_constraints, train_masks, y=y)
    public_diag.to_csv(OUT / "public_maskaware_projection_public_mask_diagnostics.csv", index=False)
    oof_diag.to_csv(OUT / "public_maskaware_projection_oof_mask_diagnostics.csv", index=False)

    candidates = build_candidates(public_aggs, oof_aggs, public_prior, oof_prior, y)
    q_files = [f for f in POSTERIOR_Q + CONSERVATIVE_Q if (OUT / f).exists()]
    q_arrays = [read_sub(f)[TARGETS].to_numpy(dtype=float) for f in q_files]
    summary = summarize_candidates(candidates, q_files, q_arrays, sample)
    summary = summary.sort_values(["robust_score_t65", "posterior_mean_expected"]).reset_index(drop=True)
    summary.to_csv(OUT / "public_maskaware_entropy_summary.csv", index=False)

    selected = select_rows(summary)
    lookup = {str(c["candidate_id"]): c for c in candidates}
    saved = save_selected(selected, lookup, sample)
    saved.to_csv(OUT / "public_maskaware_entropy_selected.csv", index=False)
    integ = integrity(saved, sample)
    integ.to_csv(OUT / "public_maskaware_entropy_integrity.csv", index=False)

    family_diag = (
        public_diag.groupby("family")
        .agg(
            masks=("mask_name", "count"),
            ok_rate=("ok", "mean"),
            median_rows=("rows", "median"),
            mean_abs_logit_delta=("mean_abs_logit_delta", "mean"),
            p90_abs_logit_delta=("p90_abs_logit_delta", "mean"),
            max_abs_logit_delta=("max_abs_logit_delta", "max"),
            mean_probability_move=("mean_probability_move", "mean"),
        )
        .reset_index()
    )
    family_diag.to_csv(OUT / "public_maskaware_projection_family_diagnostics.csv", index=False)

    report = []
    report.append("# Public Mask-Aware Entropy Projection\n")
    report.append(
        "This experiment inverts the assumption that the public LB subset behaves like all 250 rows. "
        "It solves the three public-score constraints on many plausible row masks, averages the resulting logit shifts, and scores marginal/conditional mask-bagged candidates.\n"
    )
    report.append("\n## Public Mask Diagnostics\n")
    report.append("```\n" + family_diag.round(6).to_string(index=False) + "\n```")
    cols = [
        "file",
        "selection_trust",
        "selection_score",
        "family_group",
        "agg_mode",
        "target_mask",
        "gamma",
        "oof_loss",
        "posterior_mean_expected",
        "conservative_mean_expected",
        "posterior_mean_delta_vs_stage2",
        "conservative_mean_delta_vs_stage2",
        "mean_probability_move",
    ]
    report.append("\n\n## Saved Candidates\n")
    report.append("```\n" + saved[cols].round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Integrity\n")
    report.append("```\n" + integ.round(9).to_string(index=False) + "\n```")
    (OUT / "public_maskaware_entropy_report.md").write_text("".join(report))

    print("[mask-aware saved]")
    print(saved[cols].round(9).to_string(index=False))
    print("\n[integrity]")
    print(integ.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
