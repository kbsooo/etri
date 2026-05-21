from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANT_PATTERNS = {
    "awakening": [
        "awaken",
        "longest_block",
        "sleep_eff",
        "sol_",
    ],
    "sleep_sensor": [
        "sleep_ev_",
        "sleep_hr_",
        "sleep_screen",
        "sleep_usage",
        "sleep_mlight",
        "sleep_wlight",
        "sleep_sensor",
        "sleep_late_minus",
    ],
    "postwake_recovery": [
        "postwake",
        "day_recovery",
        "wake_activity",
        "wake_phone",
    ],
    "sleep_digital": [
        "sleep_screen",
        "sleep_usage",
        "sleep_ev_phone_active",
        "wake_phone",
    ],
    "postwake_digital": [
        "postwake1h_ev_phone_active",
        "postwake1h_phone_still",
        "postwake1h_screen",
        "postwake1h_usage",
        "postwake3h_ev_phone_active",
        "postwake3h_phone_still",
        "postwake3h_screen",
        "postwake3h_usage",
        "day_recovery_ev_phone_active",
        "day_recovery_phone_still",
        "day_recovery_screen",
        "day_recovery_usage",
    ],
    "sleep_wake_digital": [
        "sleep_screen",
        "sleep_usage",
        "sleep_ev_phone_active",
        "wake_phone",
        "postwake1h_ev_phone_active",
        "postwake1h_phone_still",
        "postwake1h_screen",
        "postwake1h_usage",
        "postwake3h_ev_phone_active",
        "postwake3h_phone_still",
        "postwake3h_screen",
        "postwake3h_usage",
        "day_recovery_ev_phone_active",
        "day_recovery_phone_still",
        "day_recovery_screen",
        "day_recovery_usage",
    ],
    "fragment_core": [
        "awaken_density",
        "awaken_late_load",
        "awaken_cluster",
        "sleep_sensor_fragment_score",
        "sleep_arousal_transition",
        "sleep_late_minus",
        "longest_block_share",
    ],
}


def selected_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_PATTERNS[variant]
    cols = []
    for col in frame.columns:
        if not col.startswith("z_sfr_"):
            continue
        if any(pattern in col for pattern in patterns):
            cols.append(col)
    return sorted(cols)


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
    path = output_dir / f"domain_sleep_fragment_recovery_{variant}_v1.parquet"
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
        f"# Sleep Fragment Recovery {variant} Variant",
        "",
        "## Purpose",
        "",
        "Compact S-family probe view split from the broad sleep-fragment/recovery latent family.",
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
    (output_dir / "domain_sleep_fragment_recovery_pruned_variants_v1.report.json").write_text(
        json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "domain_sleep_fragment_recovery_pruned_variants_v1.report.md").write_text(
        "\n".join(
            [
                "# Sleep Fragment Recovery Pruned Variants",
                "",
                "## Purpose",
                "",
                "Split broad sleep fragmentation/recovery features into compact probeable subfamilies.",
                "",
                dataframe_to_markdown(pd.DataFrame(reports)[["variant", "output", "feature_count", "rows"]]),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact sleep-fragment/recovery latent variants.")
    parser.add_argument("--input", default="artifacts/domain_sleep_fragment_recovery_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
