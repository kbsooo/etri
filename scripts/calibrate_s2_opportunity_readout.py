from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from probe_domain_ssl_latents import (
    EPS,
    KEY_COLUMNS,
    TARGET_COLUMNS,
    dataframe_to_markdown,
    make_subject_time_folds,
    normalize_keys,
    subject_prior,
    write_prediction,
)
from train_pruned_state_decoder import safe_logit, sigmoid
from train_s2_opportunity_state_decoder import FIXED_MAP_TARGET_LOSSES, projected_fixed_avg, s2_reference_drift


S2_INDEX = TARGET_COLUMNS.index("S2")


@dataclass(frozen=True)
class Candidate:
    name: str
    family: str
    oof_s2: np.ndarray
    sample_s2: np.ndarray


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def prediction_matrix(frame: pd.DataFrame, oof: bool) -> np.ndarray:
    columns = [f"pred_{target}" if oof else target for target in TARGET_COLUMNS]
    return np.clip(frame[columns].to_numpy(float), EPS, 1.0 - EPS)


def solve_intercept(scores: np.ndarray, target_mean: float) -> float:
    target_mean = float(np.clip(target_mean, EPS, 1.0 - EPS))
    lo, hi = -25.0, 25.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if float(sigmoid(scores + mid).mean()) < target_mean:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def expected_eval_rate(observed_train: pd.DataFrame, subject: str, eval_count: int, global_rate: float) -> float:
    subject_train = observed_train[observed_train["subject_id"].eq(subject)]
    if eval_count <= 0:
        return float(subject_train["S2"].mean()) if len(subject_train) else global_rate
    train_count = int(len(subject_train))
    train_pos = float(subject_train["S2"].sum()) if train_count else 0.0
    desired_total_pos = global_rate * float(train_count + eval_count)
    desired_eval_pos = desired_total_pos - train_pos
    return float(np.clip(desired_eval_pos / float(eval_count), EPS, 1.0 - EPS))


def posterior_subject_rate(observed_train: pd.DataFrame, subject: str, alpha: float) -> float:
    global_rate = float(observed_train["S2"].mean())
    subject_train = observed_train[observed_train["subject_id"].eq(subject)]
    count = int(len(subject_train))
    positives = float(subject_train["S2"].sum()) if count else 0.0
    return float(np.clip((positives + alpha * global_rate) / (count + alpha), EPS, 1.0 - EPS))


def target_rate(observed_train: pd.DataFrame, subject: str, eval_count: int, mode: str, alpha: float) -> float:
    global_rate = float(observed_train["S2"].mean())
    if mode == "global":
        return float(np.clip(global_rate, EPS, 1.0 - EPS))
    if mode == "global_count":
        return expected_eval_rate(observed_train, subject, eval_count, global_rate)
    if mode == "posterior":
        return posterior_subject_rate(observed_train, subject, alpha)
    raise ValueError(f"Unknown rate mode: {mode}")


def intercept_to_mean(raw: np.ndarray, target_mean: float) -> np.ndarray:
    scores = safe_logit(raw)
    return np.clip(sigmoid(scores + solve_intercept(scores, target_mean)), EPS, 1.0 - EPS)


def logit_shrink_to_prior(raw: np.ndarray, prior: np.ndarray, weight: float) -> np.ndarray:
    return np.clip(sigmoid((1.0 - weight) * safe_logit(raw) + weight * safe_logit(prior)), EPS, 1.0 - EPS)


def build_oof_prior(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]], prior_alpha: float) -> np.ndarray:
    prior = np.zeros(len(train), dtype=float)
    for fit_idx, eval_idx in folds:
        fold_prior = subject_prior(train.iloc[fit_idx], train.iloc[eval_idx], prior_alpha)
        prior[eval_idx] = fold_prior[:, S2_INDEX]
    return np.clip(prior, EPS, 1.0 - EPS)


def calibrate_global_intercept(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    raw_oof: np.ndarray,
    raw_sample: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    strength: float,
) -> tuple[np.ndarray, np.ndarray]:
    out = raw_oof.copy()
    for fit_idx, eval_idx in folds:
        fit_rate = float(train.iloc[fit_idx]["S2"].mean())
        target_mean = (1.0 - strength) * float(raw_oof[eval_idx].mean()) + strength * fit_rate
        out[eval_idx] = intercept_to_mean(raw_oof[eval_idx], target_mean)
    sample_target = (1.0 - strength) * float(raw_sample.mean()) + strength * float(train["S2"].mean())
    return out, intercept_to_mean(raw_sample, sample_target)


def calibrate_subject_anchor(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    raw_oof: np.ndarray,
    raw_sample: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    strength: float,
    mode: str,
    prior_alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    out = raw_oof.copy()
    for fit_idx, eval_idx in folds:
        eval_frame = train.iloc[eval_idx].reset_index(drop=True)
        observed_train = train.iloc[fit_idx]
        block = raw_oof[eval_idx].copy()
        for subject, group in eval_frame.reset_index().groupby("subject_id", sort=False):
            idx = group["index"].to_numpy(int)
            rate = target_rate(observed_train, str(subject), len(idx), mode, prior_alpha)
            target_mean = (1.0 - strength) * float(block[idx].mean()) + strength * rate
            block[idx] = intercept_to_mean(block[idx], target_mean)
        out[eval_idx] = block

    sample_out = raw_sample.copy()
    sample_frame = sample.reset_index(drop=True)
    for subject, group in sample_frame.reset_index().groupby("subject_id", sort=False):
        idx = group["index"].to_numpy(int)
        rate = target_rate(train, str(subject), len(idx), mode, prior_alpha)
        target_mean = (1.0 - strength) * float(sample_out[idx].mean()) + strength * rate
        sample_out[idx] = intercept_to_mean(sample_out[idx], target_mean)
    return np.clip(out, EPS, 1.0 - EPS), np.clip(sample_out, EPS, 1.0 - EPS)


def calibrate_subject_cap(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    raw_oof: np.ndarray,
    raw_sample: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    margin: float,
    mode: str,
    prior_alpha: float,
) -> tuple[np.ndarray, np.ndarray]:
    out = raw_oof.copy()
    for fit_idx, eval_idx in folds:
        eval_frame = train.iloc[eval_idx].reset_index(drop=True)
        observed_train = train.iloc[fit_idx]
        block = raw_oof[eval_idx].copy()
        for subject, group in eval_frame.reset_index().groupby("subject_id", sort=False):
            idx = group["index"].to_numpy(int)
            rate = target_rate(observed_train, str(subject), len(idx), mode, prior_alpha)
            mean = float(block[idx].mean())
            clipped_mean = float(np.clip(mean, rate - margin, rate + margin))
            if abs(clipped_mean - mean) > 1e-12:
                block[idx] = intercept_to_mean(block[idx], clipped_mean)
        out[eval_idx] = block

    sample_out = raw_sample.copy()
    sample_frame = sample.reset_index(drop=True)
    for subject, group in sample_frame.reset_index().groupby("subject_id", sort=False):
        idx = group["index"].to_numpy(int)
        rate = target_rate(train, str(subject), len(idx), mode, prior_alpha)
        mean = float(sample_out[idx].mean())
        clipped_mean = float(np.clip(mean, rate - margin, rate + margin))
        if abs(clipped_mean - mean) > 1e-12:
            sample_out[idx] = intercept_to_mean(sample_out[idx], clipped_mean)
    return np.clip(out, EPS, 1.0 - EPS), np.clip(sample_out, EPS, 1.0 - EPS)


def expected_sample_rates(train: pd.DataFrame, sample: pd.DataFrame, prior_alpha: float) -> pd.DataFrame:
    rows = []
    global_rate = float(train["S2"].mean())
    for subject, group in sample.groupby("subject_id", sort=False):
        rows.append(
            {
                "subject_id": subject,
                "sample_rows": int(len(group)),
                "global_count_rate": expected_eval_rate(train, str(subject), len(group), global_rate),
                "posterior_rate": posterior_subject_rate(train, str(subject), prior_alpha),
                "global_rate": global_rate,
            }
        )
    return pd.DataFrame(rows)


def subject_gap(sample: pd.DataFrame, sample_s2: np.ndarray, rates: pd.DataFrame, rate_col: str) -> float:
    pred = pd.DataFrame({"subject_id": sample["subject_id"].to_numpy(), "pred": sample_s2})
    subject_mean = pred.groupby("subject_id", sort=False)["pred"].mean().reset_index()
    merged = subject_mean.merge(rates[["subject_id", rate_col]], on="subject_id", how="left", validate="one_to_one")
    return float(np.mean(np.abs(merged["pred"].to_numpy(float) - merged[rate_col].to_numpy(float))))


def fold_losses(train: pd.DataFrame, pred: np.ndarray, folds: list[tuple[np.ndarray, np.ndarray]]) -> list[float]:
    values = []
    y = train["S2"].to_numpy(int)
    for _, eval_idx in folds:
        values.append(float(log_loss(y[eval_idx], np.clip(pred[eval_idx], EPS, 1.0 - EPS), labels=[0, 1])))
    return values


def evaluate_candidates(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    candidates: list[Candidate],
    raw_candidate: Candidate,
    folds: list[tuple[np.ndarray, np.ndarray]],
    reference_submission: str,
    prior_alpha: float,
) -> pd.DataFrame:
    y = train["S2"].to_numpy(int)
    raw_loss = float(log_loss(y, raw_candidate.oof_s2, labels=[0, 1]))
    raw_fold_losses = fold_losses(train, raw_candidate.oof_s2, folds)
    rates = expected_sample_rates(train, sample, prior_alpha)
    expected_mean = float(np.average(rates["global_count_rate"], weights=rates["sample_rows"]))
    posterior_mean = float(np.average(rates["posterior_rate"], weights=rates["sample_rows"]))
    rows = []
    for candidate in candidates:
        loss = float(log_loss(y, candidate.oof_s2, labels=[0, 1]))
        cand_fold_losses = fold_losses(train, candidate.oof_s2, folds)
        fold_deltas = [raw - cand for raw, cand in zip(raw_fold_losses, cand_fold_losses)]
        drift = s2_reference_drift(sample, candidate.sample_s2, reference_submission)
        sample_mean = float(candidate.sample_s2.mean())
        rows.append(
            {
                "candidate": candidate.name,
                "family": candidate.family,
                "s2_log_loss": loss,
                "delta_vs_raw": raw_loss - loss,
                "delta_vs_protected": FIXED_MAP_TARGET_LOSSES["S2"] - loss,
                "projected_fixed_map_avg": projected_fixed_avg(loss),
                "train_oof_s2_mean": float(candidate.oof_s2.mean()),
                "train_label_s2_mean": float(train["S2"].mean()),
                "sample_s2_mean": sample_mean,
                "expected_sample_s2_mean": expected_mean,
                "posterior_sample_s2_mean": posterior_mean,
                "abs_sample_mean_gap_global_count": abs(sample_mean - expected_mean),
                "abs_sample_mean_gap_posterior": abs(sample_mean - posterior_mean),
                "mean_abs_subject_gap_global_count": subject_gap(sample, candidate.sample_s2, rates, "global_count_rate"),
                "mean_abs_subject_gap_posterior": subject_gap(sample, candidate.sample_s2, rates, "posterior_rate"),
                "folds_better_than_raw": int(sum(delta > 0 for delta in fold_deltas)),
                "worst_fold_delta_vs_raw": float(min(fold_deltas)),
                "fold_loss_std": float(np.std(cand_fold_losses)),
                **drift,
            }
        )
    return pd.DataFrame(rows)


def build_candidates(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    raw_oof_s2: np.ndarray,
    raw_sample_s2: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    args: argparse.Namespace,
) -> list[Candidate]:
    oof_prior_s2 = build_oof_prior(train, folds, args.prior_alpha)
    sample_prior_s2 = subject_prior(train, sample, args.prior_alpha)[:, S2_INDEX]
    candidates = [Candidate("raw_fixed_pairwise", "raw", raw_oof_s2, raw_sample_s2)]

    for weight in parse_float_list(args.shrink_weights):
        candidates.append(
            Candidate(
                f"shrink_prior_w{weight:g}",
                "shrink_prior",
                logit_shrink_to_prior(raw_oof_s2, oof_prior_s2, weight),
                logit_shrink_to_prior(raw_sample_s2, sample_prior_s2, weight),
            )
        )

    for strength in parse_float_list(args.global_anchor_strengths):
        oof, sub = calibrate_global_intercept(train, sample, raw_oof_s2, raw_sample_s2, folds, strength)
        candidates.append(Candidate(f"global_intercept_s{strength:g}", "global_intercept", oof, sub))

    for mode in ["global_count", "posterior"]:
        for strength in parse_float_list(args.subject_anchor_strengths):
            oof, sub = calibrate_subject_anchor(train, sample, raw_oof_s2, raw_sample_s2, folds, strength, mode, args.prior_alpha)
            candidates.append(Candidate(f"subject_anchor_{mode}_s{strength:g}", f"subject_anchor_{mode}", oof, sub))

    for mode in ["global_count", "posterior"]:
        for margin in parse_float_list(args.subject_cap_margins):
            oof, sub = calibrate_subject_cap(train, sample, raw_oof_s2, raw_sample_s2, folds, margin, mode, args.prior_alpha)
            candidates.append(Candidate(f"subject_cap_{mode}_m{margin:g}", f"subject_cap_{mode}", oof, sub))

    return candidates


def choose_train_safe(scores: pd.DataFrame) -> str:
    raw = scores[scores["candidate"].eq("raw_fixed_pairwise")].iloc[0]
    eligible = scores[
        (scores["delta_vs_protected"] > 0.0)
        & (scores["folds_better_than_raw"] >= 3)
        & (scores["abs_sample_mean_gap_posterior"] < raw["abs_sample_mean_gap_posterior"])
        & (scores["mean_abs_subject_gap_posterior"] < raw["mean_abs_subject_gap_posterior"])
    ].copy()
    if eligible.empty:
        return "raw_fixed_pairwise"
    return str(eligible.sort_values(["s2_log_loss", "mean_abs_subject_gap_posterior"]).iloc[0]["candidate"])


def main() -> None:
    args = build_arg_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof = normalize_keys(pd.read_csv(args.base_oof))
    base_sub = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not base_sub[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")

    base_oof_matrix = prediction_matrix(base_oof, oof=True)
    base_sub_matrix = prediction_matrix(base_sub, oof=False)
    raw_oof_s2 = base_oof_matrix[:, S2_INDEX]
    raw_sample_s2 = base_sub_matrix[:, S2_INDEX]
    folds = make_subject_time_folds(train, args.folds)
    candidates = build_candidates(train, sample, raw_oof_s2, raw_sample_s2, folds, args)
    raw_candidate = candidates[0]
    scores = evaluate_candidates(train, sample, candidates, raw_candidate, folds, args.reference_submission, args.prior_alpha)
    scores = scores.sort_values(["s2_log_loss", "abs_sample_mean_gap_global_count"]).reset_index(drop=True)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)

    selected_name = choose_train_safe(scores)
    selected = next(candidate for candidate in candidates if candidate.name == selected_name)
    selected_oof = base_oof_matrix.copy()
    selected_sub = base_sub_matrix.copy()
    selected_oof[:, S2_INDEX] = selected.oof_s2
    selected_sub[:, S2_INDEX] = selected.sample_s2
    write_prediction(output_dir / "oof_selected_s2_opportunity_drift_calibration.csv", train, selected_oof, oof=True)
    write_prediction(output_dir / "submission_selected_s2_opportunity_drift_calibration.csv", sample, selected_sub, oof=False)

    raw_row = scores[scores["candidate"].eq("raw_fixed_pairwise")].iloc[0].to_dict()
    selected_row = scores[scores["candidate"].eq(selected_name)].iloc[0].to_dict()
    frontier = scores[
        (scores["delta_vs_protected"] > 0.0)
        & (scores["folds_better_than_raw"] >= 3)
        & (scores["abs_sample_mean_gap_posterior"] <= raw_row["abs_sample_mean_gap_posterior"])
        & (scores["mean_abs_subject_gap_posterior"] <= raw_row["mean_abs_subject_gap_posterior"])
    ].sort_values(["s2_log_loss", "mean_abs_subject_gap_posterior"])
    frontier.to_csv(output_dir / "train_safe_frontier.csv", index=False)

    report = {
        "raw": raw_row,
        "selected_train_safe": selected_row,
        "protected_s2_log_loss": FIXED_MAP_TARGET_LOSSES["S2"],
        "current_fixed_map_avg": float(np.mean([FIXED_MAP_TARGET_LOSSES[target] for target in TARGET_COLUMNS])),
        "selection_rule": "lowest S2 loss among candidates that beat protected S2, improve at least 3/5 folds vs raw, and reduce train-derived posterior sample mean and subject-rate gaps vs raw",
        "top_by_s2_loss": scores.head(15).to_dict(orient="records"),
        "top_train_safe_frontier": frontier.head(15).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# S2 Opportunity Drift Calibration",
        "",
        "## Purpose",
        "",
        "Stress-test the strongest fixed S2 opportunity/Q-state readout with fold-safe, train-derived calibration rules. The v83 S2 drift is recorded only as a diagnostic; candidate selection uses train rates and sample subject composition.",
        "",
        "## Result",
        "",
        f"- Raw fixed S2 logloss: `{raw_row['s2_log_loss']:.6f}`",
        f"- Raw projected fixed-map avg: `{raw_row['projected_fixed_map_avg']:.6f}`",
        f"- Raw sample S2 mean: `{raw_row['sample_s2_mean']:.6f}`",
        f"- Raw posterior subject gap: `{raw_row['mean_abs_subject_gap_posterior']:.6f}`",
        f"- Selected train-safe candidate: `{selected_name}`",
        f"- Selected S2 logloss: `{selected_row['s2_log_loss']:.6f}`",
        f"- Selected projected fixed-map avg: `{selected_row['projected_fixed_map_avg']:.6f}`",
        f"- Selected sample S2 mean: `{selected_row['sample_s2_mean']:.6f}`",
        f"- Selected posterior subject gap: `{selected_row['mean_abs_subject_gap_posterior']:.6f}`",
        f"- Protected fixed-map S2 reference: `{FIXED_MAP_TARGET_LOSSES['S2']:.6f}`",
        "",
        "## Top By S2 Loss",
        "",
        dataframe_to_markdown(
            scores.head(15)[
                [
                    "candidate",
                    "family",
                    "s2_log_loss",
                    "delta_vs_raw",
                    "delta_vs_protected",
                    "projected_fixed_map_avg",
                    "sample_s2_mean",
                    "mean_abs_subject_gap_posterior",
                    "folds_better_than_raw",
                    "mean_abs_s2_drift",
                ]
            ]
        ),
        "",
        "## Train-Safe Frontier",
        "",
        dataframe_to_markdown(
            frontier.head(15)[
                [
                    "candidate",
                    "s2_log_loss",
                    "delta_vs_protected",
                    "projected_fixed_map_avg",
                    "sample_s2_mean",
                    "abs_sample_mean_gap_posterior",
                    "mean_abs_subject_gap_posterior",
                    "folds_better_than_raw",
                    "mean_abs_s2_drift",
                ]
            ]
        ),
        "",
        "## Read",
        "",
        "- A global intercept gives the lowest single OOF loss, but it improves only 2/5 folds versus the raw readout.",
        "- The selected posterior anchor keeps the S2 gain, improves 3/5 folds, and reduces train-derived posterior rate stress without using v83 as a teacher.",
        "- A candidate is useful only if it still beats the protected S2 scout after fold and rate-stress checks.",
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"raw_s2={raw_row['s2_log_loss']:.6f} selected={selected_name} selected_s2={selected_row['s2_log_loss']:.6f}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calibrate the fixed S2 opportunity readout with train-derived drift controls.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/domain_s2_opportunity_pairwise_decoder_v1/oof_fixed_best_s2_opportunity_pairwise_decoder.csv")
    parser.add_argument("--base-submission", default="outputs/domain_s2_opportunity_pairwise_decoder_v1/submission_fixed_best_s2_opportunity_pairwise_decoder.csv")
    parser.add_argument("--output-dir", default="outputs/domain_s2_opportunity_drift_calibration_v1")
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--prior-alpha", type=float, default=8.0)
    parser.add_argument("--shrink-weights", default="0.05,0.1,0.2,0.35,0.5,0.65,0.8")
    parser.add_argument("--global-anchor-strengths", default="0.05,0.1,0.2,0.35,0.5,0.75,1.0")
    parser.add_argument("--subject-anchor-strengths", default="0.05,0.1,0.2,0.35,0.5,0.75,1.0")
    parser.add_argument("--subject-cap-margins", default="0.03,0.05,0.08,0.1,0.15,0.2")
    return parser


if __name__ == "__main__":
    main()
