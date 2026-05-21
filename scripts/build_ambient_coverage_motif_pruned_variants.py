from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANT_PATTERNS = {
    "ambient_light": [
        "light",
        "mlight",
        "wlight",
        "bright",
        "dark",
        "amb_",
        "ambient",
        "silence",
        "speech",
        "music",
    ],
    "coverage_no_wear": [
        "coverage",
        "no_wear",
        "low_coverage",
        "present_",
        "missing_run",
        "missing_until_next",
        "phone_nowear",
        "phone_lowcov",
    ],
    "motif_distance": [
        "motif",
    ],
    "night_environment": [
        "night",
        "lateNight",
        "z_night",
        "night_",
    ],
    "coverage_rhythm": [
        "coverage_transition",
        "coverage_mean",
        "coverage_std",
        "low_coverage_longest",
        "no_wear_longest",
        "past7",
        "past14",
    ],
}


def selected_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_PATTERNS[variant]
    return sorted(
        col
        for col in frame.columns
        if col.startswith("z_acm_") and any(pattern in col for pattern in patterns)
    )


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


def write_variant(frame: pd.DataFrame, variant: str, output_dir: Path) -> dict[str, object]:
    cols = selected_columns(frame, variant)
    if not cols:
        raise ValueError(f"No selected columns for {variant}")
    out = frame[KEY_COLUMNS + cols].copy()
    path = output_dir / f"domain_ambient_coverage_motif_{variant}_v1.parquet"
    out.to_parquet(path, index=False)
    report = {
        "variant": variant,
        "output": str(path),
        "rows": int(len(out)),
        "feature_count": int(len(cols)),
        "patterns": VARIANT_PATTERNS[variant],
    }
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    coverage = pd.DataFrame(
        {
            "feature": cols,
            "mean": [float(out[c].mean(skipna=True)) for c in cols],
            "std": [float(out[c].std(skipna=True)) for c in cols],
        }
    )
    md = [
        f"# Ambient Coverage Motif {variant} Variant",
        "",
        "## Purpose",
        "",
        "Compact subfamily split from broad ambient/coverage/motif features.",
        "",
        f"- Output: `{path}`",
        f"- Rows: `{len(out)}`",
        f"- Feature count: `{len(cols)}`",
        "",
        "## Pattern Rules",
        "",
        ", ".join(f"`{p}`" for p in VARIANT_PATTERNS[variant]),
        "",
        "## Feature Coverage",
        "",
        dataframe_to_markdown(coverage.head(40)),
    ]
    path.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")
    return report


def run(args: argparse.Namespace) -> None:
    frame = pd.read_parquet(args.input).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = [write_variant(frame, variant, output_dir) for variant in VARIANT_PATTERNS]
    (output_dir / "domain_ambient_coverage_motif_pruned_variants_v1.report.json").write_text(
        json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "domain_ambient_coverage_motif_pruned_variants_v1.report.md").write_text(
        "\n".join(
            [
                "# Ambient Coverage Motif Pruned Variants",
                "",
                "## Purpose",
                "",
                "Split ambient/coverage/motif features into compact probeable subfamilies.",
                "",
                dataframe_to_markdown(pd.DataFrame(reports)[["variant", "output", "feature_count", "rows"]]),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact ambient/coverage/motif variants.")
    parser.add_argument("--input", default="artifacts/domain_ambient_coverage_motif_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
