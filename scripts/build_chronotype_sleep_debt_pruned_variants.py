from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANT_PATTERNS = {
    "sleep_to_sleep": [
        "sleep_window",
        "sleep_to_sleep",
    ],
    "phase_social_jetlag": [
        "onset_hour",
        "wake_hour",
        "midpoint",
        "social_jetlag",
        "late_bed_streak",
        "early_wake_streak",
        "circ_std",
        "weekend",
    ],
    "debt_ledger": [
        "sleep_deficit",
        "sleep_surplus",
        "eff_deficit",
        "sol_excess",
        "awakening_excess",
    ],
    "postwake_energy": [
        "postwake3h_step",
        "postwake3h_cal",
        "postwake3h_body",
        "postwake3h_mobility",
        "postwake6h_step",
        "postwake6h_cal",
        "postwake6h_body",
        "postwake6h_mobility",
        "postwake3h_ev_moving",
        "postwake6h_ev_moving",
    ],
    "postwake_digital": [
        "postwake3h_phone",
        "postwake3h_screen",
        "postwake3h_usage",
        "postwake3h_ev_phone",
        "postwake6h_phone",
        "postwake6h_screen",
        "postwake6h_usage",
        "postwake6h_ev_phone",
    ],
    "prebed_arousal": [
        "prebed6h_phone",
        "prebed6h_screen",
        "prebed6h_usage",
        "prebed6h_ev_phone",
        "prebed6h_ev_moving",
        "prebed6h_mobility",
        "prebed6h_body",
        "prebed6h_step",
        "prebed6h_cal",
    ],
}


def selected_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_PATTERNS[variant]
    return sorted(
        col
        for col in frame.columns
        if col.startswith("z_cs_") and any(pattern in col for pattern in patterns)
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
    path = output_dir / f"domain_chronotype_sleep_debt_{variant}_v1.parquet"
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
        f"# Chronotype Sleep Debt {variant} Variant",
        "",
        "## Purpose",
        "",
        "Compact subfamily split from broad chronotype/sleep-debt features.",
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
    (output_dir / "domain_chronotype_sleep_debt_pruned_variants_v1.report.json").write_text(
        json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "domain_chronotype_sleep_debt_pruned_variants_v1.report.md").write_text(
        "\n".join(
            [
                "# Chronotype Sleep Debt Pruned Variants",
                "",
                "## Purpose",
                "",
                "Split broad chronotype/sleep-debt features into compact probeable subfamilies.",
                "",
                dataframe_to_markdown(pd.DataFrame(reports)[["variant", "output", "feature_count", "rows"]]),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact chronotype/sleep-debt latent variants.")
    parser.add_argument("--input", default="artifacts/domain_chronotype_sleep_debt_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
