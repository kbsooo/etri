from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
VARIANTS = {
    "sleep_off_stability": [
        r"sleep_.*off_stability",
        r"sleep_.*intentional_off_like",
        r"sleep_.*device_off_ratio",
        r"sleep_.*device_off_longest_run",
    ],
    "sleep_off_fragment": [
        r"sleep_.*off_fragment",
        r"sleep_.*device_off_starts",
        r"sleep_.*device_off_transitions",
        r"sleep_.*coverage_state_transitions",
        r"sleep_.*coverage_state_entropy",
    ],
    "conflict_off": [
        r"conflict_off",
        r"phone_only_present",
        r"charging_device_off",
    ],
    "boundary_recoverage": [
        r"prebed_to_sleep",
        r"postwake_recoverage",
        r"wake_minus_onset",
        r"onset1h_.*coverage",
        r"wake1h_.*coverage",
        r"postwake2h_.*coverage",
    ],
    "no_wear_episode": [
        r"no_wear",
        r"ev_no_wear",
    ],
    "body_sensor_missing": [
        r"body_missing",
        r"ev_present_hr_missing",
        r"ev_present_pedo_missing",
        r"present_count",
    ],
    "subject_relative_only": [
        r"subdev",
        r"subrz",
        r"subpct",
    ],
    "rolling_context": [
        r"past(3|7|14|28)",
    ],
}


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def select_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = [re.compile(pattern) for pattern in VARIANTS[variant]]
    return sorted(
        col
        for col in frame.columns
        if col.startswith("z_sbc_") and any(pattern.search(col) for pattern in patterns)
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


def write_artifact(path: Path, frame: pd.DataFrame, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    cols = [col for col in frame.columns if col.startswith("z_")]
    stats = pd.DataFrame(
        {
            "feature": cols,
            "mean": [float(frame[col].mean(skipna=True)) for col in cols],
            "std": [float(frame[col].std(skipna=True)) for col in cols],
        }
    )
    md = [
        f"# {report['name']}",
        "",
        "## Purpose",
        "",
        "Compact slice of the sleep-boundary coverage/no-wear objective.",
        "",
        f"- Output: `{path}`",
        f"- Rows: `{len(frame)}`",
        f"- Feature count: `{len(cols)}`",
        "",
        "## Patterns",
        "",
        ", ".join(f"`{p}`" for p in report["patterns"]),
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(stats.head(50)),
    ]
    path.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    source = normalize(pd.read_parquet(args.input))
    best = normalize(pd.read_parquet(args.best))
    best_cols = [col for col in best.columns if col.startswith("z_")]
    if not best_cols:
        raise ValueError(f"No z_* columns in {args.best}")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    for variant in VARIANTS:
        cols = select_columns(source, variant)
        if not cols:
            raise ValueError(f"No selected columns for {variant}")
        raw = source[KEY_COLUMNS + cols].copy()
        raw_path = output_dir / f"domain_sleep_boundary_coverage_{variant}_v1.parquet"
        raw_report = {
            "name": f"Sleep Boundary Coverage Variant: {variant}",
            "variant": variant,
            "kind": "raw",
            "output": str(raw_path),
            "rows": int(len(raw)),
            "feature_count": int(len(cols)),
            "patterns": VARIANTS[variant],
        }
        write_artifact(raw_path, raw, raw_report)
        additive = best[KEY_COLUMNS + best_cols].merge(raw, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        additive_path = output_dir / f"domain_best_plus_sleep_boundary_coverage_{variant}_v1.parquet"
        additive_report = {
            "name": f"Best Plus Sleep Boundary Coverage Variant: {variant}",
            "variant": variant,
            "kind": "best_plus",
            "output": str(additive_path),
            "rows": int(len(additive)),
            "feature_count": int(len(additive.columns) - len(KEY_COLUMNS)),
            "sbc_feature_count": int(len(cols)),
            "best_feature_count": int(len(best_cols)),
            "patterns": VARIANTS[variant],
        }
        write_artifact(additive_path, additive, additive_report)
        reports.extend([raw_report, additive_report])

    report = {"input": args.input, "best": args.best, "variants": reports}
    report_path = output_dir / "domain_sleep_boundary_coverage_pruned_variants_v1.report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    table = pd.DataFrame(reports)[["variant", "kind", "output", "feature_count", "rows"]]
    report_path.with_suffix(".md").write_text(
        "\n".join(
            [
                "# Sleep Boundary Coverage Pruned Variants",
                "",
                "Split the broad sleep-boundary coverage objective into compact probeable subfamilies.",
                "",
                dataframe_to_markdown(table),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split sleep-boundary coverage latents into pruned variants.")
    parser.add_argument("--input", default="artifacts/domain_sleep_boundary_coverage_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
