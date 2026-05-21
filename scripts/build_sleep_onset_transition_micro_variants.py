from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

MICRO_VARIANTS = {
    "charging_timing": [
        "last_charging_latency",
        "charging_recency",
        "charging_rise",
    ],
    "charging_windows": [
        "_charging_ratio",
        "_charging_starts",
    ],
    "settled_no_phone": [
        "_settled_ratio",
        "settled_recency",
        "settled_run_start",
        "quiet_settled",
    ],
    "settled_charging": [
        "_settled_charging_ratio",
        "quiet_settled",
        "readiness",
    ],
    "phone_charging_conflict": [
        "conflict_phone_charging",
        "last_hour_conflict",
        "disruption",
    ],
    "readiness_rolling": [
        "onset_readiness_score",
        "readiness_score_past",
    ],
    "pre30m_settle": [
        "pre30m_charging",
        "pre30m_settled",
        "pre30m_conflict",
        "pre30m_phone",
        "pre30m_moving",
        "pre30m_bright",
        "pre30m_dark",
    ],
    "pre1h_settle": [
        "pre1h_charging",
        "pre1h_settled",
        "pre1h_conflict",
        "pre1h_phone",
        "pre1h_moving",
        "pre1h_bright",
        "pre1h_dark",
    ],
    "base_values_only": [
        "__BASE_VALUES_ONLY__",
    ],
    "subject_relative_only": [
        "_subdev",
        "_subrz",
        "_subpct",
    ],
    "rolling_context_only": [
        "_past3_",
        "_past7_",
        "_past14_",
        "_past28_",
    ],
    "s3_core_timing_settle_conflict": [
        "last_charging_latency",
        "charging_recency",
        "charging_rise",
        "settled_recency",
        "settled_run_start",
        "_settled_charging_ratio",
        "_settled_ratio",
        "conflict_phone_charging",
        "last_hour_conflict",
        "disruption",
        "readiness",
    ],
    "s3_final_hour_core": [
        "pre30m_charging",
        "pre30m_settled",
        "pre30m_conflict",
        "pre1h_charging",
        "pre1h_settled",
        "pre1h_conflict",
        "last_charging_latency",
        "charging_recency",
        "readiness",
        "disruption",
    ],
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
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def select_columns(columns: list[str], patterns: list[str]) -> list[str]:
    if "__BASE_VALUES_ONLY__" in patterns:
        derived = ("_subdev", "_subrz", "_subpct", "_past3_", "_past7_", "_past14_", "_past28_")
        return sorted([col for col in columns if col.startswith("z_sot_") and not any(token in col for token in derived)])
    return sorted([col for col in columns if col.startswith("z_sot_") and any(pattern in col for pattern in patterns)])


def write_frame(path: Path, frame: pd.DataFrame, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    z_cols = [c for c in frame.columns if c.startswith("z_")]
    stats = pd.DataFrame(
        {
            "feature": z_cols,
            "mean": [float(frame[c].mean(skipna=True)) for c in z_cols],
            "std": [float(frame[c].std(skipna=True)) for c in z_cols],
        }
    )
    md = [
        f"# {report['name']}",
        "",
        f"- Output: `{path}`",
        f"- Rows: `{len(frame)}`",
        f"- Feature count: `{len(z_cols)}`",
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(stats.head(80)),
    ]
    path.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    source = normalize_keys(pd.read_parquet(args.input))
    best = normalize_keys(pd.read_parquet(args.best))
    best_cols = [c for c in best.columns if c.startswith("z_")]
    output_dir = Path(args.output_dir)
    reports = []
    for name, patterns in MICRO_VARIANTS.items():
        cols = select_columns(source.columns.tolist(), patterns)
        if not cols:
            raise ValueError(f"No columns selected for {name}")
        raw = source[KEY_COLUMNS + cols].copy()
        raw_path = output_dir / f"domain_sleep_onset_transition_micro_{name}_v1.parquet"
        raw_report = {
            "name": f"Sleep Onset Transition Micro Variant: {name}",
            "variant": name,
            "kind": "raw",
            "patterns": patterns,
            "output": str(raw_path),
            "rows": int(len(raw)),
            "feature_count": int(len(cols)),
        }
        write_frame(raw_path, raw, raw_report)

        additive = best[KEY_COLUMNS + best_cols].merge(raw, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        additive_path = output_dir / f"domain_best_plus_sleep_onset_transition_micro_{name}_v1.parquet"
        additive_report = {
            "name": f"Best Plus Sleep Onset Transition Micro Variant: {name}",
            "variant": name,
            "kind": "best_plus",
            "patterns": patterns,
            "output": str(additive_path),
            "rows": int(len(additive)),
            "best_feature_count": int(len(best_cols)),
            "extra_feature_count": int(len(cols)),
            "feature_count": int(len(best_cols) + len(cols)),
        }
        write_frame(additive_path, additive, additive_report)
        reports.extend([raw_report, additive_report])

    report_path = output_dir / "domain_sleep_onset_transition_micro_variants_v1.report.json"
    report_path.write_text(json.dumps({"input": args.input, "best": args.best, "variants": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = pd.DataFrame(reports)
    report_path.with_suffix(".md").write_text(
        "# Sleep Onset Transition Micro Variants\n\n"
        + dataframe_to_markdown(rows[["variant", "kind", "output", "feature_count", "rows"]]),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split the S3-positive charging-settle feature family into narrower micro variants.")
    parser.add_argument("--input", default="artifacts/domain_sleep_onset_transition_charging_settle_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
