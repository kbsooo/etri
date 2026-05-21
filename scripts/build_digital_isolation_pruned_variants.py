from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
VARIANTS = {
    "social_isolation": [
        "social",
        "passive_over_social",
        "isolation",
        "passive_share",
        "social_share",
    ],
    "app_diversity_shift": [
        "entropy",
        "hhi",
        "top1",
        "profile_jsd",
    ],
    "phone_fragmentation": [
        "phone_start",
        "phone_burst",
        "short_check",
        "screen_without_usage",
        "phone_still",
        "phone_move",
    ],
    "prebed_consumption": [
        "prebed",
    ],
    "digital_rhythm": [
        "night",
        "evening",
        "past7",
        "past14",
        "burstiness",
    ],
}


def choose_columns(columns: list[str], patterns: list[str]) -> list[str]:
    return [
        col
        for col in columns
        if col.startswith("z_di_") and any(pattern in col for pattern in patterns)
    ]


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
    all_cols = source.columns.tolist()
    summaries = []
    for variant, patterns in VARIANTS.items():
        selected = choose_columns(all_cols, patterns)
        if not selected:
            raise ValueError(f"No columns selected for {variant}")
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
            f"# Digital Isolation Variant: {variant}",
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
    md = ["# Digital Isolation Pruned Variants", "", dataframe_to_markdown(pd.DataFrame(summaries))]
    report_path.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split digital isolation features into pruned hypothesis variants.")
    parser.add_argument("--input", default="artifacts/domain_digital_isolation_v1.parquet")
    parser.add_argument(
        "--output-pattern",
        default="artifacts/domain_digital_isolation_{variant}_v1.parquet",
    )
    parser.add_argument("--report", default="artifacts/domain_digital_isolation_pruned_variants_v1.report.json")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
