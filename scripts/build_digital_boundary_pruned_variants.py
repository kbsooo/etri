from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]


VARIANT_PATTERNS = {
    "core": [
        "boundary_disruption_score",
        "morning_sluggish_score",
        "last_phone_before_onset_min",
        "first_phone_after_wake_min",
        "first_move_after_wake_min",
        "wake_phone_before_move_min",
        "phone_before_sleep_recency",
    ],
    "prebed": [
        "prebed1h_phone",
        "prebed2h_phone",
        "prebed4h_phone",
        "prebed_total",
        "prebed_stim",
        "prebed_social",
        "prebed_share",
    ],
    "sleep_phone": [
        "sleep_phone",
        "sleep_usage",
        "sleep_screen",
        "sleep_charging",
        "sleep_lowcov",
        "sleep_without_charging",
    ],
    "postwake": [
        "postwake1h_phone",
        "postwake2h_phone",
        "postwake1h_step",
        "postwake2h_step",
        "first_phone_after_wake",
        "first_move_after_wake",
        "wake_phone",
        "morning_sluggish",
    ],
    "app_stim": [
        "app_total",
        "app_stim",
        "app_social",
        "app_entropy",
        "prebed_total",
        "prebed_stim",
        "prebed_social",
        "prebed_entropy",
    ],
}


def select_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_PATTERNS[variant]
    selected = []
    for col in frame.columns:
        if not col.startswith("z_db_"):
            continue
        if any(pattern in col for pattern in patterns):
            selected.append(col)
    return sorted(selected)


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
    cols = select_columns(frame, variant)
    if not cols:
        raise ValueError(f"No columns selected for variant {variant}")
    out = frame[KEY_COLUMNS + cols].copy()
    path = output_dir / f"domain_digital_boundary_{variant}_v1.parquet"
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
        f"# Digital Boundary {variant} Variant",
        "",
        "## Purpose",
        "",
        "Pruned digital-boundary representation to test whether narrower phone/sleep timing axes are more label-readable than the full 405-feature family.",
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
    (output_dir / "domain_digital_boundary_pruned_variants_v1.report.json").write_text(
        json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md_rows = pd.DataFrame(reports)[["variant", "output", "feature_count", "rows"]]
    (output_dir / "domain_digital_boundary_pruned_variants_v1.report.md").write_text(
        "\n".join(
            [
                "# Digital Boundary Pruned Variants",
                "",
                "## Purpose",
                "",
                "Split the broad smartphone sleep-boundary feature family into compact probeable subfamilies.",
                "",
                dataframe_to_markdown(md_rows),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact pruned digital-boundary latent variants.")
    parser.add_argument("--input", default="artifacts/domain_digital_boundary_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
