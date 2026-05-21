from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANTS = {
    "sleep_micro_core": [
        r"sleep_(full|first|mid|final)_micro_awake_score",
        r"sleep_(full|first|mid|final)_quiet_break_(ratio|starts|transitions)",
        r"sleep_(full|first|mid|final)_intrusion_(ratio|starts|transitions)",
        r"micro_awake_final_minus_first",
    ],
    "sleep_micro_runs": [
        r"sleep_(full|first|mid|final)_quiet_break_longest_run",
        r"sleep_(full|first|mid|final)_intrusion_longest_run",
        r"sleep_(full|first|mid|final)_phone_dark_still_conflict_longest_run",
        r"sleep_(full|first|mid|final)_motion_dark_conflict_longest_run",
        r"consensus_duration_share",
    ],
    "phone_motion_conflict": [
        r"sleep_(full|first|mid|final)_phone_dark_still_conflict",
        r"sleep_(full|first|mid|final)_motion_dark_conflict",
        r"sleep_(full|first|mid|final)_bright_still_conflict",
    ],
    "phase_delta": [
        r"micro_awake_final_minus_first",
        r"sleep_final_.*(micro_awake|quiet_break|intrusion|phone_dark|motion_dark|bright_still)",
        r"sleep_first_.*(micro_awake|quiet_break|intrusion|phone_dark|motion_dark|bright_still)",
    ],
    "awakenings_interaction": [
        r"awakenings_x_micro_awake",
        r"n_awakenings",
    ],
    "subject_relative_sleep_micro": [
        r"sleep_(full|first|mid|final).*(micro_awake|quiet_break|intrusion|phone_dark|motion_dark|bright_still).*(subdev|subrz|subpct)",
        r"micro_awake_final_minus_first_(subdev|subrz|subpct)",
        r"awakenings_x_micro_awake_(subdev|subrz|subpct)",
    ],
    "rolling_sleep_micro": [
        r"sleep_(full|first|mid|final).*(micro_awake|quiet_break|intrusion|phone_dark|motion_dark|bright_still).*past(3|7|14|28)",
        r"micro_awake_final_minus_first_past(3|7|14|28)",
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
        if col.startswith("z_scp_") and any(pattern.search(col) for pattern in patterns)
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
    cols = [c for c in frame.columns if c.startswith("z_")]
    stats = pd.DataFrame(
        {
            "feature": cols,
            "mean": [float(frame[c].mean(skipna=True)) for c in cols],
            "std": [float(frame[c].std(skipna=True)) for c in cols],
        }
    )
    md = [
        f"# {report['name']}",
        "",
        "## Purpose",
        "",
        "Compact S2 micro-awakening slice from sleep-consensus purity features.",
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
        dataframe_to_markdown(stats.head(60)),
    ]
    path.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    source = normalize(pd.read_parquet(args.input))
    best = normalize(pd.read_parquet(args.best))
    best_cols = [c for c in best.columns if c.startswith("z_")]
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
        raw_path = output_dir / f"domain_s2_micro_awake_{variant}_v1.parquet"
        raw_report = {
            "name": f"S2 Micro Awake Variant: {variant}",
            "variant": variant,
            "kind": "raw",
            "output": str(raw_path),
            "rows": int(len(raw)),
            "feature_count": int(len(cols)),
            "patterns": VARIANTS[variant],
        }
        write_artifact(raw_path, raw, raw_report)

        additive = best[KEY_COLUMNS + best_cols].merge(raw, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        additive_path = output_dir / f"domain_best_plus_s2_micro_awake_{variant}_v1.parquet"
        additive_report = {
            "name": f"Best Plus S2 Micro Awake Variant: {variant}",
            "variant": variant,
            "kind": "best_plus",
            "output": str(additive_path),
            "rows": int(len(additive)),
            "feature_count": int(len(additive.columns) - len(KEY_COLUMNS)),
            "micro_feature_count": int(len(cols)),
            "best_feature_count": int(len(best_cols)),
            "patterns": VARIANTS[variant],
        }
        write_artifact(additive_path, additive, additive_report)
        reports.extend([raw_report, additive_report])

    report = {"input": args.input, "best": args.best, "variants": reports}
    report_path = output_dir / "domain_s2_micro_awake_variants_v1.report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    table = pd.DataFrame(reports)[["variant", "kind", "output", "feature_count", "rows"]]
    report_path.with_suffix(".md").write_text(
        "\n".join(
            [
                "# S2 Micro Awake Variants",
                "",
                "Split broad sleep-consensus micro-awakening features into compact sleep-window-only objectives.",
                "",
                dataframe_to_markdown(table),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact S2 micro-awakening variants.")
    parser.add_argument("--input", default="artifacts/domain_sleep_consensus_purity_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
