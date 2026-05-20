from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5
GAP_BINS = (1.5, 3.5, 7.5, np.inf)


@dataclass(frozen=True)
class PriorSpec:
    bandwidth: float
    subject_alpha: float
    transition_mix: float
    blend_weight: float
    blend_mode: str

    @property
    def name(self) -> str:
        return (
            f"markov_bw{self.bandwidth:g}"
            f"_a{self.subject_alpha:g}"
            f"_tm{self.transition_mix:g}"
            f"_bwgt{self.blend_weight:g}"
            f"_{self.blend_mode}"
        )


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def add_date_ord(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["_date_ord"] = pd.to_datetime(out["lifelog_date"]).map(pd.Timestamp.toordinal).astype(float)
    return out


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame))
    return [
        (np.setdiff1d(all_idx, np.array(sorted(indices), dtype=int)), np.array(sorted(indices), dtype=int))
        for indices in val_indices
    ]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_base_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    oof = normalize_keys(pd.read_csv(args.base_oof))
    submission = normalize_keys(pd.read_csv(args.base_submission))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")
    return prediction_matrix(oof), submission_matrix(submission)


def gap_bin(gap: float) -> int:
    return int(np.searchsorted(GAP_BINS, gap, side="left"))


def smoothed_rate(successes: float, total: float, alpha: float, prior: float) -> float:
    return float((successes + alpha * prior) / (total + alpha))


def estimate_tables(source: pd.DataFrame, target: str, alpha: float) -> dict[str, object]:
    global_rate = float(source[target].mean())
    subject_rates = {
        str(subject): smoothed_rate(float(group[target].sum()), float(len(group)), alpha, global_rate)
        for subject, group in source.groupby("subject_id", sort=False)
    }
    n_bins = len(GAP_BINS)
    prev_counts = np.zeros((n_bins, 2, 2), dtype=float)
    next_counts = np.zeros((n_bins, 2, 2), dtype=float)
    both_counts = np.zeros((n_bins, 2, 2, 2), dtype=float)

    for _, group in source.sort_values(["subject_id", "_date_ord"]).groupby("subject_id", sort=False):
        dates = group["_date_ord"].to_numpy(dtype=float)
        labels = group[target].to_numpy(dtype=int)
        if len(group) < 2:
            continue
        for pos in range(1, len(group)):
            gap = max(1.0, float(dates[pos] - dates[pos - 1]))
            b = gap_bin(gap)
            prev_label = int(labels[pos - 1])
            current_label = int(labels[pos])
            prev_counts[b, prev_label, current_label] += 1.0
        for pos in range(len(group) - 1):
            gap = max(1.0, float(dates[pos + 1] - dates[pos]))
            b = gap_bin(gap)
            current_label = int(labels[pos])
            next_label = int(labels[pos + 1])
            next_counts[b, next_label, current_label] += 1.0
        for pos in range(1, len(group) - 1):
            gap = max(float(dates[pos] - dates[pos - 1]), float(dates[pos + 1] - dates[pos]), 1.0)
            b = gap_bin(gap)
            prev_label = int(labels[pos - 1])
            next_label = int(labels[pos + 1])
            current_label = int(labels[pos])
            both_counts[b, prev_label, next_label, current_label] += 1.0

    prev_rates = np.zeros((n_bins, 2), dtype=float)
    next_rates = np.zeros((n_bins, 2), dtype=float)
    both_rates = np.zeros((n_bins, 2, 2), dtype=float)
    prev_support = prev_counts.sum(axis=2)
    next_support = next_counts.sum(axis=2)
    both_support = both_counts.sum(axis=3)
    for b in range(n_bins):
        for label in range(2):
            prev_rates[b, label] = smoothed_rate(prev_counts[b, label, 1], prev_support[b, label], alpha, global_rate)
            next_rates[b, label] = smoothed_rate(next_counts[b, label, 1], next_support[b, label], alpha, global_rate)
            for next_label in range(2):
                both_rates[b, label, next_label] = smoothed_rate(
                    both_counts[b, label, next_label, 1],
                    both_support[b, label, next_label],
                    alpha,
                    global_rate,
                )
    return {
        "global_rate": global_rate,
        "subject_rates": subject_rates,
        "prev_rates": prev_rates,
        "next_rates": next_rates,
        "both_rates": both_rates,
        "prev_support": prev_support,
        "next_support": next_support,
        "both_support": both_support,
    }


def target_prior(
    source: pd.DataFrame,
    eval_frame: pd.DataFrame,
    target: str,
    bandwidth: float,
    subject_alpha: float,
    transition_mix: float,
) -> np.ndarray:
    tables = estimate_tables(source, target, subject_alpha)
    global_rate = float(tables["global_rate"])
    subject_rates: dict[str, float] = tables["subject_rates"]  # type: ignore[assignment]
    prev_rates: np.ndarray = tables["prev_rates"]  # type: ignore[assignment]
    next_rates: np.ndarray = tables["next_rates"]  # type: ignore[assignment]
    both_rates: np.ndarray = tables["both_rates"]  # type: ignore[assignment]
    prev_support: np.ndarray = tables["prev_support"]  # type: ignore[assignment]
    next_support: np.ndarray = tables["next_support"]  # type: ignore[assignment]
    both_support: np.ndarray = tables["both_support"]  # type: ignore[assignment]
    grouped = {
        str(subject): group.sort_values("_date_ord").reset_index(drop=True)
        for subject, group in source.groupby("subject_id", sort=False)
    }

    priors = np.empty(len(eval_frame), dtype=float)
    for out_i, (_, row) in enumerate(eval_frame.iterrows()):
        subject = str(row["subject_id"])
        date_ord = float(row["_date_ord"])
        subject_rate = float(subject_rates.get(subject, global_rate))
        group = grouped.get(subject)
        if group is None or group.empty:
            priors[out_i] = subject_rate
            continue

        dates = group["_date_ord"].to_numpy(dtype=float)
        labels = group[target].to_numpy(dtype=float)
        signed = dates - date_ord
        abs_dist = np.abs(signed)
        weights = np.exp(-abs_dist / bandwidth)
        weight_sum = float(weights.sum())
        kernel_rate = subject_rate if weight_sum <= 1e-12 else float((weights * labels).sum() / weight_sum)

        transition_logits = [safe_logit(np.array([subject_rate]))[0]]
        transition_weights = [max(1.0, min(float(len(group)), subject_alpha))]

        prev_mask = signed < 0
        next_mask = signed > 0
        prev_label = None
        next_label = None
        prev_gap = None
        next_gap = None
        if prev_mask.any():
            prev_pos = np.where(prev_mask)[0][np.argmin(abs_dist[prev_mask])]
            prev_label = int(labels[prev_pos])
            prev_gap = max(1.0, float(abs_dist[prev_pos]))
            b = gap_bin(prev_gap)
            transition_logits.append(safe_logit(np.array([prev_rates[b, prev_label]]))[0])
            transition_weights.append(float(prev_support[b, prev_label] + subject_alpha))
        if next_mask.any():
            next_pos = np.where(next_mask)[0][np.argmin(abs_dist[next_mask])]
            next_label = int(labels[next_pos])
            next_gap = max(1.0, float(abs_dist[next_pos]))
            b = gap_bin(next_gap)
            transition_logits.append(safe_logit(np.array([next_rates[b, next_label]]))[0])
            transition_weights.append(float(next_support[b, next_label] + subject_alpha))
        if prev_label is not None and next_label is not None and prev_gap is not None and next_gap is not None:
            b = gap_bin(max(prev_gap, next_gap))
            transition_logits.append(safe_logit(np.array([both_rates[b, prev_label, next_label]]))[0])
            transition_weights.append(float(both_support[b, prev_label, next_label] + subject_alpha))

        transition_logit = float(np.average(transition_logits, weights=np.asarray(transition_weights, dtype=float)))
        transition_rate = float(sigmoid(np.array([transition_logit]))[0])
        mixed_logit = (
            transition_mix * safe_logit(np.array([transition_rate]))[0]
            + (1.0 - transition_mix) * safe_logit(np.array([kernel_rate]))[0]
        )
        priors[out_i] = float(sigmoid(np.array([mixed_logit]))[0])
    return np.clip(priors, EPS, 1.0 - EPS)


def build_prior_matrices(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    bandwidth: float,
    subject_alpha: float,
    transition_mix: float,
) -> tuple[np.ndarray, np.ndarray]:
    oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    test = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for train_idx, val_idx in folds:
            source = train.iloc[train_idx].reset_index(drop=True)
            val_frame = train.iloc[val_idx].reset_index(drop=True)
            oof[val_idx, target_i] = target_prior(source, val_frame, target, bandwidth, subject_alpha, transition_mix)
        test[:, target_i] = target_prior(train, sample, target, bandwidth, subject_alpha, transition_mix)
    return np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS)


def blend_predictions(base: np.ndarray, prior: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        blended = (1.0 - weight) * base + weight * prior
    elif mode == "logit":
        blended = sigmoid((1.0 - weight) * safe_logit(base) + weight * safe_logit(prior))
    else:
        raise ValueError(f"Unknown blend mode: {mode}")
    return np.clip(blended, EPS, 1.0 - EPS)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, target_i], labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda v: "" if pd.isna(v) else f"{v:.6f}")
        else:
            display[col] = display[col].map(lambda v: "" if pd.isna(v) else str(v))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *body])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = add_date_ord(normalize_keys(pd.read_csv(args.train_path)))
    sample = add_date_ord(normalize_keys(pd.read_csv(args.sample_path)))
    base_oof, base_test = load_base_predictions(args, train, sample)
    folds = make_subject_time_folds(train, args.folds)
    y = train[TARGET_COLUMNS]
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    specs = [
        PriorSpec(bandwidth, subject_alpha, transition_mix, blend_weight, blend_mode)
        for bandwidth in parse_float_list(args.bandwidths)
        for subject_alpha in parse_float_list(args.subject_alphas)
        for transition_mix in parse_float_list(args.transition_mixes)
        for blend_weight in parse_float_list(args.blend_weights)
        for blend_mode in parse_str_list(args.blend_modes)
    ]

    prior_cache: dict[tuple[float, float, float], tuple[np.ndarray, np.ndarray]] = {}
    pred_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    candidate_rows = []
    best_by_target: dict[str, dict] = {}
    for spec_i, spec in enumerate(specs, start=1):
        key = (spec.bandwidth, spec.subject_alpha, spec.transition_mix)
        if key not in prior_cache:
            print(f"[prior {len(prior_cache) + 1}] bandwidth={spec.bandwidth:g} alpha={spec.subject_alpha:g} mix={spec.transition_mix:g}")
            prior_cache[key] = build_prior_matrices(train, sample, folds, spec.bandwidth, spec.subject_alpha, spec.transition_mix)
        prior_oof, prior_test = prior_cache[key]
        blended_oof = blend_predictions(base_oof, prior_oof, spec.blend_weight, spec.blend_mode)
        blended_test = blend_predictions(base_test, prior_test, spec.blend_weight, spec.blend_mode)
        pred_cache[spec.name] = (blended_oof, blended_test)
        avg, per_target = average_loss(y, blended_oof)
        candidate_rows.append(
            {
                "name": spec.name,
                "bandwidth": spec.bandwidth,
                "subject_alpha": spec.subject_alpha,
                "transition_mix": spec.transition_mix,
                "blend_weight": spec.blend_weight,
                "blend_mode": spec.blend_mode,
                "avg_log_loss": avg,
                **per_target,
            }
        )
        for target_i, target in enumerate(TARGET_COLUMNS):
            value = per_target[target]
            current = best_by_target.get(target)
            if current is None or value < current["log_loss"]:
                folds_improved = 0
                for fold_i, (_, val_idx) in enumerate(folds):
                    cand_fold = target_loss(y, blended_oof, target_i, val_idx)
                    folds_improved += int(cand_fold < base_fold_target[target][fold_i])
                best_by_target[target] = {
                    "target": target,
                    "log_loss": value,
                    "base_log_loss": base_targets[target],
                    "delta_vs_base": base_targets[target] - value,
                    "candidate": spec.name,
                    "bandwidth": spec.bandwidth,
                    "subject_alpha": spec.subject_alpha,
                    "transition_mix": spec.transition_mix,
                    "blend_weight": spec.blend_weight,
                    "blend_mode": spec.blend_mode,
                    "folds_improved": folds_improved,
                }
        if spec_i % 50 == 0:
            print(f"evaluated {spec_i}/{len(specs)} specs")

    final_oof = base_oof.copy()
    final_test = base_test.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        used = selected["delta_vs_base"] >= args.min_delta and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = pred_cache[selected["candidate"]][0][:, target_i]
            final_test[:, target_i] = pred_cache[selected["candidate"]][1][:, target_i]
        selection_rows.append({**selected, "used": bool(used)})

    candidate_scores = pd.DataFrame(candidate_rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selection_rows)
    final_avg, final_targets = average_loss(y, final_oof)
    candidate_scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_markov_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_markov_label_prior.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_test[:, target_i]
    submission_path = output_dir / "submission_markov_label_prior.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "top_candidates": candidate_scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "markov_label_prior_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Markov Label Prior Report",
        "",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Final avg logloss: `{final_avg:.6f}`",
        f"- Candidate specs evaluated: `{len(specs)}`",
        f"- Target promotion rule: delta >= `{args.min_delta:g}` and improved folds >= `{args.min_target_folds_improved}/{args.folds}`",
        "",
        "## Selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top Candidates",
        "",
        dataframe_to_markdown(candidate_scores.head(12)),
        "",
    ]
    (output_dir / "markov_label_prior_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {oof_path}")
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe same-subject Markov label prior blended into base predictions.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--output-dir", default="outputs/markov_label_prior")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bandwidths", default="1,2,3,5,7,14")
    parser.add_argument("--subject-alphas", default="2,5,10,20")
    parser.add_argument("--transition-mixes", default="0.25,0.5,0.75,1.0")
    parser.add_argument("--blend-weights", default="0.05,0.1,0.2,0.3,0.5,0.7,1.0")
    parser.add_argument("--blend-modes", default="prob,logit")
    parser.add_argument("--min-target-folds-improved", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.00005)
    return parser.parse_args()


if __name__ == "__main__":
    main()
