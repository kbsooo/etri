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
class Candidate:
    name: str
    oof_path: Path
    submission_path: Path | None


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[np.ndarray]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_indices: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(), n_folds)
        for fold, chunk in enumerate(chunks):
            val_indices[fold].extend(chunk.tolist())
    return [np.array(sorted(indices), dtype=int) for indices in val_indices]


def add_panel_position(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="test", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    out = all_rows.sort_index()
    train_pos = out[out["_split"].eq("train")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    test_pos = out[out["_split"].eq("test")].sort_values("_row")[["panel_index", "panel_position"]].reset_index(drop=True)
    train_out = train.reset_index(drop=True).copy()
    test_out = sample.reset_index(drop=True).copy()
    train_out[["panel_index", "panel_position"]] = train_pos
    test_out[["panel_index", "panel_position"]] = test_pos
    return train_out, test_out


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    pred_cols = [f"pred_{target}" for target in TARGET_COLUMNS]
    missing = sorted(set(pred_cols) - set(oof.columns))
    if missing:
        raise ValueError(f"OOF file is missing prediction columns: {missing}")
    pred = oof[pred_cols].to_numpy(dtype=float)
    return np.clip(pred, EPS, 1.0 - EPS)


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    pred = submission[TARGET_COLUMNS].to_numpy(dtype=float)
    return np.clip(pred, EPS, 1.0 - EPS)


def per_target_log_loss(y: pd.DataFrame, pred: np.ndarray, indices: np.ndarray | None = None) -> dict[str, float]:
    if indices is None:
        indices = np.arange(len(y))
    out = {}
    for i, target in enumerate(TARGET_COLUMNS):
        out[target] = float(log_loss(y.iloc[indices][target].to_numpy(), pred[indices, i], labels=[0, 1]))
    out["avg"] = float(np.mean([out[target] for target in TARGET_COLUMNS]))
    return out


def row_losses(y: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    y_arr = y[TARGET_COLUMNS].to_numpy(dtype=float)
    pred = np.clip(pred, EPS, 1.0 - EPS)
    return -(y_arr * np.log(pred) + (1.0 - y_arr) * np.log(1.0 - pred)).mean(axis=1)


def bootstrap_improvement(base_loss: np.ndarray, candidate_loss: np.ndarray, seed: int, n_bootstrap: int) -> dict[str, float]:
    diff = base_loss - candidate_loss
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap, dtype=float)
    for i in range(n_bootstrap):
        idx = rng.integers(0, len(diff), len(diff))
        boot[i] = float(diff[idx].mean())
    return {
        "improvement": float(diff.mean()),
        "improvement_p025": float(np.quantile(boot, 0.025)),
        "improvement_p500": float(np.quantile(boot, 0.500)),
        "improvement_p975": float(np.quantile(boot, 0.975)),
    }


def slice_summary(frame: pd.DataFrame, y: pd.DataFrame, pred: np.ndarray) -> dict[str, float]:
    rows: dict[str, float] = {}
    for subject, group in frame.reset_index().groupby("subject_id", sort=True):
        score = per_target_log_loss(y, pred, group["index"].to_numpy())["avg"]
        rows[f"subject_{subject}"] = score
    for label, lo, hi in [("early", -np.inf, 1 / 3), ("mid", 1 / 3, 2 / 3), ("late", 2 / 3, np.inf)]:
        idx = frame.index[(frame["panel_position"] >= lo) & (frame["panel_position"] < hi)].to_numpy()
        if len(idx):
            rows[f"panel_{label}"] = per_target_log_loss(y, pred, idx)["avg"]
    return rows


def default_candidates() -> list[Candidate]:
    return [
        Candidate(
            "latent_temporal",
            Path("outputs/latent_decoder/oof_targetwise_temporal_blend.csv"),
            Path("outputs/latent_decoder/submission_latent_decoder_targetwise_temporal.csv"),
        ),
        Candidate(
            "master_temporal",
            Path("outputs/master_aggressive_decoder_fast/oof_temporal_master_oof_blend.csv"),
            Path("outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv"),
        ),
        Candidate(
            "q_ranker_tuned",
            Path("outputs/q_ranker_decoder_tuned/oof_q_ranker_with_baseline_s.csv"),
            Path("outputs/q_ranker_decoder_tuned/submission_q_ranker_with_baseline_s.csv"),
        ),
        Candidate(
            "master_targetwise",
            Path("outputs/master_aggressive_decoder_fast/oof_targetwise.csv"),
            Path("outputs/master_aggressive_decoder_fast/submission_master_aggressive_targetwise.csv"),
        ),
        Candidate(
            "master_best_global",
            Path("outputs/master_aggressive_decoder_fast/oof_best.csv"),
            Path("outputs/master_aggressive_decoder_fast/submission_master_aggressive_best.csv"),
        ),
        Candidate(
            "latent_targetwise",
            Path("outputs/latent_decoder/oof_targetwise.csv"),
            Path("outputs/latent_decoder/submission_latent_decoder_targetwise.csv"),
        ),
    ]


def load_candidates(args: argparse.Namespace) -> list[Candidate]:
    if not args.candidates:
        return default_candidates()
    candidates = []
    for item in args.candidates:
        parts = item.split(":")
        if len(parts) not in {2, 3}:
            raise ValueError("--candidate entries must be name:oof_path[:submission_path]")
        candidates.append(Candidate(parts[0], Path(parts[1]), Path(parts[2]) if len(parts) == 3 else None))
    return candidates


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

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    train, sample = add_panel_position(train, sample)
    y = train[TARGET_COLUMNS]
    folds = make_subject_time_folds(train, args.folds)

    baseline_name = args.baseline
    loaded: dict[str, dict] = {}
    for candidate in load_candidates(args):
        if not candidate.oof_path.exists():
            continue
        oof = normalize_keys(pd.read_csv(candidate.oof_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            raise ValueError(f"{candidate.name} OOF keys do not match train keys: {candidate.oof_path}")
        pred = prediction_matrix(oof)
        sub_pred = None
        if candidate.submission_path and candidate.submission_path.exists():
            submission = normalize_keys(pd.read_csv(candidate.submission_path))
            if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
                raise ValueError(f"{candidate.name} submission keys do not match sample keys: {candidate.submission_path}")
            sub_pred = submission_matrix(submission)
        loaded[candidate.name] = {
            "candidate": candidate,
            "pred": pred,
            "submission_pred": sub_pred,
            "row_loss": row_losses(y, pred),
            "overall": per_target_log_loss(y, pred),
            "slices": slice_summary(train, y, pred),
        }
    if baseline_name not in loaded:
        raise ValueError(f"Baseline candidate not loaded: {baseline_name}")

    base = loaded[baseline_name]
    base_fold_scores = [per_target_log_loss(y, base["pred"], fold)["avg"] for fold in folds]
    summary_rows = []
    fold_rows = []
    target_rows = []
    shift_rows = []

    for name, item in loaded.items():
        pred = item["pred"]
        overall = item["overall"]
        folds_scores = [per_target_log_loss(y, pred, fold)["avg"] for fold in folds]
        fold_improvements = [base_score - score for base_score, score in zip(base_fold_scores, folds_scores)]
        boot = bootstrap_improvement(base["row_loss"], item["row_loss"], args.seed, args.bootstrap)
        per_target_delta = {target: base["overall"][target] - overall[target] for target in TARGET_COLUMNS}
        worst_target_regression = float(min(per_target_delta.values()))
        robust_penalty = 0.35 * float(np.std(folds_scores)) + 0.15 * max(0.0, -worst_target_regression)
        robust_score = float(overall["avg"] + robust_penalty)
        promote = (
            boot["improvement_p025"] > 0.0
            and sum(delta > 0 for delta in fold_improvements) >= max(args.folds - 1, 1)
            and worst_target_regression >= -args.max_target_regression
        )
        summary_rows.append(
            {
                "name": name,
                "avg_log_loss": overall["avg"],
                "robust_score": robust_score,
                "fold_std": float(np.std(folds_scores)),
                "worst_fold": float(np.max(folds_scores)),
                "improved_folds_vs_baseline": int(sum(delta > 0 for delta in fold_improvements)),
                "worst_target_delta_vs_baseline": worst_target_regression,
                "promote": bool(promote),
                **boot,
            }
        )
        for fold_i, (score, delta) in enumerate(zip(folds_scores, fold_improvements), start=1):
            fold_rows.append({"name": name, "fold": fold_i, "avg_log_loss": score, "delta_vs_baseline": delta})
        for target in TARGET_COLUMNS:
            target_rows.append(
                {
                    "name": name,
                    "target": target,
                    "log_loss": overall[target],
                    "delta_vs_baseline": per_target_delta[target],
                }
            )
        sub_pred = item["submission_pred"]
        if sub_pred is not None:
            for i, target in enumerate(TARGET_COLUMNS):
                oof_col = pred[:, i]
                sub_col = sub_pred[:, i]
                shift_rows.append(
                    {
                        "name": name,
                        "target": target,
                        "oof_pred_mean": float(oof_col.mean()),
                        "test_pred_mean": float(sub_col.mean()),
                        "mean_shift_test_minus_oof": float(sub_col.mean() - oof_col.mean()),
                        "oof_pred_std": float(oof_col.std()),
                        "test_pred_std": float(sub_col.std()),
                        "test_overconfident_frac": float(((sub_col < 0.05) | (sub_col > 0.95)).mean()),
                    }
                )

    summary = pd.DataFrame(summary_rows).sort_values(["promote", "robust_score", "avg_log_loss"], ascending=[False, True, True])
    folds_df = pd.DataFrame(fold_rows)
    targets_df = pd.DataFrame(target_rows)
    shifts_df = pd.DataFrame(shift_rows)
    summary.to_csv(output_dir / "robust_candidate_summary.csv", index=False)
    folds_df.to_csv(output_dir / "robust_fold_scores.csv", index=False)
    targets_df.to_csv(output_dir / "robust_target_scores.csv", index=False)
    shifts_df.to_csv(output_dir / "prediction_shift_summary.csv", index=False)

    report = {
        "baseline": baseline_name,
        "folds": args.folds,
        "bootstrap": args.bootstrap,
        "summary": summary.to_dict(orient="records"),
        "fold_scores": folds_df.to_dict(orient="records"),
        "target_scores": targets_df.to_dict(orient="records"),
        "prediction_shift": shifts_df.to_dict(orient="records"),
        "promotion_rule": {
            "bootstrap_improvement_p025": "> 0",
            "improved_folds_vs_baseline": f">= {max(args.folds - 1, 1)}",
            "worst_target_regression": f">= {-args.max_target_regression}",
        },
    }
    (output_dir / "robust_oof_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    top_cols = [
        "name",
        "avg_log_loss",
        "robust_score",
        "fold_std",
        "worst_fold",
        "improved_folds_vs_baseline",
        "worst_target_delta_vs_baseline",
        "improvement_p025",
        "improvement",
        "improvement_p975",
        "promote",
    ]
    lines = [
        "# Robust OOF diagnostics",
        "",
        f"- Baseline: `{baseline_name}`",
        f"- Candidate count: {len(summary)}",
        f"- Promotion rule: bootstrap p025 > 0, at least {max(args.folds - 1, 1)}/{args.folds} folds improved, no target regression worse than {args.max_target_regression:.4f}.",
        "",
        "## Candidate summary",
        "",
        dataframe_to_markdown(summary[top_cols]),
        "",
        "## Target deltas vs baseline",
        "",
        dataframe_to_markdown(targets_df.pivot(index="name", columns="target", values="delta_vs_baseline").reset_index()),
        "",
        "## Prediction shift",
        "",
        (
            dataframe_to_markdown(
                shifts_df.groupby("name", as_index=False).agg(
                    mean_abs_shift=("mean_shift_test_minus_oof", lambda s: float(np.mean(np.abs(s)))),
                    max_overconfident_frac=("test_overconfident_frac", "max"),
                )
            )
            if not shifts_df.empty
            else "_No submission files were provided for shift diagnostics._"
        ),
        "",
    ]
    (output_dir / "robust_oof_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(summary[top_cols].to_string(index=False))
    print(f"saved report: {output_dir / 'robust_oof_report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Robust diagnostics for OOF submission candidates.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--output-dir", default="outputs/robust_eval")
    parser.add_argument("--baseline", default="latent_temporal")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--bootstrap", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-target-regression", type=float, default=0.003)
    parser.add_argument(
        "--candidates",
        nargs="*",
        default=None,
        help="Optional entries formatted as name:oof_path[:submission_path].",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
