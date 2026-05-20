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


@dataclass(frozen=True)
class ForwardSpec:
    half_life: float
    alpha: float
    weight: float
    mode: str
    direction: str

    @property
    def name(self) -> str:
        return f"{self.direction}_h{self.half_life:g}_a{self.alpha:g}_w{self.weight:g}_{self.mode}"


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


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {
        target: float(log_loss(y[target].to_numpy(), np.clip(pred[:, target_i], EPS, 1.0 - EPS), labels=[0, 1]))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    return float(np.mean(list(per_target.values()))), per_target


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, target_i], labels=[0, 1]))


def prior_for_frame(
    source: pd.DataFrame,
    eval_frame: pd.DataFrame,
    target: str,
    half_life: float,
    alpha: float,
    direction: str,
) -> np.ndarray:
    global_rate = float(source[target].mean())
    decay = np.log(2.0) / max(half_life, 1e-6)
    grouped = {
        str(subject): group.sort_values(["_date_ord", "sleep_date"]).reset_index(drop=True)
        for subject, group in source.groupby("subject_id", sort=False)
    }
    prior = np.zeros(len(eval_frame), dtype=float)
    for out_i, (_, row) in enumerate(eval_frame.iterrows()):
        subject = str(row["subject_id"])
        date_ord = float(row["_date_ord"])
        group = grouped.get(subject)
        if group is None or group.empty:
            prior[out_i] = global_rate
            continue
        dates = group["_date_ord"].to_numpy(dtype=float)
        labels = group[target].to_numpy(dtype=float)
        gaps = date_ord - dates
        if direction == "forward":
            mask = gaps > 0
            distances = gaps
        elif direction == "bidirectional":
            mask = gaps != 0
            distances = np.abs(gaps)
        else:
            raise ValueError(f"Unknown prior direction: {direction}")
        if not mask.any():
            prior[out_i] = global_rate
            continue
        weights = np.exp(-decay * distances[mask])
        num = float((weights * labels[mask]).sum() + alpha * global_rate)
        den = float(weights.sum() + alpha)
        prior[out_i] = num / den
    return np.clip(prior, EPS, 1.0 - EPS)


def build_forward_prior(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    half_life: float,
    alpha: float,
    direction: str,
) -> tuple[np.ndarray, np.ndarray]:
    train_prior = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    test_prior = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        for train_idx, val_idx in folds:
            source = train.iloc[train_idx].reset_index(drop=True)
            eval_frame = train.iloc[val_idx].reset_index(drop=True)
            train_prior[val_idx, target_i] = prior_for_frame(source, eval_frame, target, half_life, alpha, direction)
        test_prior[:, target_i] = prior_for_frame(train, sample, target, half_life, alpha, direction)
    return np.clip(train_prior, EPS, 1.0 - EPS), np.clip(test_prior, EPS, 1.0 - EPS)


def blend_predictions(base: np.ndarray, prior: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        out = (1.0 - weight) * base + weight * prior
    elif mode == "logit":
        out = sigmoid((1.0 - weight) * safe_logit(base) + weight * safe_logit(prior))
    else:
        raise ValueError(f"Unknown blend mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(display.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy()]
    return "\n".join([header, separator, *rows])


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = add_date_ord(normalize_keys(pd.read_csv(args.train_path))).reset_index(drop=True)
    sample = add_date_ord(normalize_keys(pd.read_csv(args.sample_path))).reset_index(drop=True)
    base_oof, base_submission = load_base_predictions(args, train, sample)
    y = train[TARGET_COLUMNS]
    folds = make_subject_time_folds(train, args.folds)

    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    specs = [
        ForwardSpec(half_life, alpha, weight, mode, direction)
        for half_life in parse_float_list(args.half_lives)
        for alpha in parse_float_list(args.alphas)
        for weight in parse_float_list(args.weights)
        for mode in parse_str_list(args.modes)
        for direction in parse_str_list(args.directions)
    ]
    prior_cache: dict[tuple[float, float, str], tuple[np.ndarray, np.ndarray]] = {}
    pred_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    rows = []
    best_by_target: dict[str, dict] = {}

    for spec_i, spec in enumerate(specs, start=1):
        key = (spec.half_life, spec.alpha, spec.direction)
        if key not in prior_cache:
            print(f"[prior {len(prior_cache) + 1}] direction={spec.direction} half_life={spec.half_life:g} alpha={spec.alpha:g}")
            prior_cache[key] = build_forward_prior(train, sample, folds, spec.half_life, spec.alpha, spec.direction)
        prior_oof, prior_submission = prior_cache[key]
        blended_oof = blend_predictions(base_oof, prior_oof, spec.weight, spec.mode)
        blended_submission = blend_predictions(base_submission, prior_submission, spec.weight, spec.mode)
        pred_cache[spec.name] = (blended_oof, blended_submission)
        avg, per_target = average_loss(y, blended_oof)
        rows.append(
            {
                "name": spec.name,
                "half_life": spec.half_life,
                "alpha": spec.alpha,
                "weight": spec.weight,
                "mode": spec.mode,
                "avg_log_loss": avg,
                **per_target,
            }
        )
        for target_i, target in enumerate(TARGET_COLUMNS):
            value = per_target[target]
            current = best_by_target.get(target)
            if current is None or value < current["log_loss"]:
                folds_improved = sum(
                    target_loss(y, blended_oof, target_i, val_idx) < base_fold_target[target][fold_i]
                    for fold_i, (_, val_idx) in enumerate(folds)
                )
                best_by_target[target] = {
                    "target": target,
                    "log_loss": value,
                    "base_log_loss": base_targets[target],
                    "delta_vs_base": base_targets[target] - value,
                    "candidate": spec.name,
                    "half_life": spec.half_life,
                    "alpha": spec.alpha,
                    "weight": spec.weight,
                    "mode": spec.mode,
                    "direction": spec.direction,
                    "folds_improved": int(folds_improved),
                }

    final_oof = base_oof.copy()
    final_submission = base_submission.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target[target]
        used = selected["delta_vs_base"] >= args.min_delta and selected["folds_improved"] >= args.min_target_folds_improved
        if used:
            final_oof[:, target_i] = pred_cache[selected["candidate"]][0][:, target_i]
            final_submission[:, target_i] = pred_cache[selected["candidate"]][1][:, target_i]
        selection_rows.append({**selected, "used": bool(used)})

    scores = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    selection = pd.DataFrame(selection_rows)
    final_avg, final_targets = average_loss(y, final_oof)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection.to_csv(output_dir / "targetwise_forward_prior_selection.csv", index=False)

    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_forward_label_prior.csv"
    oof.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_forward_label_prior.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "top_candidates": scores.head(20).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "forward_label_prior_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Forward Label Prior Report",
        "",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Final avg logloss: `{final_avg:.6f}`",
        f"- Target promotion rule: delta >= `{args.min_delta:g}` and improved folds >= `{args.min_target_folds_improved}/{args.folds}`",
        "",
        "## Selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top Candidates",
        "",
        dataframe_to_markdown(scores.head(12)),
        "",
    ]
    (output_dir / "forward_label_prior_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forward-only same-subject label prior blended into a base probability candidate.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/multi_signal_qcount_blend_w015_020_015_015/oof_multi_signal_qcount_blend.csv")
    parser.add_argument("--base-submission", default="outputs/multi_signal_qcount_blend_w015_020_015_015/submission_multi_signal_qcount_blend.csv")
    parser.add_argument("--output-dir", default="outputs/forward_label_prior")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--half-lives", default="1,2,3,5,7,14,28")
    parser.add_argument("--alphas", default="0.5,1,2,5,10,20")
    parser.add_argument("--weights", default="0.01,0.02,0.03,0.05,0.08,0.1,0.15,0.2,0.3")
    parser.add_argument("--modes", default="prob,logit")
    parser.add_argument("--directions", default="forward")
    parser.add_argument("--min-target-folds-improved", type=int, default=3)
    parser.add_argument("--min-delta", type=float, default=0.00001)
    return parser.parse_args()


if __name__ == "__main__":
    main()
