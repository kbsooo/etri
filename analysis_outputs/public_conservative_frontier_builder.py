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

POSTERIOR_Q = [
    "submission_public_entropyproj_public2d0_g050.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]

CONSERVATIVE_Q = [
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_public2dblend_budget0p0.csv",
    "submission_projblend_cap0p0.csv",
    "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
]

SAFE_FILES = [
    "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "submission_public2dblend_budget0p0.csv",
    "submission_projblend_cap0p0.csv",
    "submission_publicobsblend_stage2_to_ordinal_w005.csv",
    "submission_publicobsblend_anchor578_to_stage2_w095.csv",
]

RISKY_FILES = [
    "submission_public_minimaxens_r01_a6_h422045.csv",
    "submission_public_minimaxens_r05_a10_h506746.csv",
    "submission_public_entropyproj_public2d0_g075.csv",
    "submission_public_entropyproj_public2d0_g100.csv",
    "submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv",
    "submission_public_entropytm_public2d0_q1_q3_s3_s4_g075.csv",
]

TARGET_MASKS = {
    "all": TARGETS,
    "noq2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "core_q1q3s3s4": ["Q1", "Q3", "S3", "S4"],
    "q1q3s2s3s4": ["Q1", "Q3", "S2", "S3", "S4"],
}

RISK_WEIGHTS = [0.10, 0.15, 0.20, 0.25, 0.35, 0.50, 0.65, 0.80]
TRUST_LEVELS = [0.35, 0.50, 0.65, 0.80]


@dataclass
class Candidate:
    candidate_id: str
    kind: str
    safe_file: str
    risky_file: str
    blend_mode: str
    target_mask: str
    risk_weight: float
    pred: np.ndarray
    oof: np.ndarray | None


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def ce_row_loss(q: np.ndarray, p: np.ndarray) -> np.ndarray:
    qq = clip(q)
    pp = clip(p)
    return (-(qq * np.log(pp) + (1.0 - qq) * np.log(1.0 - pp))).mean(axis=1)


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(pred)
    return float((-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))).mean())


def stable_tag(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def oof_name_for_submission(file_name: str) -> str | None:
    special = {
        "submission_hybrid_0p578_logit_after_subject_final9_strict.csv": "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy",
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv": "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy",
        "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv": "final_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75_oof.npy",
    }
    if file_name in special:
        return special[file_name]
    if file_name.startswith("submission_public2dblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_projblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_publicobsblend_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_public_entropyproj_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_public_entropytm_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    if file_name.startswith("submission_public_minimaxens_"):
        return file_name.replace("submission_", "final_").replace(".csv", "_oof.npy")
    return None


def load_pred(file_name: str) -> np.ndarray:
    return load_sub(file_name)[TARGETS].to_numpy(dtype=float)


def load_oof_array(file_name: str) -> np.ndarray | None:
    oof_name = oof_name_for_submission(file_name)
    if oof_name is None:
        return None
    path = OUT / oof_name
    if not path.exists():
        return None
    return clip(np.load(path))


def blend_arrays(safe: np.ndarray, risky: np.ndarray, w: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip((1.0 - w) * safe + w * risky)
    if mode == "logit":
        return clip(sigmoid((1.0 - w) * logit(safe) + w * logit(risky)))
    raise ValueError(f"unknown blend mode {mode}")


def make_candidates() -> list[Candidate]:
    needed = []
    for f in SAFE_FILES + RISKY_FILES + POSTERIOR_Q + CONSERVATIVE_Q:
        if f not in needed and (OUT / f).exists():
            needed.append(f)
    pred = {f: load_pred(f) for f in needed}
    oof = {f: load_oof_array(f) for f in needed}

    candidates: list[Candidate] = []
    for f in needed:
        candidates.append(
            Candidate(
                candidate_id=f,
                kind="existing",
                safe_file=f,
                risky_file=f,
                blend_mode="identity",
                target_mask="all",
                risk_weight=1.0,
                pred=clip(pred[f]),
                oof=oof[f],
            )
        )

    for safe_file in SAFE_FILES:
        if safe_file not in pred:
            continue
        for risky_file in RISKY_FILES:
            if risky_file not in pred or risky_file == safe_file:
                continue
            safe_pred = pred[safe_file]
            risky_pred = pred[risky_file]
            safe_oof = oof.get(safe_file)
            risky_oof = oof.get(risky_file)
            for mode in ["prob", "logit"]:
                for mask_name, mask_targets in TARGET_MASKS.items():
                    idx = [TARGETS.index(t) for t in mask_targets]
                    for w in RISK_WEIGHTS:
                        blended = clip(safe_pred.copy())
                        blended[:, idx] = blend_arrays(safe_pred[:, idx], risky_pred[:, idx], w, mode)
                        blended_oof = None
                        if safe_oof is not None and risky_oof is not None:
                            blended_oof = clip(safe_oof.copy())
                            blended_oof[:, idx] = blend_arrays(safe_oof[:, idx], risky_oof[:, idx], w, mode)
                        cid = "|".join([safe_file, risky_file, mode, mask_name, f"{w:.2f}"])
                        candidates.append(
                            Candidate(
                                candidate_id=cid,
                                kind="frontier_blend",
                                safe_file=safe_file,
                                risky_file=risky_file,
                                blend_mode=mode,
                                target_mask=mask_name,
                                risk_weight=w,
                                pred=blended,
                                oof=blended_oof,
                            )
                        )
    return candidates


def scenario_loss_matrix(candidates: list[Candidate], q_arrays: list[np.ndarray]) -> np.ndarray:
    losses = np.zeros((len(candidates), len(q_arrays)), dtype=np.float64)
    for i, cand in enumerate(candidates):
        for j, q in enumerate(q_arrays):
            losses[i, j] = float(ce_row_loss(q, cand.pred).mean())
    return losses


def first_stage_summary(candidates: list[Candidate], q_files: list[str], losses: np.ndarray) -> pd.DataFrame:
    q_group = np.array(["posterior" if f in POSTERIOR_Q else "conservative" for f in q_files])
    post_idx = np.where(q_group == "posterior")[0]
    cons_idx = np.where(q_group == "conservative")[0]
    best = losses.min(axis=0)
    regret = losses - best

    rows = []
    for i, cand in enumerate(candidates):
        base = {
            "candidate_index": i,
            "candidate_id": cand.candidate_id,
            "kind": cand.kind,
            "safe_file": cand.safe_file,
            "risky_file": cand.risky_file,
            "blend_mode": cand.blend_mode,
            "target_mask": cand.target_mask,
            "risk_weight": cand.risk_weight,
            "posterior_full_expected": float(losses[i, post_idx].mean()),
            "conservative_full_expected": float(losses[i, cons_idx].mean()),
            "posterior_full_regret": float(regret[i, post_idx].mean()),
            "conservative_full_regret": float(regret[i, cons_idx].mean()),
            "max_full_regret": float(regret[i].max()),
        }
        for trust in TRUST_LEVELS:
            base[f"full_score_t{int(trust * 100):02d}"] = (
                trust * base["posterior_full_expected"]
                + (1.0 - trust) * base["conservative_full_expected"]
                + 1.25
                * (
                    trust * base["posterior_full_regret"]
                    + (1.0 - trust) * base["conservative_full_regret"]
                )
                + 0.10 * base["max_full_regret"]
            )
        rows.append(base)
    return pd.DataFrame(rows)


def preselect_indices(summary: pd.DataFrame) -> list[int]:
    chosen: list[int] = []
    for trust in TRUST_LEVELS:
        col = f"full_score_t{int(trust * 100):02d}"
        for idx in summary.sort_values(col)["candidate_index"].head(90).astype(int).tolist():
            if idx not in chosen:
                chosen.append(idx)
    for idx in summary[summary["kind"] == "existing"]["candidate_index"].astype(int).tolist():
        if idx not in chosen:
            chosen.append(idx)
    return chosen[:260]


def mask_matrix(sample: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame, np.ndarray]:
    masks = build_masks(sample)
    meta = []
    mat = np.zeros((len(masks), len(sample)), dtype=np.float64)
    all_mask = np.zeros(len(masks), dtype=bool)
    for i, rec in enumerate(masks):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        mat[i, mask] = 1.0 / float(mask.sum())
        meta.append({k: rec[k] for k in ["mask_kind", "mask_name", "rows"]})
        if rec["mask_kind"] == "all":
            all_mask[i] = True
    return mat, pd.DataFrame(meta), ~all_mask


def second_stage_summary(
    candidates: list[Candidate],
    selected_indices: list[int],
    q_files: list[str],
    q_arrays: list[np.ndarray],
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = [candidates[i] for i in selected_indices]
    mat, mask_meta, eval_mask = mask_matrix(sample)
    q_group = np.array(["posterior" if f in POSTERIOR_Q else "conservative" for f in q_files])
    post_idx = np.where(q_group == "posterior")[0]
    cons_idx = np.where(q_group == "conservative")[0]

    scores = np.zeros((len(selected), len(q_arrays), mat.shape[0]), dtype=np.float64)
    for i, cand in enumerate(selected):
        for j, q in enumerate(q_arrays):
            scores[i, j] = mat @ ce_row_loss(q, cand.pred)

    best = scores.min(axis=0)
    regret = scores - best
    stage2 = load_pred("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv")
    prior = load_pred("submission_public2dblend_budget0p0.csv")
    stage2_scores = np.stack([mat @ ce_row_loss(q, stage2) for q in q_arrays], axis=0)
    prior_scores = np.stack([mat @ ce_row_loss(q, prior) for q in q_arrays], axis=0)

    rows = []
    detail_rows = []
    for i, cand in enumerate(selected):
        cand_scores = scores[i][:, eval_mask]
        cand_regret = regret[i][:, eval_mask]
        stage2_delta = cand_scores - stage2_scores[:, eval_mask]
        prior_delta = cand_scores - prior_scores[:, eval_mask]
        post_scores = cand_scores[post_idx].ravel()
        cons_scores = cand_scores[cons_idx].ravel()
        post_regret = cand_regret[post_idx].ravel()
        cons_regret = cand_regret[cons_idx].ravel()
        post_stage2_delta = stage2_delta[post_idx].ravel()
        cons_stage2_delta = stage2_delta[cons_idx].ravel()
        cons_prior_delta = prior_delta[cons_idx].ravel()

        base = {
            "selected_index": i,
            "original_candidate_index": selected_indices[i],
            "candidate_id": cand.candidate_id,
            "kind": cand.kind,
            "safe_file": cand.safe_file,
            "risky_file": cand.risky_file,
            "blend_mode": cand.blend_mode,
            "target_mask": cand.target_mask,
            "risk_weight": cand.risk_weight,
            "posterior_mean_expected": float(post_scores.mean()),
            "posterior_p90_expected": float(np.quantile(post_scores, 0.90)),
            "conservative_mean_expected": float(cons_scores.mean()),
            "conservative_p90_expected": float(np.quantile(cons_scores, 0.90)),
            "posterior_mean_regret": float(post_regret.mean()),
            "conservative_mean_regret": float(cons_regret.mean()),
            "p90_regret": float(np.quantile(cand_regret.ravel(), 0.90)),
            "p95_regret": float(np.quantile(cand_regret.ravel(), 0.95)),
            "max_regret": float(cand_regret.max()),
            "posterior_mean_delta_vs_stage2": float(post_stage2_delta.mean()),
            "conservative_mean_delta_vs_stage2": float(cons_stage2_delta.mean()),
            "conservative_p90_delta_vs_stage2": float(np.quantile(cons_stage2_delta, 0.90)),
            "conservative_p90_delta_vs_prior": float(np.quantile(cons_prior_delta, 0.90)),
            "win_rate_vs_stage2_all": float((stage2_delta.ravel() < 0).mean()),
            "win_rate_vs_prior_all": float((prior_delta.ravel() < 0).mean()),
        }
        for trust in TRUST_LEVELS:
            score = (
                trust * base["posterior_mean_expected"]
                + (1.0 - trust) * base["conservative_mean_expected"]
                + 1.75
                * (
                    trust * base["posterior_mean_regret"]
                    + (1.0 - trust) * base["conservative_mean_regret"]
                )
                + 0.75 * base["p90_regret"]
                + 0.25 * base["p95_regret"]
                + 0.20 * max(base["conservative_p90_delta_vs_stage2"], 0.0)
                + 0.10 * max(base["conservative_p90_delta_vs_prior"], 0.0)
            )
            base[f"robust_score_t{int(trust * 100):02d}"] = float(score)
        rows.append(base)

        top_worst = np.argsort(cand_regret.ravel())[-8:][::-1]
        flat_shape = cand_regret.shape
        for flat in top_worst:
            q_i, mask_i = np.unravel_index(flat, flat_shape)
            rec = mask_meta[eval_mask].iloc[mask_i].to_dict()
            detail_rows.append(
                {
                    "candidate_id": cand.candidate_id,
                    "q_file": q_files[q_i],
                    "q_group": q_group[q_i],
                    **rec,
                    "expected_loss": float(cand_scores[q_i, mask_i]),
                    "regret_vs_selected_best": float(cand_regret[q_i, mask_i]),
                    "delta_vs_stage2": float(stage2_delta[q_i, mask_i]),
                    "delta_vs_prior": float(prior_delta[q_i, mask_i]),
                }
            )

    return pd.DataFrame(rows), pd.DataFrame(detail_rows)


def choose_saved(summary: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    chosen_rows = []
    seen_candidates: set[str] = set()
    for trust in TRUST_LEVELS:
        col = f"robust_score_t{int(trust * 100):02d}"
        ranked = summary.sort_values([col, "posterior_mean_expected"]).copy()
        rank = 0
        for _, row in ranked.iterrows():
            cid = str(row["candidate_id"])
            if cid in seen_candidates:
                continue
            rank += 1
            out = row.to_dict()
            out["selection_trust"] = trust
            out["selection_rank_for_trust"] = rank
            out["selection_score"] = row[col]
            chosen_rows.append(out)
            seen_candidates.add(cid)
            if rank >= 3:
                break
            if len(chosen_rows) >= limit:
                break
        if len(chosen_rows) >= limit:
            break
    return pd.DataFrame(chosen_rows).head(limit)


def save_submissions(
    selected: pd.DataFrame,
    candidates: list[Candidate],
    sample: pd.DataFrame,
    y: np.ndarray,
) -> pd.DataFrame:
    rows = []
    lookup = {i: cand for i, cand in enumerate(candidates)}
    for out_rank, row in enumerate(selected.itertuples(index=False), start=1):
        cand = lookup[int(row.original_candidate_index)]
        trust_tag = int(round(float(row.selection_trust) * 100))
        tag = stable_tag(cand.candidate_id)
        file_name = f"submission_public_consfront_t{trust_tag:02d}_r{out_rank:02d}_{tag}.csv"
        oof_name = f"final_public_consfront_t{trust_tag:02d}_r{out_rank:02d}_{tag}_oof.npy"
        out = sample[KEY].copy()
        out[TARGETS] = clip(cand.pred)
        out.to_csv(OUT / file_name, index=False)
        oof_loss = np.nan
        if cand.oof is not None:
            np.save(OUT / oof_name, clip(cand.oof))
            oof_loss = mean_loss(y, cand.oof)
        rows.append(
            {
                "file": file_name,
                "oof_file": oof_name if cand.oof is not None else "",
                "selection_trust": row.selection_trust,
                "selection_rank_for_trust": row.selection_rank_for_trust,
                "selection_score": row.selection_score,
                "safe_file": cand.safe_file,
                "risky_file": cand.risky_file,
                "blend_mode": cand.blend_mode,
                "target_mask": cand.target_mask,
                "risk_weight": cand.risk_weight,
                "posterior_mean_expected": row.posterior_mean_expected,
                "conservative_mean_expected": row.conservative_mean_expected,
                "posterior_mean_delta_vs_stage2": row.posterior_mean_delta_vs_stage2,
                "conservative_mean_delta_vs_stage2": row.conservative_mean_delta_vs_stage2,
                "oof_loss": oof_loss,
                "candidate_id": cand.candidate_id,
            }
        )
    return pd.DataFrame(rows)


def integrity(saved: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for file_name in saved["file"].tolist():
        sub = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        rows.append(
            {
                "file": file_name,
                "rows": len(sub),
                "key_match": bool(sub[KEY].equals(sample[KEY])),
                "duplicate_keys": int(sub.duplicated(KEY).sum()),
                "null_predictions": int(sub[TARGETS].isna().sum().sum()),
                "min_prob": float(sub[TARGETS].min().min()),
                "max_prob": float(sub[TARGETS].max().max()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    y = train[TARGETS].to_numpy(dtype=float)

    q_files = [f for f in POSTERIOR_Q + CONSERVATIVE_Q if (OUT / f).exists()]
    q_arrays = [load_pred(f) for f in q_files]
    candidates = make_candidates()
    losses = scenario_loss_matrix(candidates, q_arrays)
    first = first_stage_summary(candidates, q_files, losses)
    first = first.sort_values(["full_score_t65", "posterior_full_expected"]).reset_index(drop=True)
    first.to_csv(OUT / "public_conservative_frontier_stage1.csv", index=False)

    selected_indices = preselect_indices(first)
    second, worst = second_stage_summary(candidates, selected_indices, q_files, q_arrays, sample)
    second = second.sort_values(["robust_score_t65", "posterior_mean_expected"]).reset_index(drop=True)
    second.to_csv(OUT / "public_conservative_frontier_summary.csv", index=False)
    worst.to_csv(OUT / "public_conservative_frontier_worst_masks.csv", index=False)

    chosen = choose_saved(second)
    saved = save_submissions(chosen, candidates, sample, y)
    saved.to_csv(OUT / "public_conservative_frontier_selected.csv", index=False)
    integ = integrity(saved, sample)
    integ.to_csv(OUT / "public_conservative_frontier_integrity.csv", index=False)

    report = []
    report.append("# Public Conservative Frontier\n")
    report.append(
        "This grid blends public-constraint entropy/minimax predictions back toward observed-safe submissions. "
        "Scores use posterior scenarios plus conservative pseudo-posteriors from stage2, public2d0, projblend, and anchor.\n"
    )
    cols = [
        "file",
        "selection_trust",
        "selection_score",
        "safe_file",
        "risky_file",
        "blend_mode",
        "target_mask",
        "risk_weight",
        "posterior_mean_expected",
        "conservative_mean_expected",
        "posterior_mean_delta_vs_stage2",
        "conservative_mean_delta_vs_stage2",
        "oof_loss",
    ]
    report.append("\n## Saved Frontier Submissions\n")
    report.append("```\n" + saved[cols].round(9).to_string(index=False) + "\n```")
    report.append("\n\n## Integrity\n")
    report.append("```\n" + integ.round(9).to_string(index=False) + "\n```")
    (OUT / "public_conservative_frontier_report.md").write_text("".join(report))

    print("[saved conservative frontier]")
    print(saved[cols].round(9).to_string(index=False))
    print("\n[integrity]")
    print(integ.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
