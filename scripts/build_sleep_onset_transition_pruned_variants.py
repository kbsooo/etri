from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANT_PATTERNS = {
    "last_event_latency": [
        "last_",
        "latency",
        "recency",
    ],
    "shutdown_slope": [
        "shutdown",
        "rise",
        "decay",
        "cleanliness",
    ],
    "prebed_fragmentation": [
        "starts",
        "toggles",
        "longest",
        "fragmentation",
        "conflict",
    ],
    "light_environment_transition": [
        "bright",
        "dark",
        "light",
        "silence",
        "speech",
        "music",
        "vehicle",
    ],
    "charging_settle": [
        "charging",
        "settled",
        "quiet_settled",
        "readiness",
    ],
    "onset_consensus": [
        "readiness",
        "cleanliness",
        "disruption",
        "settled",
        "conflict",
        "last_hour",
    ],
}


def select_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_PATTERNS[variant]
    selected = []
    for col in frame.columns:
        if not col.startswith("z_sot_"):
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
    path = output_dir / f"domain_sleep_onset_transition_{variant}_v1.parquet"
    out.to_parquet(path, index=False)
    report = {
        "variant": variant,
        "output": str(path),
        "rows": int(len(out)),
        "feature_count": int(len(cols)),
        "patterns": VARIANT_PATTERNS[variant],
    }
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    stats = pd.DataFrame(
        {
            "feature": cols,
            "mean": [float(out[c].mean(skipna=True)) for c in cols],
            "std": [float(out[c].std(skipna=True)) for c in cols],
        }
    )
    md = [
        f"# Sleep Onset Transition Variant: {variant}",
        "",
        "## Purpose",
        "",
        "Compact probeable slice of sleep-onset transition features, separated so harmful axes can be dropped instead of averaged into the latent.",
        "",
        f"- Output: `{path}`",
        f"- Rows: `{len(out)}`",
        f"- Feature count: `{len(cols)}`",
        "",
        "## Pattern Rules",
        "",
        ", ".join(f"`{p}`" for p in VARIANT_PATTERNS[variant]),
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(stats.head(60)),
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
    report_path = output_dir / "domain_sleep_onset_transition_pruned_variants_v1.report.json"
    report_path.write_text(json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Sleep Onset Transition Pruned Variants",
        "",
        "Split transition features into latency, shutdown, fragmentation, environment, settling, and consensus families.",
        "",
        dataframe_to_markdown(pd.DataFrame(reports)[["variant", "output", "feature_count", "rows"]]),
    ]
    report_path.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact pruned sleep-onset transition variants.")
    parser.add_argument("--input", default="artifacts/domain_sleep_onset_transition_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
