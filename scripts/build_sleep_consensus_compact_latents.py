from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]
WINDOWS = ["prebed90m", "sleep_full", "sleep_first", "sleep_mid", "sleep_final", "postwake90m"]
METRICS = [
    "purity_score",
    "micro_awake_score",
    "sleep_consensus_ratio",
    "missing_sleep_like_ratio",
    "device_off_conflict_ratio",
    "quiet_break_ratio",
    "coverage_present_ratio",
    "sensor_disagreement_ratio",
]
GLOBAL_METRICS = [
    "z_scp_purity_final_minus_first",
    "z_scp_purity_midpoint_u_shape",
    "z_scp_micro_awake_final_minus_first",
    "z_scp_consensus_duration_share",
    "z_scp_sleep_eff_x_purity",
    "z_scp_awakenings_x_micro_awake",
    "z_scp_sol_x_prebed_conflict",
]
ROLL_SUFFIXES = ["past7_delta", "past14_delta"]
SUBJECT_SUFFIXES = ["subdev", "subrz", "subpct"]


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def compact_columns(columns: list[str], mode: str) -> list[str]:
    wanted = []
    base_names = [f"z_scp_{window}_{metric}" for window in WINDOWS for metric in METRICS] + GLOBAL_METRICS
    for name in base_names:
        if mode in {"core", "all"} and name in columns:
            wanted.append(name)
        if mode in {"subject_relative", "all"}:
            wanted.extend([f"{name}_{suffix}" for suffix in SUBJECT_SUFFIXES if f"{name}_{suffix}" in columns])
        if mode in {"rolling", "all"}:
            wanted.extend([f"{name}_{suffix}" for suffix in ROLL_SUFFIXES if f"{name}_{suffix}" in columns])
    return sorted(set(wanted))


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
    for mode in ["core", "subject_relative", "rolling", "all"]:
        cols = compact_columns(source.columns.tolist(), mode)
        if not cols:
            raise ValueError(f"No compact columns selected for {mode}")
        raw = source[KEY_COLUMNS + cols].copy()
        raw_path = output_dir / f"domain_sleep_consensus_compact_{mode}_v1.parquet"
        raw_report = {
            "name": f"Sleep Consensus Compact: {mode}",
            "mode": mode,
            "kind": "raw",
            "output": str(raw_path),
            "rows": int(len(raw)),
            "feature_count": int(len(cols)),
        }
        write_frame(raw_path, raw, raw_report)

        additive = best[KEY_COLUMNS + best_cols].merge(raw, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        additive_path = output_dir / f"domain_best_plus_sleep_consensus_compact_{mode}_v1.parquet"
        additive_report = {
            "name": f"Best Plus Sleep Consensus Compact: {mode}",
            "mode": mode,
            "kind": "best_plus",
            "output": str(additive_path),
            "rows": int(len(additive)),
            "best_feature_count": int(len(best_cols)),
            "extra_feature_count": int(len(cols)),
            "feature_count": int(len(best_cols) + len(cols)),
        }
        write_frame(additive_path, additive, additive_report)
        reports.extend([raw_report, additive_report])

    report_path = output_dir / "domain_sleep_consensus_compact_v1.report.json"
    report_path.write_text(json.dumps({"input": args.input, "best": args.best, "reports": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.with_suffix(".md").write_text(
        "# Sleep Consensus Compact Latents\n\n"
        + dataframe_to_markdown(pd.DataFrame(reports)[["mode", "kind", "output", "feature_count", "rows"]]),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build compact sleep-consensus latent slices from high-dimensional SCP features.")
    parser.add_argument("--input", default="artifacts/domain_sleep_consensus_purity_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
