from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_pruned_state_decoder import average_log_loss, drift_vs_reference, write_prediction
from train_s2_sleep_retrieval_encoder import EPS, TARGET_COLUMNS, normalize_keys
from train_hourly_transformer_encoder import dataframe_to_markdown


def collect_prediction_pairs(output_dirs: list[Path]) -> list[tuple[str, Path, Path]]:
    pairs: list[tuple[str, Path, Path]] = []
    for output_dir in output_dirs:
        for view_dir in sorted(path for path in output_dir.iterdir() if path.is_dir()):
            for stem in ("targetwise", "best_global"):
                oof_path = view_dir / f"oof_{stem}.csv"
                sub_path = view_dir / f"submission_{stem}.csv"
                if oof_path.exists() and sub_path.exists():
                    pairs.append((f"{view_dir.name}__{stem}", oof_path, sub_path))
    if not pairs:
        raise FileNotFoundError(f"No hourly transformer prediction pairs found under: {output_dirs}")
    return pairs


def prediction_matrix(path: Path, target_prefix: bool) -> np.ndarray:
    frame = pd.read_csv(path)
    cols = [f"pred_{target}" if target_prefix else target for target in TARGET_COLUMNS]
    return np.clip(frame[cols].to_numpy(float), EPS, 1.0 - EPS)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    pairs = collect_prediction_pairs([Path(item) for item in args.input_dirs])

    rows = []
    oof_by_name: dict[str, np.ndarray] = {}
    sub_by_name: dict[str, np.ndarray] = {}
    for name, oof_path, sub_path in pairs:
        oof = prediction_matrix(oof_path, target_prefix=True)
        sub = prediction_matrix(sub_path, target_prefix=False)
        avg, per_target = average_log_loss(train[TARGET_COLUMNS], oof)
        rows.append({"source": name, "avg_log_loss": avg, **per_target})
        oof_by_name[name] = oof
        sub_by_name[name] = sub
    score_df = pd.DataFrame(rows).sort_values("avg_log_loss").reset_index(drop=True)

    target_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=float)
    target_sub = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    selected_rows = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        best = min(rows, key=lambda row: row[target])
        source = str(best["source"])
        target_oof[:, target_i] = oof_by_name[source][:, target_i]
        target_sub[:, target_i] = sub_by_name[source][:, target_i]
        selected_rows.append({"target": target, "source": source, "target_log_loss": float(best[target])})

    target_oof = np.clip(target_oof, EPS, 1.0 - EPS)
    target_sub = np.clip(target_sub, EPS, 1.0 - EPS)
    target_avg, target_per = average_log_loss(train[TARGET_COLUMNS], target_oof)
    drift = drift_vs_reference(sample, target_sub, Path(args.reference_submission) if args.reference_submission else None)

    score_df.to_csv(output_dir / "source_scores.csv", index=False)
    pd.DataFrame(selected_rows).to_csv(output_dir / "target_selection.csv", index=False)
    write_prediction(output_dir / "oof_hourly_transformer_cross_view_targetwise.csv", train, target_oof, oof=True)
    write_prediction(output_dir / "submission_hourly_transformer_cross_view_targetwise.csv", sample, target_sub, oof=False)

    report = {
        "avg_log_loss": target_avg,
        "per_target": target_per,
        "selected": selected_rows,
        "drift_vs_reference": drift,
        "n_sources": len(rows),
        "note": "Full-OOF target-wise view selection. Use as signal discovery; nested selection is required before treating it as honest validation.",
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Hourly Transformer Cross-View Diagnostic",
        "",
        "## Result",
        "",
        f"- Full-OOF target-wise avg logloss: `{target_avg:.6f}`",
        f"- Drift vs v83 reference: `{drift.get('mean_abs_drift', float('nan')):.6f}`",
        f"- Sources searched: `{len(rows)}`",
        "",
        "## Selected Sources",
        "",
        dataframe_to_markdown(pd.DataFrame(selected_rows)),
        "",
        "## Top Sources",
        "",
        dataframe_to_markdown(score_df.head(12)),
        "",
        "## Caveat",
        "",
        "This is intentionally a breakthrough-search diagnostic, not an honest final score. It selects the best view per target on full OOF labels, so nested view selection is required before using this as a submission-quality estimate.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a target-wise diagnostic ensemble over hourly Transformer views.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument(
        "--input-dirs",
        nargs="+",
        default=["outputs/hourly_transformer_encoder_v1", "outputs/hourly_transformer_encoder_v1_extra"],
    )
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    parser.add_argument("--output-dir", default="outputs/hourly_transformer_cross_view_diagnostic_v1")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
