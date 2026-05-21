from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

from train_deep_learning_golf import EPS, grouped_abs_drift, macro_f1_at_half
from train_hourly_transformer_encoder import dataframe_to_markdown
from train_pruned_state_decoder import average_log_loss, drift_vs_reference, write_prediction
from train_s2_sleep_retrieval_encoder import KEY_COLUMNS, TARGET_COLUMNS, normalize_keys


def load_candidates(input_dir: Path) -> tuple[list[str], np.ndarray, np.ndarray]:
    path = input_dir / "latent_golf_candidate_predictions.npz"
    if not path.exists():
        raise FileNotFoundError(f"Missing candidate predictions: {path}")
    data = np.load(path, allow_pickle=True)
    sources = [str(item) for item in data["sources"].tolist()]
    return sources, data["oof"].astype(float), data["sample"].astype(float)


def source_index(sources: list[str]) -> dict[str, int]:
    return {source: i for i, source in enumerate(sources)}


def best_count_sources(counts: pd.DataFrame, min_count: int) -> dict[str, str]:
    chosen: dict[str, str] = {}
    for target in TARGET_COLUMNS:
        part = counts[counts["target"] == target].sort_values(["count", "source"], ascending=[False, True])
        if part.empty:
            continue
        row = part.iloc[0]
        if int(row["count"]) >= min_count:
            chosen[target] = str(row["source"])
    return chosen


def compose_policy(
    policy_name: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    sources: list[str],
    oof_all: np.ndarray,
    sample_all: np.ndarray,
    target_sources: dict[str, str],
    fallback_source: str,
    reference_submission: str,
) -> dict[str, object]:
    idx = source_index(sources)
    if fallback_source not in idx:
        raise ValueError(f"Fallback source not found: {fallback_source}")
    oof = oof_all[idx[fallback_source]].copy()
    sample_pred = sample_all[idx[fallback_source]].copy()
    used = {}
    for target_i, target in enumerate(TARGET_COLUMNS):
        source = target_sources.get(target, fallback_source)
        if source not in idx:
            raise ValueError(f"Policy {policy_name} selected missing source for {target}: {source}")
        oof[:, target_i] = oof_all[idx[source], :, target_i]
        sample_pred[:, target_i] = sample_all[idx[source], :, target_i]
        used[target] = source
    oof = np.clip(oof, EPS, 1.0 - EPS)
    sample_pred = np.clip(sample_pred, EPS, 1.0 - EPS)
    avg, per_target = average_log_loss(train[TARGET_COLUMNS], oof)
    return {
        "policy": policy_name,
        "avg_log_loss": float(avg),
        "macro_f1_at_0p5": macro_f1_at_half(train[TARGET_COLUMNS], oof),
        "per_target": {target: float(per_target[target]) for target in TARGET_COLUMNS},
        "sources": used,
        "oof": oof,
        "sample": sample_pred,
        "drift_vs_reference": drift_vs_reference(sample, sample_pred, Path(reference_submission) if reference_submission else None),
        "subject_drift_vs_reference": grouped_abs_drift(sample, sample_pred, reference_submission, "subject_id"),
    }


def target_losses(train: pd.DataFrame, pred: np.ndarray) -> dict[str, float]:
    return {
        target: float(log_loss(train[target].to_numpy(int), pred[:, i], labels=[0, 1]))
        for i, target in enumerate(TARGET_COLUMNS)
    }


def run(args: argparse.Namespace) -> None:
    input_dir = Path(args.input_dir)
    nested_dir = Path(args.nested_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    sources, oof_all, sample_all = load_candidates(input_dir)
    scores = pd.read_csv(input_dir / "latent_golf_scores.csv")
    counts = pd.read_csv(nested_dir / "nested_selection_counts.csv")
    full_selection = pd.read_csv(nested_dir / "full_targetwise_selection_from_fold_losses.csv")

    subject_prior = "subject_prior"
    best_global = str(scores.sort_values("avg_log_loss").iloc[0]["source"])
    full_target_map = {str(row["target"]): str(row["source"]) for _, row in full_selection.iterrows()}
    ge3_map = best_count_sources(counts, 3)
    ge4_map = best_count_sources(counts, 4)
    ge5_map = best_count_sources(counts, 5)

    policies = [
        ("best_global", {}, best_global),
        ("nested_ge5_on_prior", ge5_map, subject_prior),
        ("nested_ge4_on_prior", ge4_map, subject_prior),
        ("nested_ge3_on_prior", ge3_map, subject_prior),
        ("nested_ge5_on_global", ge5_map, best_global),
        ("nested_ge4_on_global", ge4_map, best_global),
        ("nested_ge3_on_global", ge3_map, best_global),
        ("full_targetwise_upper_bound", full_target_map, subject_prior),
    ]

    results = []
    for name, target_map, fallback in policies:
        result = compose_policy(
            name,
            train,
            sample,
            sources,
            oof_all,
            sample_all,
            target_map,
            fallback,
            args.reference_submission,
        )
        write_prediction(output_dir / f"oof_{name}.csv", train, result["oof"], oof=True)
        write_prediction(output_dir / f"submission_{name}.csv", sample, result["sample"], oof=False)
        row = {
            "policy": name,
            "avg_log_loss": result["avg_log_loss"],
            "macro_f1_at_0p5": result["macro_f1_at_0p5"],
            "drift_vs_reference": result["drift_vs_reference"].get("mean_abs_drift"),
            "fallback": fallback,
            "n_overridden_targets": sum(result["sources"][target] != fallback for target in TARGET_COLUMNS),
            **target_losses(train, result["oof"]),
        }
        results.append(row)
        result_for_json = {k: v for k, v in result.items() if k not in {"oof", "sample"}}
        (output_dir / f"policy_{name}.json").write_text(json.dumps(result_for_json, indent=2), encoding="utf-8")

    result_df = pd.DataFrame(results).sort_values("avg_log_loss").reset_index(drop=True)
    result_df.to_csv(output_dir / "fixed_policy_scores.csv", index=False)
    best_policy = str(result_df.iloc[0]["policy"])
    best_json = json.loads((output_dir / f"policy_{best_policy}.json").read_text(encoding="utf-8"))
    report = {
        "input_dir": str(input_dir),
        "nested_dir": str(nested_dir),
        "best_policy": best_policy,
        "best_avg_log_loss": float(result_df.iloc[0]["avg_log_loss"]),
        "best_drift_vs_reference": best_json["drift_vs_reference"],
        "best_sources": best_json["sources"],
        "best_global_source": best_global,
        "nested_ge3_sources": ge3_map,
        "nested_ge4_sources": ge4_map,
        "nested_ge5_sources": ge5_map,
        "scores": result_df.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = [
        "# Fixed Deep Learning Golf Policy",
        "",
        "## Result",
        "",
        f"- Best policy: `{best_policy}`",
        f"- Best OOF avg logloss: `{result_df.iloc[0]['avg_log_loss']:.6f}`",
        f"- Drift vs v83: `{result_df.iloc[0]['drift_vs_reference']:.6f}`",
        f"- Best global source: `{best_global}`",
        "",
        "## Policy Scores",
        "",
        dataframe_to_markdown(result_df),
        "",
        "## Nested Count Maps",
        "",
        f"- ge5: `{ge5_map}`",
        f"- ge4: `{ge4_map}`",
        f"- ge3: `{ge3_map}`",
        "",
        "## Best Policy Sources",
        "",
        dataframe_to_markdown(pd.DataFrame([{"target": target, "source": source} for target, source in best_json["sources"].items()])),
        "",
        "## Decision",
        "",
        "This converts nested selection counts into fixed target rules. It is still an OOF policy comparison, but it avoids choosing each target source directly from full-train OOF losses.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compose fixed target rules from saved latent golf candidates.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--nested-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reference-submission", default="outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
