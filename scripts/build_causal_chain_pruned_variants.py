from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
VARIANTS = {
    "load": ["physical_load", "mobility_context", "high_load", "load_after"],
    "arousal": ["evening_arousal", "arousal", "late_arousal", "onset_late"],
    "opportunity": ["sleep_opportunity", "opportunity", "phase_compression", "wake_late", "onset_late"],
    "continuity": ["sleep_friction", "continuity", "fragmented", "sleep_quality"],
    "recovery": ["morning_recovery", "recovery", "fatigue"],
    "chain_interactions": ["chain_score", "gap", "deficit", "high_load_low", "load_after_bad", "arousal_to"],
}


def choose_columns(columns: list[str], patterns: list[str]) -> list[str]:
    return [col for col in columns if col.startswith("z_cc_") and any(pattern in col for pattern in patterns)]


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    source = pd.read_parquet(args.input).copy()
    summaries = []
    for variant, patterns in VARIANTS.items():
        selected = choose_columns(source.columns.tolist(), patterns)
        if not selected:
            raise ValueError(f"No selected columns for {variant}")
        out = source[KEY_COLUMNS + sorted(selected)].copy()
        output = Path(args.output_pattern.format(variant=variant))
        output.parent.mkdir(parents=True, exist_ok=True)
        out.to_parquet(output, index=False)
        summary = {
            "variant": variant,
            "output": str(output),
            "rows": int(len(out)),
            "feature_count": int(len(selected)),
            "patterns": patterns,
        }
        summaries.append(summary)
        output.with_suffix(".report.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        stats = pd.DataFrame(
            {
                "feature": sorted(selected),
                "mean": [float(out[c].mean()) for c in sorted(selected)],
                "std": [float(out[c].std()) for c in sorted(selected)],
            }
        )
        md = [
            f"# Causal Chain Variant: {variant}",
            "",
            f"- Output: `{output}`",
            f"- Rows: `{len(out)}`",
            f"- Feature count: `{len(selected)}`",
            "",
            "## Patterns",
            "",
            ", ".join(f"`{p}`" for p in patterns),
            "",
            "## Feature Summary",
            "",
            dataframe_to_markdown(stats.head(50)),
        ]
        output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")

    report = {"input": args.input, "variants": summaries}
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = ["# Causal Chain Pruned Variants", "", dataframe_to_markdown(pd.DataFrame(summaries))]
    report_path.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split causal chain latent features into pruned variants.")
    parser.add_argument("--input", default="artifacts/domain_causal_chain_v1.parquet")
    parser.add_argument("--output-pattern", default="artifacts/domain_causal_chain_{variant}_v1.parquet")
    parser.add_argument("--report", default="artifacts/domain_causal_chain_pruned_variants_v1.report.json")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
