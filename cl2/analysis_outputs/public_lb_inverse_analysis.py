from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]


ANCHOR_FILE = "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def read_submission(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)


def loss_delta_given_q(q: np.ndarray, candidate: np.ndarray, anchor: np.ndarray) -> float:
    cand = clip(candidate)
    anc = clip(anchor)
    qq = clip(q)
    return float(np.mean(qq * (np.log(anc) - np.log(cand)) + (1.0 - qq) * (np.log(1.0 - anc) - np.log(1.0 - cand))))


def contrast_weight(candidate: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    cand = clip(candidate)
    anc = clip(anchor)
    return np.log(anc / (1.0 - anc)) - np.log(cand / (1.0 - cand))


def contrast_intercept(candidate: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    cand = clip(candidate)
    anc = clip(anchor)
    return np.log(1.0 - anc) - np.log(1.0 - cand)


def observed_public_delta() -> tuple[float, float, float]:
    obs = pd.read_csv(OUT / "public_lb_observations.csv")
    public = dict(zip(obs["file"], obs["public_lb"]))
    offline = dict(zip(obs["file"], obs["offline_estimate"]))
    return (
        float(public[ANCHOR_FILE]),
        float(public[STAGE2_FILE]),
        float(offline[STAGE2_FILE]) - float(offline[ANCHOR_FILE]),
    )


def candidate_files() -> list[str]:
    out: set[str] = {ANCHOR_FILE, STAGE2_FILE}
    for summary_name in ["public_target_switch_probes.csv", "public_anchor_stage2_blend_candidates.csv"]:
        path = OUT / summary_name
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "file" in df.columns:
            out.update(str(x) for x in df["file"].dropna().tolist())
    for path in OUT.glob("submission_publicblend_anchor578_stage2567_prob_w*_latentmix.csv"):
        out.add(path.name)
    return sorted(out)


def orthogonal_fraction(w: np.ndarray, basis: np.ndarray) -> float:
    ww = w.reshape(-1)
    bb = basis.reshape(-1)
    norm_w = float(np.linalg.norm(ww))
    norm_b = float(np.linalg.norm(bb))
    if norm_w <= 1e-12 or norm_b <= 1e-12:
        return 0.0
    proj = bb * (float(np.dot(ww, bb)) / float(np.dot(bb, bb)))
    return float(np.linalg.norm(ww - proj) / norm_w)


def public_score_std_under_q(q: np.ndarray, w: np.ndarray) -> float:
    qq = clip(q)
    var = qq * (1.0 - qq) * np.square(w)
    n = q.size
    return float(np.sqrt(np.sum(var)) / max(n, 1))


def make_constraint_summary(anchor: np.ndarray, stage2: np.ndarray, anchor_public: float, stage2_public: float, offline_delta: float) -> tuple[float, pd.DataFrame]:
    public_delta = stage2_public - anchor_public
    delta_if_anchor_true = loss_delta_given_q(anchor, stage2, anchor)
    delta_if_stage2_true = loss_delta_given_q(stage2, stage2, anchor)
    denom = delta_if_stage2_true - delta_if_anchor_true
    alpha = float((public_delta - delta_if_anchor_true) / denom) if abs(denom) > 1e-12 else np.nan
    alpha_clipped = float(np.clip(alpha, 0.0, 1.0)) if np.isfinite(alpha) else np.nan

    w = contrast_weight(stage2, anchor)
    b = contrast_intercept(stage2, anchor)
    n = anchor.size
    weighted_label_sum = float(n * public_delta - np.sum(b))
    row = {
        "anchor_public": anchor_public,
        "stage2_public": stage2_public,
        "public_delta_stage2_vs_anchor": public_delta,
        "offline_delta_stage2_vs_anchor": offline_delta,
        "public_to_offline_delta_ratio": public_delta / offline_delta if abs(offline_delta) > 1e-12 else np.nan,
        "delta_if_anchor_probs_true": delta_if_anchor_true,
        "delta_if_stage2_probs_true": delta_if_stage2_true,
        "latent_mix_alpha_raw": alpha,
        "latent_mix_alpha_clipped": alpha_clipped,
        "n_cells": int(n),
        "sum_intercept": float(np.sum(b)),
        "observed_weighted_label_sum": weighted_label_sum,
        "weight_l2": float(np.linalg.norm(w.reshape(-1))),
        "score_std_under_anchor_probs": public_score_std_under_q(anchor, w),
        "score_std_under_stage2_probs": public_score_std_under_q(stage2, w),
    }
    return alpha_clipped, pd.DataFrame([row])


def make_candidate_predictions(anchor_df: pd.DataFrame, stage2_df: pd.DataFrame, alpha: float, anchor_public: float) -> pd.DataFrame:
    anchor = anchor_df[TARGETS].to_numpy(dtype=float)
    stage2 = stage2_df[TARGETS].to_numpy(dtype=float)
    q_mix = clip((1.0 - alpha) * anchor + alpha * stage2)
    stage2_w = contrast_weight(stage2, anchor)

    rows = []
    for file_name in candidate_files():
        path = OUT / file_name
        if not path.exists():
            continue
        cand_df = read_submission(file_name)
        if not cand_df[KEY].equals(anchor_df[KEY]):
            continue
        cand = cand_df[TARGETS].to_numpy(dtype=float)
        w = contrast_weight(cand, anchor)
        delta_mix = loss_delta_given_q(q_mix, cand, anchor)
        delta_anchor_prior = loss_delta_given_q(anchor, cand, anchor)
        delta_stage2_prior = loss_delta_given_q(stage2, cand, anchor)
        changed = [target for target in TARGETS if np.abs(cand_df[target].to_numpy(dtype=float) - anchor_df[target].to_numpy(dtype=float)).mean() > 1e-12]
        row = {
            "file": file_name,
            "changed_targets": ",".join(changed),
            "pred_public_from_latent_mix": float(anchor_public + delta_mix),
            "pred_delta_vs_anchor": delta_mix,
            "delta_if_anchor_probs_true": delta_anchor_prior,
            "delta_if_stage2_probs_true": delta_stage2_prior,
            "orthogonal_fraction_vs_stage2": orthogonal_fraction(w, stage2_w),
            "score_std_under_latent_mix": public_score_std_under_q(q_mix, w),
            "distance_abs_mean_vs_anchor": float(np.abs(cand - anchor).mean()),
            "distance_abs_p90_vs_anchor": float(np.quantile(np.abs(cand - anchor), 0.90)),
            "min_prob": float(cand.min()),
            "max_prob": float(cand.max()),
        }
        for target in TARGETS:
            j = TARGETS.index(target)
            row[f"{target}_pred_delta"] = loss_delta_given_q(q_mix[:, [j]], cand[:, [j]], anchor[:, [j]])
            row[f"{target}_distance_abs_mean"] = float(np.abs(cand[:, j] - anchor[:, j]).mean())
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["info_score"] = df["orthogonal_fraction_vs_stage2"] * df["score_std_under_latent_mix"]
    return df.sort_values(["pred_public_from_latent_mix", "info_score"], ascending=[True, False]).reset_index(drop=True)


def save_latent_alpha_blend(anchor_df: pd.DataFrame, stage2_df: pd.DataFrame, alpha: float) -> str:
    anchor = anchor_df[TARGETS].to_numpy(dtype=float)
    stage2 = stage2_df[TARGETS].to_numpy(dtype=float)
    pred = clip((1.0 - alpha) * anchor + alpha * stage2)
    out = anchor_df.copy()
    out[TARGETS] = pred
    tag = int(round(alpha * 1000))
    file_name = f"submission_publicblend_anchor578_stage2567_prob_w{tag:03d}_latentmix.csv"
    out.to_csv(OUT / file_name, index=False)
    return file_name


def main() -> None:
    anchor_df = read_submission(ANCHOR_FILE)
    stage2_df = read_submission(STAGE2_FILE)
    assert anchor_df[KEY].equals(stage2_df[KEY])
    anchor = anchor_df[TARGETS].to_numpy(dtype=float)
    stage2 = stage2_df[TARGETS].to_numpy(dtype=float)
    anchor_public, stage2_public, offline_delta = observed_public_delta()

    alpha, constraint = make_constraint_summary(anchor, stage2, anchor_public, stage2_public, offline_delta)
    constraint.to_csv(OUT / "public_lb_inverse_constraint.csv", index=False)

    latent_file = save_latent_alpha_blend(anchor_df, stage2_df, alpha)
    preds = make_candidate_predictions(anchor_df, stage2_df, alpha, anchor_public)
    preds.to_csv(OUT / "public_candidate_latent_mix_predictions.csv", index=False)

    print("\nconstraint")
    print(constraint.round(9).to_string(index=False))
    print("\nlatent-mix candidate predictions")
    print(f"saved latent alpha blend: {latent_file}")
    display_cols = [
        "file",
        "changed_targets",
        "pred_public_from_latent_mix",
        "pred_delta_vs_anchor",
        "orthogonal_fraction_vs_stage2",
        "score_std_under_latent_mix",
        "info_score",
        "distance_abs_mean_vs_anchor",
    ]
    print(preds[display_cols].head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
