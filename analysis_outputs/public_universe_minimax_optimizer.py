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

from public_subset_sensitivity_audit import build_masks, load_sub  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

BASELINE_PRIOR = "submission_public2dblend_budget0p0.csv"

CORE_Q = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]
MASK_Q = [
    "submission_public_maskaware_t80_r11_544844af.csv",
    "submission_public_maskaware_t80_r12_dcfaabba.csv",
    "submission_public_maskaware_t65_r07_768f6df0.csv",
    "submission_public_maskaware_t80_r10_18d78615.csv",
]
CONSERVATIVE_Q = [
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_public2dblend_budget0p0.csv",
    "submission_projblend_cap0p0.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_public_consfront_t80_r10_b06ca82f.csv",
]

PROFILES = {
    "u80": {"core": 0.80, "mask": 0.15, "conservative": 0.05},
    "u65": {"core": 0.65, "mask": 0.25, "conservative": 0.10},
    "u50": {"core": 0.50, "mask": 0.30, "conservative": 0.20},
    "u35": {"core": 0.35, "mask": 0.30, "conservative": 0.35},
}

BASE_CANDIDATES = [
    BASELINE_PRIOR,
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_projblend_cap0p0.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
    "submission_public_minimaxens_r01_a6_h422045.csv",
    "submission_public_consfront_t80_r10_b06ca82f.csv",
    "submission_public_maskaware_t80_r11_544844af.csv",
    "submission_public_maskaware_t65_r07_768f6df0.csv",
]


@dataclass
class EvalResult:
    score: float
    weighted_expected: float
    p90_expected: float
    weighted_regret: float
    p90_regret: float
    p95_regret: float
    max_regret: float
    weighted_delta_vs_prior: float
    p90_delta_vs_prior: float
    win_rate_vs_prior: float


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def ce_row_loss(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    qq = clip(q)
    pp = clip(p)
    return (-(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))).mean(axis=1)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(pred)
    return float((-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))).mean())


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    order = np.argsort(values)
    v = values[order]
    w = weights[order]
    cdf = np.cumsum(w)
    cdf = cdf / cdf[-1]
    return float(v[np.searchsorted(cdf, q, side="left")])


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def normalized_mask_matrix(sample: pd.DataFrame, max_masks: int | None = None, seed: int = 260526) -> np.ndarray:
    masks = [m for m in build_masks(sample) if m["mask_kind"] != "all"]
    if max_masks is not None and len(masks) > max_masks:
        rng = np.random.default_rng(seed)
        keep_idx: list[int] = []
        for kind in ["global_order", "subject_order", "single_subject"]:
            keep_idx.extend([i for i, m in enumerate(masks) if m["mask_kind"] == kind])
        for kind, cap in [("subject_contiguous", max_masks // 3), ("random_rows", max_masks)]:
            idx = [i for i, m in enumerate(masks) if m["mask_kind"] == kind]
            remaining = max(0, max_masks - len(keep_idx))
            take = min(cap, remaining, len(idx))
            if take:
                pick = rng.choice(idx, size=take, replace=False)
                keep_idx.extend(int(x) for x in pick)
        if len(keep_idx) < max_masks:
            remaining_pool = sorted(set(range(len(masks))) - set(keep_idx))
            take = min(max_masks - len(keep_idx), len(remaining_pool))
            if take:
                pick = rng.choice(remaining_pool, size=take, replace=False)
                keep_idx.extend(int(x) for x in pick)
        keep_idx = sorted(set(keep_idx))[:max_masks]
        masks = [masks[i] for i in keep_idx]
    mat = np.zeros((len(masks), len(sample)), dtype=np.float64)
    for i, rec in enumerate(masks):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
    return mat


def oof_name_for_submission(file_name: str) -> str | None:
    special = {
        "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy",
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy",
        "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy",
    }
    if file_name in special:
        return special[file_name]
    for prefix in [
        "submission_public2dblend_",
        "submission_projblend_",
        "submission_publicobsblend_",
        "submission_public_entropyproj_",
        "submission_public_entropytm_",
        "submission_public_minimaxens_",
        "submission_public_consfront_",
        "submission_public_maskaware_",
    ]:
        if file_name.startswith(prefix):
            return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    return None


def candidate_files() -> list[str]:
    files: list[str] = []
    for f in BASE_CANDIDATES:
        if (OUT / f).exists() and f not in files:
            files.append(f)
    for path_name, n in [
        ("public_posterior_scenario_robustness_summary.csv", 32),
        ("public_entropy_targetmask_selected.csv", 20),
        ("public_maskaware_entropy_selected.csv", 12),
        ("public_conservative_frontier_selected.csv", 12),
        ("public_minimax_ensemble_selected.csv", 8),
    ]:
        p = OUT / path_name
        if not p.exists():
            continue
        col = "file"
        for f in pd.read_csv(p)[col].head(n).tolist():
            if (OUT / f).exists() and f not in files:
                files.append(f)
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


def scenario_weights(groups: list[str], profile: dict[str, float], mask_count: int) -> np.ndarray:
    counts = {g: groups.count(g) for g in sorted(set(groups))}
    weights = []
    for g in groups:
        per_scenario = profile[g] / max(1, counts[g])
        weights.extend([per_scenario / mask_count] * mask_count)
    out = np.asarray(weights, dtype=np.float64)
    out = out / out.sum()
    return out


def evaluate(
    weights: np.ndarray,
    pred_stack: np.ndarray,
    q_scenarios: list[np.ndarray],
    mask_mat: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
    metric_weights: np.ndarray,
) -> EvalResult:
    p = clip(np.tensordot(weights, pred_stack, axes=(0, 0)))
    all_scores = []
    for q in q_scenarios:
        all_scores.append(mask_mat @ ce_row_loss(q, p))
    scores = np.concatenate(all_scores)
    regret = scores - best_scores
    delta_prior = scores - prior_scores
    weighted_expected = float(np.sum(metric_weights * scores))
    weighted_regret = float(np.sum(metric_weights * regret))
    weighted_delta_vs_prior = float(np.sum(metric_weights * delta_prior))
    p90_expected = weighted_quantile(scores, metric_weights, 0.90)
    p90_regret = weighted_quantile(regret, metric_weights, 0.90)
    p95_regret = weighted_quantile(regret, metric_weights, 0.95)
    max_regret = float(regret.max())
    p90_delta_vs_prior = weighted_quantile(delta_prior, metric_weights, 0.90)
    win_rate_vs_prior = float(np.sum(metric_weights[delta_prior < 0.0]))
    score = (
        weighted_expected
        + 1.75 * weighted_regret
        + 0.85 * p90_regret
        + 0.25 * p95_regret
        + 0.04 * max_regret
        + 0.10 * max(p90_delta_vs_prior, 0.0)
        + 0.01 * max(0.80 - win_rate_vs_prior, 0.0)
    )
    return EvalResult(
        score,
        weighted_expected,
        p90_expected,
        weighted_regret,
        p90_regret,
        p95_regret,
        max_regret,
        weighted_delta_vs_prior,
        p90_delta_vs_prior,
        win_rate_vs_prior,
    )


def search(
    pred_stack: np.ndarray,
    q_scenarios: list[np.ndarray],
    mask_mat: np.ndarray,
    best_scores: np.ndarray,
    prior_scores: np.ndarray,
    metric_weights: np.ndarray,
    seed: int,
) -> list[tuple[np.ndarray, EvalResult, str]]:
    rng = np.random.default_rng(seed)
    n = pred_stack.shape[0]
    starts: list[tuple[np.ndarray, str]] = []
    for i in range(n):
        w = np.zeros(n)
        w[i] = 1.0
        starts.append((w, f"single_{i}"))
    for alpha, count in [(0.12, 50), (0.25, 50), (0.60, 40), (1.20, 25)]:
        for _ in range(count):
            starts.append((rng.dirichlet(np.full(n, alpha)), f"dirichlet_{alpha}"))
    for k in [2, 3, 4, 5, 7]:
        for _ in range(35):
            idx = rng.choice(n, size=k, replace=False)
            local = rng.dirichlet(np.full(k, 0.65))
            w = np.zeros(n)
            w[idx] = local
            starts.append((w, f"sparse{k}"))

    scored = [(w, evaluate(w, pred_stack, q_scenarios, mask_mat, best_scores, prior_scores, metric_weights), s) for w, s in starts]
    scored.sort(key=lambda x: (x[1].score, x[1].weighted_expected))
    top = scored[:50]

    combined = top
    combined.sort(key=lambda x: (x[1].score, x[1].weighted_expected))
    dedup = []
    seen = set()
    for w, ev, source in combined:
        key = tuple(np.round(w, 4))
        if key in seen:
            continue
        dedup.append((w, ev, source))
        seen.add(key)
        if len(dedup) >= 80:
            break
    return dedup


def save_candidate(
    profile_name: str,
    rank: int,
    weights: np.ndarray,
    files: list[str],
    pred_stack: np.ndarray,
    oof_stack: np.ndarray,
    sample: pd.DataFrame,
) -> tuple[str, str]:
    pred = clip(np.tensordot(weights, pred_stack, axes=(0, 0)))
    oof = clip(np.tensordot(weights, oof_stack, axes=(0, 0)))
    tag = stable_tag(";".join(f"{f}:{w:.6f}" for f, w in zip(files, weights, strict=True) if w > 1e-5))
    sub_file = f"submission_public_universeens_{profile_name}_r{rank:02d}_{tag}.csv"
    oof_file = f"final_public_universeens_{profile_name}_r{rank:02d}_{tag}_oof.npy"
    out = sample[KEY].copy()
    out[TARGETS] = pred
    out.to_csv(OUT / sub_file, index=False)
    np.save(OUT / oof_file, oof)
    return sub_file, oof_file


def candidate_best_and_prior(
    pred_stack: np.ndarray,
    q_scenarios: list[np.ndarray],
    prior_pred: np.ndarray,
    mask_mat: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    per_candidate = []
    prior_scores_parts = []
    for q in q_scenarios:
        scores = []
        for pred in pred_stack:
            scores.append(mask_mat @ ce_row_loss(q, pred))
        per_candidate.append(np.vstack(scores))
        prior_scores_parts.append(mask_mat @ ce_row_loss(q, prior_pred))
    candidate_score_tensor = np.stack(per_candidate)
    return candidate_score_tensor.min(axis=1).reshape(-1), np.concatenate(prior_scores_parts)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    y = train[TARGETS].to_numpy(dtype=float)
    full_mask_mat = normalized_mask_matrix(sample)
    search_mask_mat = normalized_mask_matrix(sample, max_masks=128)

    files = candidate_files()
    pred_stack = np.stack([load_sub(f)[TARGETS].to_numpy(dtype=float) for f in files])
    oof_names = [oof_name_for_submission(f) for f in files]
    if any(name is None or not (OUT / name).exists() for name in oof_names):
        missing = [f for f, name in zip(files, oof_names, strict=True) if name is None or not (OUT / name).exists()]
        raise FileNotFoundError(f"missing OOF files for {missing}")
    oof_stack = np.stack([clip(np.load(OUT / name)) for name in oof_names if name is not None])

    q_files, q_groups = scenario_files()
    q_scenarios = [load_sub(f)[TARGETS].to_numpy(dtype=float) for f in q_files]
    prior_pred = load_sub(BASELINE_PRIOR)[TARGETS].to_numpy(dtype=float)
    full_best_scores, full_prior_scores = candidate_best_and_prior(pred_stack, q_scenarios, prior_pred, full_mask_mat)
    search_best_scores, search_prior_scores = candidate_best_and_prior(pred_stack, q_scenarios, prior_pred, search_mask_mat)

    all_rows = []
    saved_rows = []
    for profile_index, (profile_name, profile) in enumerate(PROFILES.items(), start=1):
        search_metric_weights = scenario_weights(q_groups, profile, search_mask_mat.shape[0])
        full_metric_weights = scenario_weights(q_groups, profile, full_mask_mat.shape[0])
        search_top = search(
            pred_stack,
            q_scenarios,
            search_mask_mat,
            search_best_scores,
            search_prior_scores,
            search_metric_weights,
            seed=260526 + profile_index * 100,
        )
        top = [
            (
                w,
                evaluate(
                    w,
                    pred_stack,
                    q_scenarios,
                    full_mask_mat,
                    full_best_scores,
                    full_prior_scores,
                    full_metric_weights,
                ),
                source,
            )
            for w, _search_ev, source in search_top
        ]
        top.sort(key=lambda x: (x[1].score, x[1].weighted_expected))
        saved_for_profile = 0
        for rank, (w, ev, source) in enumerate(top, start=1):
            row: dict[str, object] = {
                "profile": profile_name,
                "rank": rank,
                "source": source,
                "active_weights": int((w > 1e-4).sum()),
                "score": ev.score,
                "weighted_expected": ev.weighted_expected,
                "p90_expected": ev.p90_expected,
                "weighted_regret": ev.weighted_regret,
                "p90_regret": ev.p90_regret,
                "p95_regret": ev.p95_regret,
                "max_regret": ev.max_regret,
                "weighted_delta_vs_prior": ev.weighted_delta_vs_prior,
                "p90_delta_vs_prior": ev.p90_delta_vs_prior,
                "win_rate_vs_prior": ev.win_rate_vs_prior,
                "profile_weights": ";".join(f"{k}={v:.2f}" for k, v in profile.items()),
            }
            for f, weight in zip(files, w, strict=True):
                if weight > 1e-4:
                    row[f"w::{f}"] = float(weight)
            all_rows.append(row)
            if rank <= 4 and saved_for_profile < 4:
                sub_file, oof_file = save_candidate(profile_name, rank, w, files, pred_stack, oof_stack, sample)
                saved_rows.append(
                    {
                        "file": sub_file,
                        "oof_file": oof_file,
                        "profile": profile_name,
                        "rank": rank,
                        "source": source,
                        "score": ev.score,
                        "weighted_expected": ev.weighted_expected,
                        "weighted_regret": ev.weighted_regret,
                        "p90_regret": ev.p90_regret,
                        "p95_regret": ev.p95_regret,
                        "max_regret": ev.max_regret,
                        "weighted_delta_vs_prior": ev.weighted_delta_vs_prior,
                        "win_rate_vs_prior": ev.win_rate_vs_prior,
                        "active_weights": int((w > 1e-4).sum()),
                        "oof_loss": mean_loss(y, np.load(OUT / oof_file)),
                        "weights": ";".join(f"{files[i]}={w[i]:.6f}" for i in np.where(w > 1e-4)[0]),
                    }
                )
                saved_for_profile += 1

    summary = pd.DataFrame(all_rows).sort_values(["profile", "score", "weighted_expected"]).reset_index(drop=True)
    selected = pd.DataFrame(saved_rows)
    summary.to_csv(OUT / "public_universe_minimax_summary.csv", index=False)
    selected.to_csv(OUT / "public_universe_minimax_selected.csv", index=False)

    integ_rows = []
    for row in selected.itertuples(index=False):
        sub = pd.read_csv(OUT / row.file, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        oof = np.load(OUT / row.oof_file)
        integ_rows.append(
            {
                "file": row.file,
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
    integ = pd.DataFrame(integ_rows)
    integ.to_csv(OUT / "public_universe_minimax_integrity.csv", index=False)

    report = []
    report.append("# Public Universe Minimax\n")
    report.append(
        "Expanded minimax search over entropy, target-mask, mask-aware, conservative-frontier, and prior candidates. "
        "Profiles weight core posterior, mask-aware posterior, and conservative pseudo-posterior scenarios differently.\n"
    )
    cols = [
        "file",
        "profile",
        "score",
        "weighted_expected",
        "weighted_regret",
        "p90_regret",
        "p95_regret",
        "weighted_delta_vs_prior",
        "win_rate_vs_prior",
        "oof_loss",
        "active_weights",
    ]
    report.append("\n## Saved Candidates\n")
    report.append("```\n" + selected[cols].round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Integrity\n")
    report.append("```\n" + integ.round(9).to_string(index=False) + "\n```")
    (OUT / "public_universe_minimax_report.md").write_text("".join(report))

    print("[universe selected]")
    print(selected[cols].round(9).to_string(index=False))
    print("\n[integrity]")
    print(integ.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
