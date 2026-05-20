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
class CalSpec:
    mode: str
    strength: float
    beta: float

    @property
    def name(self) -> str:
        return f"{self.mode}_s{self.strength:g}_b{self.beta:g}"


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40.0, 40.0)))


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


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


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS]), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


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


def expected_eval_rate(observed_train: pd.DataFrame, subject: str, target: str, eval_count: int, global_rate: float) -> float:
    subject_train = observed_train[observed_train["subject_id"].eq(subject)]
    if eval_count <= 0:
        return float(subject_train[target].mean()) if len(subject_train) else global_rate
    train_count = int(len(subject_train))
    train_pos = float(subject_train[target].sum()) if train_count else 0.0
    desired_total_pos = global_rate * float(train_count + eval_count)
    desired_eval_pos = desired_total_pos - train_pos
    return float(np.clip(desired_eval_pos / float(eval_count), EPS, 1.0 - EPS))


def target_rate(
    observed_train: pd.DataFrame,
    subject: str,
    target: str,
    eval_count: int,
    mode: str,
) -> float:
    global_rate = float(observed_train[target].mean())
    subject_train = observed_train[observed_train["subject_id"].eq(subject)]
    subject_rate = float(subject_train[target].mean()) if len(subject_train) else global_rate
    if mode == "global_count":
        return expected_eval_rate(observed_train, subject, target, eval_count, global_rate)
    if mode == "subject_rate":
        return float(np.clip(subject_rate, EPS, 1.0 - EPS))
    if mode == "blend_subject_global":
        return float(np.clip(0.5 * subject_rate + 0.5 * global_rate, EPS, 1.0 - EPS))
    if mode == "global_rate":
        return float(np.clip(global_rate, EPS, 1.0 - EPS))
    raise ValueError(f"Unknown calibration mode: {mode}")


def calibrate_eval_block(
    eval_frame: pd.DataFrame,
    pred: np.ndarray,
    observed_train: pd.DataFrame,
    targets: list[str],
    spec: CalSpec,
) -> np.ndarray:
    out = pred.copy()
    eval_reset = eval_frame.reset_index(drop=True)
    for target in targets:
        target_i = TARGET_COLUMNS.index(target)
        raw = safe_logit(pred[:, target_i])
        for subject, group in eval_reset.reset_index().groupby("subject_id", sort=False):
            idx = group["index"].to_numpy(dtype=int)
            scores = raw[idx]
            std = float(np.nanstd(scores))
            if np.isfinite(std) and std > 1e-8:
                scores = (scores - float(np.nanmean(scores))) / std
            else:
                scores = scores - float(np.nanmean(scores))
            scores = spec.beta * scores
            base_mean = float(pred[idx, target_i].mean())
            rate = target_rate(observed_train, str(subject), target, len(idx), spec.mode)
            target_mean = (1.0 - spec.strength) * base_mean + spec.strength * rate
            out[idx, target_i] = sigmoid(scores + solve_intercept(scores, target_mean))
    return np.clip(out, EPS, 1.0 - EPS)


def calibrate_oof(
    train: pd.DataFrame,
    base_oof: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
    targets: list[str],
    spec: CalSpec,
) -> np.ndarray:
    out = base_oof.copy()
    for train_idx, val_idx in folds:
        out[val_idx] = calibrate_eval_block(train.iloc[val_idx], base_oof[val_idx], train.iloc[train_idx], targets, spec)
    return out


def calibrate_submission(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_submission: np.ndarray,
    targets: list[str],
    spec: CalSpec,
) -> np.ndarray:
    return calibrate_eval_block(sample, base_submission, train, targets, spec)


def target_loss(y: pd.DataFrame, pred: np.ndarray, target_i: int, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y), dtype=int)
    target = TARGET_COLUMNS[target_i]
    return float(log_loss(y.iloc[indices][target].to_numpy(), np.clip(pred[indices, target_i], EPS, 1.0 - EPS), labels=[0, 1]))


def average_loss(y: pd.DataFrame, pred: np.ndarray) -> tuple[float, dict[str, float]]:
    per_target = {target: target_loss(y, pred, target_i) for target_i, target in enumerate(TARGET_COLUMNS)}
    return float(np.mean(list(per_target.values()))), per_target


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
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

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof_df = normalize_keys(pd.read_csv(args.base_oof))
    base_sub_df = normalize_keys(pd.read_csv(args.base_submission))
    if not base_oof_df[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys")
    if not base_sub_df[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys")

    targets = parse_str_list(args.targets)
    unknown_targets = sorted(set(targets) - set(TARGET_COLUMNS))
    if unknown_targets:
        raise ValueError(f"Unknown targets: {unknown_targets}")

    folds = make_subject_time_folds(train, args.folds)
    y = train[TARGET_COLUMNS]
    base_oof = prediction_matrix(base_oof_df)
    base_sub = submission_matrix(base_sub_df)
    base_avg, base_targets = average_loss(y, base_oof)
    base_fold_target = {
        target: [target_loss(y, base_oof, target_i, val_idx) for _, val_idx in folds]
        for target_i, target in enumerate(TARGET_COLUMNS)
    }

    specs = [
        CalSpec(mode, strength, beta)
        for mode in parse_str_list(args.modes)
        for strength in parse_float_list(args.strengths)
        for beta in parse_float_list(args.betas)
    ]
    blend_weights = parse_float_list(args.blend_weights)
    rows = []
    cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    for spec_i, spec in enumerate(specs, start=1):
        print(f"[{spec_i}/{len(specs)}] {spec.name}")
        cal_oof = calibrate_oof(train, base_oof, folds, targets, spec)
        cal_sub = calibrate_submission(train, sample, base_sub, targets, spec)
        for blend_weight in blend_weights:
            name = f"{spec.name}_w{blend_weight:g}"
            pred = base_oof.copy()
            sub = base_sub.copy()
            for target in targets:
                target_i = TARGET_COLUMNS.index(target)
                pred[:, target_i] = np.clip((1.0 - blend_weight) * base_oof[:, target_i] + blend_weight * cal_oof[:, target_i], EPS, 1.0 - EPS)
                sub[:, target_i] = np.clip((1.0 - blend_weight) * base_sub[:, target_i] + blend_weight * cal_sub[:, target_i], EPS, 1.0 - EPS)
            cache[name] = (pred, sub)
            avg, per_target = average_loss(y, pred)
            rows.append(
                {
                    "name": name,
                    "mode": spec.mode,
                    "strength": spec.strength,
                    "beta": spec.beta,
                    "blend_weight": blend_weight,
                    "avg_log_loss": avg,
                    "delta_vs_base": base_avg - avg,
                    **per_target,
                }
            )

    scores = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    best_by_target: dict[str, dict] = {}
    for row in scores.to_dict(orient="records"):
        pred, _ = cache[str(row["name"])]
        for target in targets:
            target_i = TARGET_COLUMNS.index(target)
            value = target_loss(y, pred, target_i)
            current = best_by_target.get(target)
            if current is not None and value >= current["log_loss"]:
                continue
            fold_scores = [target_loss(y, pred, target_i, val_idx) for _, val_idx in folds]
            fold_deltas = [base_fold - cand_fold for base_fold, cand_fold in zip(base_fold_target[target], fold_scores)]
            best_by_target[target] = {
                "target": target,
                "log_loss": value,
                "base_log_loss": base_targets[target],
                "delta_vs_base": base_targets[target] - value,
                "candidate": row["name"],
                "mode": row["mode"],
                "strength": row["strength"],
                "beta": row["beta"],
                "blend_weight": row["blend_weight"],
                "folds_improved": int(sum(delta > 0 for delta in fold_deltas)),
                "worst_fold_delta": float(min(fold_deltas)),
            }

    final_oof = base_oof.copy()
    final_sub = base_sub.copy()
    selection_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        selected = best_by_target.get(target)
        used = False
        if selected is not None:
            pred, sub = cache[str(selected["candidate"])]
            used = (
                selected["delta_vs_base"] >= args.min_delta
                and selected["folds_improved"] >= args.min_target_folds_improved
                and selected["worst_fold_delta"] >= -args.max_worst_fold_regression
            )
            if used:
                final_oof[:, target_i] = pred[:, target_i]
                final_sub[:, target_i] = sub[:, target_i]
            selection_rows.append({**selected, "used": bool(used)})
        else:
            selection_rows.append(
                {
                    "target": target,
                    "log_loss": base_targets[target],
                    "base_log_loss": base_targets[target],
                    "delta_vs_base": 0.0,
                    "candidate": "base",
                    "mode": "base",
                    "strength": np.nan,
                    "beta": np.nan,
                    "blend_weight": 0.0,
                    "folds_improved": 0,
                    "worst_fold_delta": 0.0,
                    "used": False,
                }
            )

    final_avg, final_targets = average_loss(y, final_oof)
    scores.to_csv(output_dir / "candidate_scores.csv", index=False)
    selection = pd.DataFrame(selection_rows)
    selection.to_csv(output_dir / "targetwise_selection.csv", index=False)

    oof_df = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_df[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_subject_rate_calibration.csv"
    oof_df.to_csv(oof_path, index=False)

    submission = sample.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_sub[:, target_i]
    submission_path = output_dir / "submission_subject_rate_calibration.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_avg,
        "base_targets": base_targets,
        "final_avg_log_loss": final_avg,
        "final_targets": final_targets,
        "selection": selection_rows,
        "top_candidates": scores.head(30).to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "subject_rate_calibration_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Subject Rate Calibration",
        "",
        f"- Base CV: `{base_avg:.6f}`",
        f"- Final CV: `{final_avg:.6f}`",
        f"- Selected targets: `{','.join(selection.loc[selection['used'], 'target'].tolist())}`",
        "",
        "## Target-wise selection",
        "",
        dataframe_to_markdown(selection),
        "",
        "## Top candidates",
        "",
        dataframe_to_markdown(scores.head(20)[["name", "avg_log_loss", "delta_vs_base", *TARGET_COLUMNS]]),
        "",
    ]
    (output_dir / "subject_rate_calibration_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"base={base_avg:.6f} final={final_avg:.6f}")
    print(selection.to_string(index=False))
    print(f"saved report: {output_dir / 'subject_rate_calibration_report.md'}")
    print(f"saved submission: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fold-safe subject/global rate calibration for target probabilities.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/multi_signal_qcount_blend_w015_020_015_015/oof_multi_signal_qcount_blend.csv")
    parser.add_argument("--base-submission", default="outputs/multi_signal_qcount_blend_w015_020_015_015/submission_multi_signal_qcount_blend.csv")
    parser.add_argument("--output-dir", default="outputs/subject_rate_calibration_on_multi_signal")
    parser.add_argument("--targets", default="S1,S2,S4")
    parser.add_argument("--modes", default="global_count,subject_rate,blend_subject_global,global_rate")
    parser.add_argument("--strengths", default="0.02,0.05,0.1,0.2,0.35,0.5,0.75,1.0")
    parser.add_argument("--betas", default="0.25,0.5,0.75,1.0,1.5,2.0")
    parser.add_argument("--blend-weights", default="0.02,0.05,0.1,0.15,0.2,0.35,0.5,0.75,1.0")
    parser.add_argument("--min-target-folds-improved", type=int, default=3)
    parser.add_argument("--min-delta", type=float, default=0.0)
    parser.add_argument("--max-worst-fold-regression", type=float, default=0.005)
    parser.add_argument("--folds", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    main()
