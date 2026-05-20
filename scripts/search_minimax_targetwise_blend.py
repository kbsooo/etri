from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    oof_path: Path
    submission_path: Path


@dataclass
class TargetOption:
    target: str
    source: str
    weight: float
    mode: str
    pred: np.ndarray
    submission: np.ndarray
    row_delta: np.ndarray
    target_delta: float
    fold_deltas: list[float]
    late_delta: float
    tail20_delta: float
    worst_subject_delta: float
    option_score: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_str_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_candidate(value: str) -> CandidateSpec:
    parts = value.split(":")
    if len(parts) != 3:
        raise ValueError("--candidate entries must be name:oof_path:submission_path")
    return CandidateSpec(parts[0], Path(parts[1]), Path(parts[2]))


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file missing columns: {missing}")
    return np.clip(oof[cols].to_numpy(dtype=float), EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


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


def add_panel_columns(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["subject_day_index"] = ordered.groupby("subject_id").cumcount()
    subject_max = ordered.groupby("subject_id")["subject_day_index"].transform("max").replace(0, 1)
    ordered["subject_position"] = ordered["subject_day_index"] / subject_max
    ordered["subject_count"] = ordered.groupby("subject_id")["subject_day_index"].transform("max") + 1
    return ordered.sort_values("_idx").drop(columns="_idx").reset_index(drop=True)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    buckets: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        for fold, chunk in enumerate(np.array_split(group["_idx"].to_numpy(), n_folds)):
            buckets[fold].extend(chunk.tolist())
    return [np.array(sorted(bucket), dtype=int) for bucket in buckets]


def make_blocks(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "all": np.arange(len(frame), dtype=int),
        "early_third": frame.index[frame["subject_position"] < 1 / 3].to_numpy(dtype=int),
        "mid_third": frame.index[(frame["subject_position"] >= 1 / 3) & (frame["subject_position"] < 2 / 3)].to_numpy(dtype=int),
        "late_third": frame.index[frame["subject_position"] >= 2 / 3].to_numpy(dtype=int),
        "tail_20pct": frame.index[frame["subject_position"] >= 0.8].to_numpy(dtype=int),
    }


def target_row_loss(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y * np.log(pred) + (1.0 - y) * np.log1p(-pred))


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


def load_predictions(args: argparse.Namespace, train: pd.DataFrame, sample: pd.DataFrame) -> dict[str, dict[str, np.ndarray]]:
    specs = [parse_candidate(item) for item in args.candidate]
    loaded: dict[str, dict[str, np.ndarray]] = {}
    for spec in specs:
        oof = normalize_keys(pd.read_csv(spec.oof_path))
        submission = normalize_keys(pd.read_csv(spec.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{spec.name} OOF keys do not match train keys")
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            raise ValueError(f"{spec.name} submission keys do not match sample keys")
        loaded[spec.name] = {
            "oof": prediction_matrix(oof),
            "submission": submission_matrix(submission),
        }
    if args.baseline not in loaded:
        raise ValueError(f"Baseline is not in candidate list: {args.baseline}")
    return loaded


def build_target_options(
    args: argparse.Namespace,
    train: pd.DataFrame,
    y_arr: np.ndarray,
    loaded: dict[str, dict[str, np.ndarray]],
    folds: list[np.ndarray],
    blocks: dict[str, np.ndarray],
    subject_groups: dict[str, np.ndarray],
) -> dict[str, list[TargetOption]]:
    base_pred = loaded[args.baseline]["oof"]
    base_submission = loaded[args.baseline]["submission"]
    weights = parse_float_list(args.weights)
    modes = parse_str_list(args.modes)
    options: dict[str, list[TargetOption]] = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        base_col = base_pred[:, target_i]
        base_sub_col = base_submission[:, target_i]
        base_loss = target_row_loss(y_arr[:, target_i], base_col)
        target_options = [
            TargetOption(
                target=target,
                source=args.baseline,
                weight=0.0,
                mode="base",
                pred=base_col,
                submission=base_sub_col,
                row_delta=np.zeros(len(train), dtype=float),
                target_delta=0.0,
                fold_deltas=[0.0 for _ in folds],
                late_delta=0.0,
                tail20_delta=0.0,
                worst_subject_delta=0.0,
                option_score=0.0,
            )
        ]
        for source, arrays in loaded.items():
            if source == args.baseline:
                continue
            cand_col = arrays["oof"][:, target_i]
            cand_sub_col = arrays["submission"][:, target_i]
            for weight in weights:
                if weight <= 0:
                    continue
                for mode in modes:
                    pred = blend_column(base_col, cand_col, weight, mode)
                    sub = blend_column(base_sub_col, cand_sub_col, weight, mode)
                    row_delta = base_loss - target_row_loss(y_arr[:, target_i], pred)
                    fold_deltas = [float(row_delta[idx].mean()) for idx in folds]
                    subject_deltas = [float(row_delta[idx].mean()) for idx in subject_groups.values()]
                    late_delta = float(row_delta[blocks["late_third"]].mean())
                    tail20_delta = float(row_delta[blocks["tail_20pct"]].mean())
                    stress_floor = min(min(fold_deltas), late_delta, tail20_delta, min(subject_deltas))
                    target_delta = float(row_delta.mean())
                    if target_delta < args.min_option_delta:
                        continue
                    if sum(delta > 0 for delta in fold_deltas) < args.min_option_folds:
                        continue
                    option_score = target_delta + args.option_stress_weight * min(0.0, stress_floor)
                    target_options.append(
                        TargetOption(
                            target=target,
                            source=source,
                            weight=float(weight),
                            mode=mode,
                            pred=pred,
                            submission=sub,
                            row_delta=row_delta,
                            target_delta=target_delta,
                            fold_deltas=fold_deltas,
                            late_delta=late_delta,
                            tail20_delta=tail20_delta,
                            worst_subject_delta=float(min(subject_deltas)),
                            option_score=float(option_score),
                        )
                    )
        kept = sorted(target_options[1:], key=lambda option: (option.option_score, option.target_delta), reverse=True)
        options[target] = [target_options[0], *kept[: args.max_options_per_target]]
    return options


def summarize_selection(
    selection: dict[str, TargetOption],
    base_avg: float,
    folds: list[np.ndarray],
    blocks: dict[str, np.ndarray],
    subject_groups: dict[str, np.ndarray],
) -> dict[str, object]:
    total_delta = sum((selection[target].row_delta for target in TARGET_COLUMNS), np.zeros(len(next(iter(selection.values())).row_delta))) / len(TARGET_COLUMNS)
    fold_deltas = [float(total_delta[idx].mean()) for idx in folds]
    block_deltas = {name: float(total_delta[idx].mean()) for name, idx in blocks.items()}
    subject_deltas = [float(total_delta[idx].mean()) for idx in subject_groups.values()]
    target_deltas = {target: float(selection[target].target_delta) for target in TARGET_COLUMNS}
    late_idx = blocks["late_third"]
    late_target_deltas = {target: float(selection[target].row_delta[late_idx].mean()) for target in TARGET_COLUMNS}
    improvement = float(total_delta.mean())
    improved_folds = int(sum(delta > 0 for delta in fold_deltas))
    return {
        "avg_log_loss": float(base_avg - improvement),
        "improvement": improvement,
        "improved_folds": improved_folds,
        "worst_target_delta": float(min(target_deltas.values())),
        "early_delta": block_deltas["early_third"],
        "mid_delta": block_deltas["mid_third"],
        "late_delta": block_deltas["late_third"],
        "tail20_delta": block_deltas["tail_20pct"],
        "worst_subject_delta": float(min(subject_deltas)),
        "worst_late_target_delta": float(min(late_target_deltas.values())),
        "fold_deltas": fold_deltas,
        "target_deltas": target_deltas,
        "late_target_deltas": late_target_deltas,
        "row_delta": total_delta,
    }


def deterministic_penalty(row: dict[str, object], args: argparse.Namespace) -> float:
    penalty = 0.0
    penalty += max(0, args.min_folds_improved - int(row["improved_folds"])) * args.fold_penalty
    penalty += max(0.0, -float(row["worst_target_delta"]) - args.max_target_regression) * args.constraint_penalty
    penalty += max(0.0, -float(row["late_delta"]) - args.max_block_regression) * args.constraint_penalty
    penalty += max(0.0, -float(row["tail20_delta"]) - args.max_tail_regression) * args.constraint_penalty
    penalty += max(0.0, -float(row["worst_subject_delta"]) - args.max_subject_regression) * args.constraint_penalty
    penalty += max(0.0, -float(row["worst_late_target_delta"]) - args.max_late_target_regression) * args.constraint_penalty
    return float(penalty)


def selection_name(selection: dict[str, TargetOption]) -> str:
    parts = []
    for target in TARGET_COLUMNS:
        option = selection[target]
        if option.weight > 0:
            parts.append(f"{target}={option.source}:{option.mode}:{option.weight:g}")
    return "base" if not parts else "|".join(parts)


def bootstrap_p025(row_delta: np.ndarray, boot_indices: np.ndarray) -> dict[str, float]:
    values = row_delta[boot_indices].mean(axis=1)
    return {
        "improvement_p025": float(np.quantile(values, 0.025)),
        "improvement_p500": float(np.quantile(values, 0.500)),
        "improvement_p975": float(np.quantile(values, 0.975)),
    }


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = add_panel_columns(normalize_keys(pd.read_csv(args.train_path)))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    loaded = load_predictions(args, train, sample)
    y_arr = train[TARGET_COLUMNS].to_numpy(dtype=float)
    base_pred = loaded[args.baseline]["oof"]
    base_submission = loaded[args.baseline]["submission"]
    base_loss = np.mean(
        np.column_stack([target_row_loss(y_arr[:, i], base_pred[:, i]) for i in range(len(TARGET_COLUMNS))]),
        axis=1,
    )
    base_avg = float(base_loss.mean())
    folds = make_subject_time_folds(train, args.folds)
    blocks = make_blocks(train)
    subject_groups = {
        str(subject): group.index.to_numpy(dtype=int)
        for subject, group in train.groupby("subject_id", sort=True)
    }

    options = build_target_options(args, train, y_arr, loaded, folds, blocks, subject_groups)
    option_rows = []
    for target, target_options in options.items():
        for option in target_options:
            option_rows.append(
                {
                    "target": target,
                    "source": option.source,
                    "weight": option.weight,
                    "mode": option.mode,
                    "target_delta": option.target_delta,
                    "folds_improved": int(sum(delta > 0 for delta in option.fold_deltas)),
                    "late_delta": option.late_delta,
                    "tail20_delta": option.tail20_delta,
                    "worst_subject_delta": option.worst_subject_delta,
                    "option_score": option.option_score,
                }
            )
    option_df = pd.DataFrame(option_rows)
    option_df.to_csv(output_dir / "target_options.csv", index=False)

    beam: list[dict[str, TargetOption]] = [{target: options[target][0] for target in TARGET_COLUMNS}]
    for target in TARGET_COLUMNS:
        expanded: list[tuple[float, dict[str, TargetOption], dict[str, object]]] = []
        for selection in beam:
            for option in options[target]:
                candidate_selection = dict(selection)
                candidate_selection[target] = option
                summary = summarize_selection(candidate_selection, base_avg, folds, blocks, subject_groups)
                score = float(summary["avg_log_loss"]) + deterministic_penalty(summary, args)
                expanded.append((score, candidate_selection, summary))
        expanded.sort(key=lambda item: (item[0], float(item[2]["avg_log_loss"])))
        beam = [item[1] for item in expanded[: args.beam_size]]

    rows = []
    cache: dict[str, dict[str, TargetOption]] = {}
    for selection in beam:
        name = selection_name(selection)
        summary = summarize_selection(selection, base_avg, folds, blocks, subject_groups)
        penalty = deterministic_penalty(summary, args)
        row = {
            "name": name,
            "avg_log_loss": summary["avg_log_loss"],
            "improvement": summary["improvement"],
            "improved_folds": summary["improved_folds"],
            "worst_target_delta": summary["worst_target_delta"],
            "early_delta": summary["early_delta"],
            "mid_delta": summary["mid_delta"],
            "late_delta": summary["late_delta"],
            "tail20_delta": summary["tail20_delta"],
            "worst_subject_delta": summary["worst_subject_delta"],
            "worst_late_target_delta": summary["worst_late_target_delta"],
            "deterministic_penalty": penalty,
        }
        for target in TARGET_COLUMNS:
            option = selection[target]
            row[f"{target}_source"] = option.source
            row[f"{target}_weight"] = option.weight
            row[f"{target}_mode"] = option.mode
            row[f"{target}_delta"] = option.target_delta
        rows.append(row)
        cache[name] = selection

    score_df = pd.DataFrame(rows).drop_duplicates("name").sort_values(["deterministic_penalty", "avg_log_loss"]).reset_index(drop=True)
    score_df.to_csv(output_dir / "minimax_grid_scores.csv", index=False)
    deterministic = score_df[
        (score_df["improvement"] > 0)
        & (score_df["improved_folds"] >= args.min_folds_improved)
        & (score_df["worst_target_delta"] >= -args.max_target_regression)
        & (score_df["late_delta"] >= -args.max_block_regression)
        & (score_df["tail20_delta"] >= -args.max_tail_regression)
        & (score_df["worst_subject_delta"] >= -args.max_subject_regression)
        & (score_df["worst_late_target_delta"] >= -args.max_late_target_regression)
    ].head(args.top_bootstrap)
    if deterministic.empty:
        deterministic = score_df.head(args.top_bootstrap)

    rng = np.random.default_rng(args.seed)
    boot_indices = rng.integers(0, len(train), size=(args.bootstrap, len(train)))
    boot_rows = []
    for row in deterministic.to_dict(orient="records"):
        selection = cache[str(row["name"])]
        summary = summarize_selection(selection, base_avg, folds, blocks, subject_groups)
        boot = bootstrap_p025(summary["row_delta"], boot_indices)  # type: ignore[arg-type]
        promote = (
            boot["improvement_p025"] > args.min_p025
            and row["improvement"] > 0
            and int(row["improved_folds"]) >= args.min_folds_improved
            and float(row["worst_target_delta"]) >= -args.max_target_regression
            and float(row["late_delta"]) >= -args.max_block_regression
            and float(row["tail20_delta"]) >= -args.max_tail_regression
            and float(row["worst_subject_delta"]) >= -args.max_subject_regression
            and float(row["worst_late_target_delta"]) >= -args.max_late_target_regression
        )
        boot_rows.append({**row, **boot, "promote": bool(promote)})
    boot_df = pd.DataFrame(boot_rows).sort_values(["promote", "avg_log_loss", "improvement_p025"], ascending=[False, True, False])
    boot_df.to_csv(output_dir / "minimax_bootstrap_scores.csv", index=False)

    if not boot_df.empty and bool(boot_df.iloc[0]["promote"]):
        selected = boot_df.iloc[0].to_dict()
    elif not boot_df.empty:
        selected = boot_df.sort_values(["improvement_p025", "avg_log_loss"], ascending=[False, True]).iloc[0].to_dict()
    else:
        selected = score_df.iloc[0].to_dict()
        selected.update({"promote": False, "improvement_p025": np.nan, "improvement_p500": np.nan, "improvement_p975": np.nan})
    best_selection = cache[str(selected["name"])]

    final_oof = base_pred.copy()
    final_submission = base_submission.copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        option = best_selection[target]
        final_oof[:, target_i] = option.pred
        final_submission[:, target_i] = option.submission

    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = final_oof[:, target_i]
    oof_path = output_dir / "oof_minimax_targetwise_blend.csv"
    oof.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = final_submission[:, target_i]
    submission_path = output_dir / "submission_minimax_targetwise_blend.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "baseline": args.baseline,
        "base_avg_log_loss": base_avg,
        "selected": selected,
        "selected_options": {
            target: {
                "source": best_selection[target].source,
                "weight": best_selection[target].weight,
                "mode": best_selection[target].mode,
                "target_delta": best_selection[target].target_delta,
            }
            for target in TARGET_COLUMNS
        },
        "args": vars(args),
    }
    (output_dir / "minimax_targetwise_blend_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Minimax Targetwise Blend Search",
        "",
        f"- Baseline: `{args.baseline}`",
        f"- Base avg logloss: `{base_avg:.6f}`",
        f"- Selected avg logloss: `{float(selected['avg_log_loss']):.6f}`",
        f"- Selected promote: `{selected.get('promote', False)}`",
        f"- Selected p025: `{selected.get('improvement_p025', np.nan)}`",
        "",
        "## Selected Options",
        "",
        dataframe_to_markdown(
            pd.DataFrame(
                [
                    {
                        "target": target,
                        "source": best_selection[target].source,
                        "weight": best_selection[target].weight,
                        "mode": best_selection[target].mode,
                        "target_delta": best_selection[target].target_delta,
                    }
                    for target in TARGET_COLUMNS
                ]
            )
        ),
        "",
        "## Bootstrap Top",
        "",
        dataframe_to_markdown(boot_df.head(20)) if not boot_df.empty else "_No bootstrap rows._",
        "",
    ]
    (output_dir / "minimax_targetwise_blend_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"selected avg={float(selected['avg_log_loss']):.6f} promote={selected.get('promote', False)} p025={selected.get('improvement_p025', np.nan)}")
    print(pd.DataFrame(report["selected_options"]).T.to_string())
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fast targetwise beam search for robust/minimax probability blends.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--weights", default="0.01,0.02,0.03,0.05,0.08,0.1,0.15,0.2,0.3,0.4,0.5,0.65,0.8,1.0")
    parser.add_argument("--modes", default="prob,logit")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--beam-size", type=int, default=400)
    parser.add_argument("--max-options-per-target", type=int, default=18)
    parser.add_argument("--top-bootstrap", type=int, default=200)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--min-option-delta", type=float, default=0.000005)
    parser.add_argument("--min-option-folds", type=int, default=2)
    parser.add_argument("--option-stress-weight", type=float, default=0.25)
    parser.add_argument("--min-folds-improved", type=int, default=4)
    parser.add_argument("--max-target-regression", type=float, default=0.001)
    parser.add_argument("--max-block-regression", type=float, default=0.0015)
    parser.add_argument("--max-tail-regression", type=float, default=0.0025)
    parser.add_argument("--max-subject-regression", type=float, default=0.006)
    parser.add_argument("--max-late-target-regression", type=float, default=0.010)
    parser.add_argument("--min-p025", type=float, default=0.00002)
    parser.add_argument("--fold-penalty", type=float, default=0.002)
    parser.add_argument("--constraint-penalty", type=float, default=4.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
