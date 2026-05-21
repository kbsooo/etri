from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANTS = {
    "full": "artifacts/domain_sleep_onset_transition_v1.parquet",
    "last_event_latency": "artifacts/domain_sleep_onset_transition_last_event_latency_v1.parquet",
    "shutdown_slope": "artifacts/domain_sleep_onset_transition_shutdown_slope_v1.parquet",
    "prebed_fragmentation": "artifacts/domain_sleep_onset_transition_prebed_fragmentation_v1.parquet",
    "light_environment_transition": "artifacts/domain_sleep_onset_transition_light_environment_transition_v1.parquet",
    "charging_settle": "artifacts/domain_sleep_onset_transition_charging_settle_v1.parquet",
    "onset_consensus": "artifacts/domain_sleep_onset_transition_onset_consensus_v1.parquet",
}


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    best = normalize_keys(pd.read_parquet(args.best))
    best_cols = [c for c in best.columns if c.startswith("z_")]
    if not best_cols:
        raise ValueError(f"No z_* columns in best latent {args.best}")
    summaries = []
    for variant, path in VARIANTS.items():
        extra = normalize_keys(pd.read_parquet(path))
        extra_cols = [c for c in extra.columns if c.startswith("z_")]
        if not extra_cols:
            raise ValueError(f"No z_* columns in {path}")
        merged = best[KEY_COLUMNS + best_cols].merge(extra[KEY_COLUMNS + extra_cols], on=KEY_COLUMNS, how="inner", validate="one_to_one")
        output = output_dir / f"domain_best_plus_sleep_onset_transition_{variant}_v1.parquet"
        merged.to_parquet(output, index=False)
        summary = {
            "variant": variant,
            "input": path,
            "output": str(output),
            "rows": int(len(merged)),
            "best_feature_count": int(len(best_cols)),
            "extra_feature_count": int(len(extra_cols)),
            "feature_count": int(len(best_cols) + len(extra_cols)),
        }
        summaries.append(summary)
        output.with_suffix(".report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    report = {"best": args.best, "variants": summaries}
    report_path = output_dir / "domain_sleep_onset_transition_plus_best_latents_v1.report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = pd.DataFrame(summaries)
    report_path.with_suffix(".md").write_text(
        "# Sleep Onset Transition Plus Best Latents\n\n"
        + dataframe_to_markdown(rows[["variant", "output", "feature_count", "rows"]]),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Concatenate best late-fusion latent with sleep-onset transition variants.")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
