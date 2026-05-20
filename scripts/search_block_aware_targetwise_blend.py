from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def parse_float_list(value: str) -> list[float]:
    return [float(part) for part in value.split(",") if part.strip()]


def parse_target_list(value: str) -> list[str]:
    if value.strip().lower() == "all":
        return TARGET_COLUMNS
    targets = [part.strip() for part in value.split(",") if part.strip()]
    unknown = sorted(set(targets) - set(TARGET_COLUMNS))
    if unknown:
        raise ValueError(f"Unknown targets: {unknown}")
    return targets


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred = np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS])
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    return [np.array(sorted(indices), dtype=int) for indices in val_indices]


def add_panel_columns(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    ordered["subject_day_index"] = ordered.groupby("subject_id").cumcount()
    subject_max = ordered.groupby("subject_id")["subject_day_index"].transform("max").replace(0, 1)
    ordered["subject_position"] = ordered["subject_day_index"] / subject_max
    return ordered.sort_values("_idx").drop(columns="_idx").reset_index(drop=True)


def block_indices(frame: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "early_third": frame.index[frame["subject_position"] < 1 / 3].to_numpy(dtype=int),
        "mid_third": frame.index[(frame["subject_position"] >= 1 / 3) & (frame["subject_position"] < 2 / 3)].to_numpy(dtype=int),
        "late_third": frame.index[frame["subject_position"] >= 2 / 3].to_numpy(dtype=int),
        "tail_20pct": frame.index[frame["subject_position"] >= 0.8].to_numpy(dtype=int),
    }


def per_target_log_loss(y: pd.DataFrame, pred: np.ndarray, indices: np.ndarray | None = None) -> dict[str, float]:
    if indices is None:
        indices = np.arange(len(y), dtype=int)
    out = {
        target: float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, target_i], labels=[0, 1]))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    out["avg"] = float(np.mean([out[target] for target in TARGET_COLUMNS]))
    return out


def row_losses(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log1p(-pred)).mean(axis=1)


def bootstrap_summary(diff: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(diff), size=(n_bootstrap, len(diff)))
    boot = diff[idx].mean(axis=1)
    return {
        "improvement": float(diff.mean()),
        "improvement_p025": float(np.quantile(boot, 0.025)),
        "improvement_p500": float(np.quantile(boot, 0.500)),
        "improvement_p975": float(np.quantile(boot, 0.975)),
    }


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

    train = add_panel_columns(normalize_keys(pd.read_csv(args.train_path)))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    base_oof_df = normalize_keys(pd.read_csv(args.base_oof))
    cand_oof_df = normalize_keys(pd.read_csv(args.candidate_oof))
    base_sub_df = normalize_keys(pd.read_csv(args.base_submission))
    cand_sub_df = normalize_keys(pd.read_csv(args.candidate_submission))
    if not base_oof_df[KEY_COLUMNS].equals(train[KEY_COLUMNS]) or not cand_oof_df[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("OOF keys do not match train keys")
    if not base_sub_df[KEY_COLUMNS].equals(sample[KEY_COLUMNS]) or not cand_sub_df[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Submission keys do not match sample keys")

    y = train[TARGET_COLUMNS]
    base_pred = prediction_matrix(base_oof_df)
    cand_pred = prediction_matrix(cand_oof_df)
    base_test = submission_matrix(base_sub_df)
    cand_test = submission_matrix(cand_sub_df)
    free_targets = parse_target_list(args.targets)
    free_indices = [TARGET_COLUMNS.index(target) for target in free_targets]
    weights = parse_float_list(args.weights)
    folds = make_subject_time_folds(train, args.folds)
    blocks = block_indices(train)

    base_overall = per_target_log_loss(y, base_pred)
    base_fold_scores = [per_target_log_loss(y, base_pred, fold)["avg"] for fold in folds]
    base_block_scores = {name: per_target_log_loss(y, base_pred, idx)["avg"] for name, idx in blocks.items()}
    base_subject_scores = {
        subject: per_target_log_loss(y, base_pred, group.index.to_numpy(dtype=int))["avg"]
        for subject, group in train.groupby("subject_id", sort=True)
    }
    late_idx = blocks["late_third"]
    base_late_target_scores = {
        target: float(log_loss(y.iloc[late_idx][target], base_pred[late_idx, target_i], labels=[0, 1]))
        for target_i, target in enumerate(TARGET_COLUMNS)
    }
    base_loss = row_losses(y, base_pred)

    rows = []
    cache: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for combo in itertools.product(weights, repeat=len(free_indices)):
        target_weights = np.zeros(len(TARGET_COLUMNS), dtype=float)
        for target_i, weight in zip(free_indices, combo):
            target_weights[target_i] = weight
        pred = np.clip(base_pred + (cand_pred - base_pred) * target_weights[None, :], EPS, 1.0 - EPS)
        test = np.clip(base_test + (cand_test - base_test) * target_weights[None, :], EPS, 1.0 - EPS)
        overall = per_target_log_loss(y, pred)
        fold_scores = [per_target_log_loss(y, pred, fold)["avg"] for fold in folds]
        block_scores = {name: per_target_log_loss(y, pred, idx)["avg"] for name, idx in blocks.items()}
        subject_deltas = [
            base_subject_scores[subject] - per_target_log_loss(y, pred, group.index.to_numpy(dtype=int))["avg"]
            for subject, group in train.groupby("subject_id", sort=True)
        ]
        late_target_delta = {
            target: base_late_target_scores[target] - float(log_loss(y.iloc[late_idx][target], pred[late_idx, target_i], labels=[0, 1]))
            for target_i, target in enumerate(TARGET_COLUMNS)
        }
        target_deltas = {target: base_overall[target] - overall[target] for target in TARGET_COLUMNS}
        name = "_".join([f"{target}{target_weights[TARGET_COLUMNS.index(target)]:g}" for target in free_targets])
        row = {
            "name": name,
            "avg_log_loss": overall["avg"],
            "delta_vs_base": base_overall["avg"] - overall["avg"],
            "fold_std": float(np.std(fold_scores)),
            "worst_fold": float(np.max(fold_scores)),
            "improved_folds": int(sum(base_score > score for base_score, score in zip(base_fold_scores, fold_scores))),
            "worst_target_delta": float(min(target_deltas.values())),
            "early_delta": base_block_scores["early_third"] - block_scores["early_third"],
            "mid_delta": base_block_scores["mid_third"] - block_scores["mid_third"],
            "late_delta": base_block_scores["late_third"] - block_scores["late_third"],
            "tail20_delta": base_block_scores["tail_20pct"] - block_scores["tail_20pct"],
            "worst_subject_delta": float(min(subject_deltas)),
            "worst_late_target_delta": float(min(late_target_delta.values())),
            **{f"w_{target}": float(target_weights[target_i]) for target_i, target in enumerate(TARGET_COLUMNS)},
        }
        rows.append(row)
        cache[name] = (pred, test, target_weights)

    scores = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)
    deterministic = scores[
        (scores["delta_vs_base"] > 0)
        & (scores["improved_folds"] >= max(args.folds - 1, 1))
        & (scores["worst_target_delta"] >= -args.max_target_regression)
        & (scores["late_delta"] >= -args.max_block_regression)
        & (scores["tail20_delta"] >= -args.max_tail_regression)
        & (scores["worst_subject_delta"] >= -args.max_subject_regression)
        & (scores["worst_late_target_delta"] >= -args.max_late_target_regression)
    ].head(args.top_bootstrap)

    boot_rows = []
    for row in deterministic.to_dict(orient="records"):
        pred, _, _ = cache[str(row["name"])]
        diff = base_loss - row_losses(y, pred)
        boot = bootstrap_summary(diff, args.seed, args.bootstrap)
        promote = boot["improvement_p025"] > args.min_p025
        boot_rows.append({**row, **boot, "promote": bool(promote)})
    boot_df = pd.DataFrame(boot_rows)
    if boot_df.empty or boot_df[boot_df["promote"]].empty:
        selected = scores.sort_values("avg_log_loss").iloc[0].to_dict()
        selected.update({"promote": False, "improvement_p025": np.nan, "improvement": selected["delta_vs_base"], "improvement_p975": np.nan})
    else:
        selected = boot_df[boot_df["promote"]].sort_values(["avg_log_loss", "improvement_p025"], ascending=[True, False]).iloc[0].to_dict()

    best_pred, best_test, best_weights = cache[str(selected["name"])]
    scores.to_csv(output_dir / "block_aware_grid_scores.csv", index=False)
    if boot_df.empty:
        boot_df.to_csv(output_dir / "block_aware_bootstrap_scores.csv", index=False)
    else:
        boot_df.sort_values(["promote", "avg_log_loss"], ascending=[False, True]).to_csv(output_dir / "block_aware_bootstrap_scores.csv", index=False)

    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = best_pred[:, target_i]
    oof_path = output_dir / "oof_block_aware_targetwise_blend.csv"
    oof.to_csv(oof_path, index=False)

    submission = pd.read_csv(args.sample_path)
    for target_i, target in enumerate(TARGET_COLUMNS):
        submission[target] = best_test[:, target_i]
    submission_path = output_dir / "submission_block_aware_targetwise_blend.csv"
    submission.to_csv(submission_path, index=False)

    report = {
        "base_avg_log_loss": base_overall["avg"],
        "selected": selected,
        "selected_weights": {target: float(best_weights[i]) for i, target in enumerate(TARGET_COLUMNS)},
        "args": vars(args),
    }
    (output_dir / "block_aware_targetwise_blend_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Block-aware Targetwise Blend Search",
        "",
        f"- Base avg logloss: `{base_overall['avg']:.6f}`",
        f"- Selected avg logloss: `{selected['avg_log_loss']:.6f}`",
        f"- Selected: `{selected['name']}`",
        f"- Promote: `{selected['promote']}`",
        "",
        "## Selected Weights",
        "",
        dataframe_to_markdown(pd.DataFrame([{target: float(best_weights[i]) for i, target in enumerate(TARGET_COLUMNS)}])),
        "",
        "## Bootstrap Top",
        "",
        dataframe_to_markdown(boot_df.sort_values(["promote", "avg_log_loss"], ascending=[False, True]).head(12)) if not boot_df.empty else "_No deterministic candidates passed block gates._",
        "",
    ]
    (output_dir / "block_aware_targetwise_blend_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"selected={selected['name']} avg={selected['avg_log_loss']:.6f} promote={selected['promote']} p025={selected['improvement_p025']}")
    print(pd.DataFrame([{target: float(best_weights[i]) for i, target in enumerate(TARGET_COLUMNS)}]).to_string(index=False))
    print(f"saved: {submission_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Targetwise probability blend search with chronological block and subject gates.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", required=True)
    parser.add_argument("--base-submission", required=True)
    parser.add_argument("--candidate-oof", required=True)
    parser.add_argument("--candidate-submission", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--targets", default="all")
    parser.add_argument("--weights", default="0,0.1,0.2,0.3,0.4,0.5,0.65,0.8,1.0")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--top-bootstrap", type=int, default=200)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-target-regression", type=float, default=0.001)
    parser.add_argument("--max-block-regression", type=float, default=0.0015)
    parser.add_argument("--max-tail-regression", type=float, default=0.0025)
    parser.add_argument("--max-subject-regression", type=float, default=0.006)
    parser.add_argument("--max-late-target-regression", type=float, default=0.010)
    parser.add_argument("--min-p025", type=float, default=0.0)
    return parser.parse_args()


if __name__ == "__main__":
    main()
