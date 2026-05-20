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
class CandidateSpec:
    name: str
    oof_path: Path
    submission_path: Path


@dataclass(frozen=True)
class TargetOption:
    target: str
    source: str
    weight: float
    mode: str
    pred: np.ndarray
    submission: np.ndarray
    row_delta: np.ndarray
    uniform_delta: float
    weighted_delta: float
    weighted_p025: float
    weighted_p500: float
    weighted_p975: float
    folds_improved: int
    mid_delta: float
    late_mid_delta: float
    tail20_delta: float
    worst_subject_delta: float
    score: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_candidate(value: str) -> CandidateSpec:
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError("--candidate entries must be name:oof_path:submission_path")
    return CandidateSpec(name=parts[0], oof_path=Path(parts[1]), submission_path=Path(parts[2]))


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    missing = sorted(set(TARGET_COLUMNS) - set(submission.columns))
    if missing:
        raise ValueError(f"Submission file missing target columns: {missing}")
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def target_row_loss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y * np.log(pred) + (1.0 - y) * np.log1p(-pred))


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def blend_column(base: np.ndarray, candidate: np.ndarray, weight: float, mode: str) -> np.ndarray:
    if mode == "prob":
        out = base + weight * (candidate - base)
    elif mode == "logit":
        out = sigmoid(safe_logit(base) + weight * (safe_logit(candidate) - safe_logit(base)))
    else:
        raise ValueError(f"Unknown blend mode: {mode}")
    return np.clip(out, EPS, 1.0 - EPS)


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    train_pos = all_rows[all_rows["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    sample_pos = all_rows[all_rows["_split"].eq("sample")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    sample_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    sample_out[["panel_index", "panel_position"]] = sample_pos
    return train_out, sample_out


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame, bins: np.ndarray) -> tuple[np.ndarray, pd.DataFrame]:
    train_bin = np.digitize(train["panel_position"].to_numpy(dtype=float), bins) - 1
    sample_bin = np.digitize(sample["panel_position"].to_numpy(dtype=float), bins) - 1
    n_bins = len(bins) - 1
    train_frac = np.bincount(train_bin, minlength=n_bins).astype(float) / max(len(train_bin), 1)
    sample_frac = np.bincount(sample_bin, minlength=n_bins).astype(float) / max(len(sample_bin), 1)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros(n_bins, dtype=float), where=train_frac > 0)
    weights = ratio[train_bin]
    if weights.mean() > 0:
        weights = weights / weights.mean()
    bin_table = pd.DataFrame(
        {
            "bin": [f"[{bins[i]:.3f},{bins[i + 1]:.3f})" for i in range(n_bins)],
            "train_frac": train_frac,
            "sample_frac": sample_frac,
            "weight_ratio": ratio,
        }
    )
    return weights.astype(float), bin_table


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    buckets: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        for fold, chunk in enumerate(np.array_split(group["_idx"].to_numpy(), n_folds)):
            buckets[fold].extend(chunk.tolist())
    return [np.array(sorted(bucket), dtype=int) for bucket in buckets]


def make_blocks(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "mid": frame.index[(frame["panel_position"] >= 1 / 3) & (frame["panel_position"] < 2 / 3)].to_numpy(dtype=int),
        "late_mid": frame.index[(frame["panel_position"] >= 2 / 3) & (frame["panel_position"] < 0.8)].to_numpy(dtype=int),
        "tail20": frame.index[frame["panel_position"] >= 0.8].to_numpy(dtype=int),
    }


def weighted_bootstrap(
    delta: np.ndarray,
    weights: np.ndarray,
    rng: np.random.Generator,
    n_bootstrap: int,
) -> dict[str, float]:
    weights = np.clip(np.asarray(weights, dtype=float), 0.0, None)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    prob = weights / weights.sum()
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.choice(len(delta), size=len(delta), replace=True, p=prob)
        values[i] = float(delta[idx].mean())
    return {
        "p025": float(np.quantile(values, 0.025)),
        "p500": float(np.quantile(values, 0.500)),
        "p975": float(np.quantile(values, 0.975)),
    }


def uniform_bootstrap(delta: np.ndarray, rng: np.random.Generator, n_bootstrap: int) -> dict[str, float]:
    values = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(delta), size=len(delta))
        values[i] = float(delta[idx].mean())
    return {
        "p025": float(np.quantile(values, 0.025)),
        "p500": float(np.quantile(values, 0.500)),
        "p975": float(np.quantile(values, 0.975)),
    }


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


def load_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, np.ndarray]]:
    loaded: dict[str, dict[str, np.ndarray]] = {}
    for spec in [parse_candidate(item) for item in args.candidate]:
        oof = normalize_keys(pd.read_csv(spec.oof_path))
        submission = normalize_keys(pd.read_csv(spec.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{spec.name} OOF keys do not match train keys")
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"{spec.name} submission keys do not match sample keys")
        loaded[spec.name] = {"oof": prediction_matrix(oof), "submission": submission_matrix(submission)}
    if args.baseline not in loaded:
        raise ValueError(f"Baseline is not in candidate list: {args.baseline}")
    return loaded


def build_options(
    args: argparse.Namespace,
    train: pd.DataFrame,
    y_arr: np.ndarray,
    loaded: dict[str, dict[str, np.ndarray]],
    weights: np.ndarray,
    folds: list[np.ndarray],
    blocks: dict[str, np.ndarray],
    subject_groups: dict[str, np.ndarray],
) -> dict[str, list[TargetOption]]:
    base_pred = loaded[args.baseline]["oof"]
    base_submission = loaded[args.baseline]["submission"]
    blend_weights = parse_float_list(args.weights)
    modes = parse_str_list(args.modes)
    target_options: dict[str, list[TargetOption]] = {}
    rng = np.random.default_rng(args.seed)
    for target_i, target in enumerate(TARGET_COLUMNS):
        base_col = base_pred[:, target_i]
        base_sub_col = base_submission[:, target_i]
        base_loss = target_row_loss(y_arr[:, target_i], base_col)
        base_option = TargetOption(
            target=target,
            source=args.baseline,
            weight=0.0,
            mode="base",
            pred=base_col,
            submission=base_sub_col,
            row_delta=np.zeros(len(train), dtype=float),
            uniform_delta=0.0,
            weighted_delta=0.0,
            weighted_p025=0.0,
            weighted_p500=0.0,
            weighted_p975=0.0,
            folds_improved=0,
            mid_delta=0.0,
            late_mid_delta=0.0,
            tail20_delta=0.0,
            worst_subject_delta=0.0,
            score=0.0,
        )
        options = [base_option]
        for source, arrays in loaded.items():
            if source == args.baseline:
                continue
            cand_col = arrays["oof"][:, target_i]
            cand_sub_col = arrays["submission"][:, target_i]
            for blend_weight in blend_weights:
                if blend_weight <= 0:
                    continue
                for mode in modes:
                    pred = blend_column(base_col, cand_col, blend_weight, mode)
                    submission = blend_column(base_sub_col, cand_sub_col, blend_weight, mode)
                    row_delta = base_loss - target_row_loss(y_arr[:, target_i], pred)
                    uniform_delta = float(row_delta.mean())
                    weighted_delta = float(np.average(row_delta, weights=weights))
                    boot = weighted_bootstrap(row_delta, weights, rng, args.option_bootstrap)
                    fold_deltas = [float(row_delta[idx].mean()) for idx in folds]
                    subject_deltas = [float(row_delta[idx].mean()) for idx in subject_groups.values()]
                    mid_delta = float(row_delta[blocks["mid"]].mean()) if len(blocks["mid"]) else 0.0
                    late_mid_delta = float(row_delta[blocks["late_mid"]].mean()) if len(blocks["late_mid"]) else 0.0
                    tail20_delta = float(row_delta[blocks["tail20"]].mean()) if len(blocks["tail20"]) else 0.0
                    worst_subject_delta = float(min(subject_deltas)) if subject_deltas else 0.0
                    folds_improved = int(sum(delta > 0 for delta in fold_deltas))
                    if weighted_delta < args.min_weighted_option_delta:
                        continue
                    if boot["p025"] < args.min_option_weighted_p025:
                        continue
                    if uniform_delta < -args.max_uniform_option_regression:
                        continue
                    if mid_delta < -args.max_mid_option_regression:
                        continue
                    if tail20_delta < -args.max_tail_option_regression:
                        continue
                    if worst_subject_delta < -args.max_subject_option_regression:
                        continue
                    if folds_improved < args.min_option_folds:
                        continue
                    stress_penalty = (
                        max(0.0, -uniform_delta) * args.uniform_penalty
                        + max(0.0, -mid_delta) * args.block_penalty
                        + max(0.0, -late_mid_delta - args.max_late_mid_option_regression) * args.block_penalty
                        + max(0.0, -tail20_delta) * args.block_penalty
                        + max(0.0, -worst_subject_delta) * args.subject_penalty
                    )
                    score = weighted_delta + args.p025_bonus_weight * boot["p025"] - stress_penalty
                    options.append(
                        TargetOption(
                            target=target,
                            source=source,
                            weight=float(blend_weight),
                            mode=mode,
                            pred=pred,
                            submission=submission,
                            row_delta=row_delta,
                            uniform_delta=uniform_delta,
                            weighted_delta=weighted_delta,
                            weighted_p025=boot["p025"],
                            weighted_p500=boot["p500"],
                            weighted_p975=boot["p975"],
                            folds_improved=folds_improved,
                            mid_delta=mid_delta,
                            late_mid_delta=late_mid_delta,
                            tail20_delta=tail20_delta,
                            worst_subject_delta=worst_subject_delta,
                            score=float(score),
                        )
                    )
        kept = sorted(options[1:], key=lambda item: (item.score, item.weighted_delta), reverse=True)
        target_options[target] = [base_option, *kept[: args.max_options_per_target]]
    return target_options


def per_target_log_loss(y_arr: np.ndarray, pred: np.ndarray, weights: np.ndarray | None = None) -> dict[str, float]:
    scores = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        scores[target] = float(log_loss(y_arr[:, target_i], pred[:, target_i], labels=[0, 1], sample_weight=weights))
    scores["avg"] = float(np.mean([scores[target] for target in TARGET_COLUMNS]))
    return scores


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_raw = normalize_keys(pd.read_csv(args.train_path))
    sample_raw = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train_raw, sample_raw)
    bins = np.asarray([float(value) for value in args.position_bins.split(",")], dtype=float)
    bins[-1] = bins[-1] + 1e-6
    row_weights, bin_table = sample_position_weights(train, sample, bins)
    loaded = load_predictions(args, train, sample)
    y_arr = train[TARGET_COLUMNS].to_numpy(dtype=float)
    folds = make_subject_time_folds(train, args.folds)
    blocks = make_blocks(train)
    subject_groups = {str(subject): group.index.to_numpy(dtype=int) for subject, group in train.groupby("subject_id", sort=True)}
    options = build_options(args, train, y_arr, loaded, row_weights, folds, blocks, subject_groups)

    option_rows = []
    selected: dict[str, TargetOption] = {}
    for target in TARGET_COLUMNS:
        non_base = [option for option in options[target] if option.weight > 0]
        best = non_base[0] if non_base else options[target][0]
        selected[target] = best
        for option in options[target]:
            option_rows.append(
                {
                    "target": target,
                    "source": option.source,
                    "weight": option.weight,
                    "mode": option.mode,
                    "uniform_delta": option.uniform_delta,
                    "weighted_delta": option.weighted_delta,
                    "weighted_p025": option.weighted_p025,
                    "weighted_p500": option.weighted_p500,
                    "weighted_p975": option.weighted_p975,
                    "folds_improved": option.folds_improved,
                    "mid_delta": option.mid_delta,
                    "late_mid_delta": option.late_mid_delta,
                    "tail20_delta": option.tail20_delta,
                    "worst_subject_delta": option.worst_subject_delta,
                    "score": option.score,
                    "selected": option == best,
                }
            )
    option_df = pd.DataFrame(option_rows)
    option_df.to_csv(output_dir / "sample_weighted_target_options.csv", index=False)

    base_pred = loaded[args.baseline]["oof"]
    base_submission = loaded[args.baseline]["submission"]
    final_pred = base_pred.copy()
    final_submission = base_submission.copy()
    combined_delta = np.zeros(len(train), dtype=float)
    for target_i, target in enumerate(TARGET_COLUMNS):
        option = selected[target]
        final_pred[:, target_i] = option.pred
        final_submission[:, target_i] = option.submission
        combined_delta += option.row_delta / len(TARGET_COLUMNS)

    base_uniform = per_target_log_loss(y_arr, base_pred)
    final_uniform = per_target_log_loss(y_arr, final_pred)
    base_weighted = per_target_log_loss(y_arr, base_pred, row_weights)
    final_weighted = per_target_log_loss(y_arr, final_pred, row_weights)
    rng = np.random.default_rng(args.seed + 1009)
    weighted_boot = weighted_bootstrap(combined_delta, row_weights, rng, args.bootstrap)
    uniform_boot = uniform_bootstrap(combined_delta, rng, args.bootstrap)
    block_rows = []
    for block_name, idx in blocks.items():
        if len(idx) == 0:
            continue
        block_rows.append({"block": block_name, "rows": int(len(idx)), "delta": float(combined_delta[idx].mean())})
    block_df = pd.DataFrame(block_rows)
    block_df.to_csv(output_dir / "sample_weighted_targetwise_blocks.csv", index=False)

    oof = train_raw[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = final_pred[:, target_i]
    oof_path = output_dir / "oof_sample_weighted_targetwise_blend.csv"
    oof.to_csv(oof_path, index=False)

    submission = sample_raw.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_sample_weighted_targetwise_blend.csv"
    submission.to_csv(submission_path, index=False)

    summary = {
        "baseline": args.baseline,
        "uniform_base_avg": base_uniform["avg"],
        "uniform_final_avg": final_uniform["avg"],
        "weighted_base_avg": base_weighted["avg"],
        "weighted_final_avg": final_weighted["avg"],
        "uniform_improvement": base_uniform["avg"] - final_uniform["avg"],
        "weighted_improvement": base_weighted["avg"] - final_weighted["avg"],
        "uniform_p025": uniform_boot["p025"],
        "uniform_p500": uniform_boot["p500"],
        "uniform_p975": uniform_boot["p975"],
        "weighted_p025": weighted_boot["p025"],
        "weighted_p500": weighted_boot["p500"],
        "weighted_p975": weighted_boot["p975"],
        "promote_weighted": weighted_boot["p025"] > args.min_combined_weighted_p025
        and base_weighted["avg"] > final_weighted["avg"],
        "promote_uniform": uniform_boot["p025"] > args.min_combined_uniform_p025
        and base_uniform["avg"] > final_uniform["avg"],
    }
    selected_rows = pd.DataFrame(
        [
            {
                "target": target,
                "source": selected[target].source,
                "weight": selected[target].weight,
                "mode": selected[target].mode,
                "uniform_delta": selected[target].uniform_delta,
                "weighted_delta": selected[target].weighted_delta,
                "weighted_p025": selected[target].weighted_p025,
                "mid_delta": selected[target].mid_delta,
                "late_mid_delta": selected[target].late_mid_delta,
                "tail20_delta": selected[target].tail20_delta,
                "worst_subject_delta": selected[target].worst_subject_delta,
            }
            for target in TARGET_COLUMNS
        ]
    )
    selected_rows.to_csv(output_dir / "sample_weighted_targetwise_selection.csv", index=False)
    bin_table.to_csv(output_dir / "sample_position_weight_bins.csv", index=False)

    report = {
        "summary": summary,
        "selected_options": selected_rows.to_dict(orient="records"),
        "position_bins": bin_table.to_dict(orient="records"),
        "args": vars(args),
    }
    (output_dir / "sample_weighted_targetwise_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    summary_df = pd.DataFrame([summary])
    md = [
        "# Sample-weighted Targetwise Blend Search",
        "",
        "This selector optimizes target adoption under the submission sample panel-position distribution.",
        "",
        "## Summary",
        "",
        dataframe_to_markdown(summary_df),
        "",
        "## Position bins",
        "",
        dataframe_to_markdown(bin_table),
        "",
        "## Selected options",
        "",
        dataframe_to_markdown(selected_rows),
        "",
        "## Block deltas",
        "",
        dataframe_to_markdown(block_df),
        "",
        "## Top target options",
        "",
        dataframe_to_markdown(option_df.sort_values(["selected", "target", "score"], ascending=[False, True, False]).head(40)),
        "",
    ]
    (output_dir / "sample_weighted_targetwise_report.md").write_text("\n".join(md), encoding="utf-8")
    print(
        "selected "
        f"uniform={summary['uniform_final_avg']:.6f} "
        f"weighted={summary['weighted_final_avg']:.6f} "
        f"weighted_p025={summary['weighted_p025']:.6f} "
        f"promote_weighted={summary['promote_weighted']}"
    )
    print(selected_rows.to_string(index=False))
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build targetwise blends using submission-position weighted OOF diagnostics.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--weights", default="0.05,0.08,0.1,0.15,0.2,0.3,0.4,0.5,0.65,0.8,1.0")
    parser.add_argument("--modes", default="prob,logit")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--position-bins", default="0,0.3333333333,0.6666666667,0.8,1.0")
    parser.add_argument("--max-options-per-target", type=int, default=12)
    parser.add_argument("--option-bootstrap", type=int, default=2500)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--min-weighted-option-delta", type=float, default=0.00005)
    parser.add_argument("--min-option-weighted-p025", type=float, default=0.0)
    parser.add_argument("--min-option-folds", type=int, default=2)
    parser.add_argument("--max-uniform-option-regression", type=float, default=0.0012)
    parser.add_argument("--max-mid-option-regression", type=float, default=0.0010)
    parser.add_argument("--max-late-mid-option-regression", type=float, default=0.0040)
    parser.add_argument("--max-tail-option-regression", type=float, default=0.0015)
    parser.add_argument("--max-subject-option-regression", type=float, default=0.015)
    parser.add_argument("--p025-bonus-weight", type=float, default=0.25)
    parser.add_argument("--uniform-penalty", type=float, default=0.30)
    parser.add_argument("--block-penalty", type=float, default=0.50)
    parser.add_argument("--subject-penalty", type=float, default=0.04)
    parser.add_argument("--min-combined-weighted-p025", type=float, default=0.00005)
    parser.add_argument("--min-combined-uniform-p025", type=float, default=0.00002)
    return parser.parse_args()


if __name__ == "__main__":
    main()
