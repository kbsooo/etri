from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANT_RULES = {
    "core_load": [
        "_mean",
        "_abs_mean",
        "_pos_mean",
        "_neg_mean",
        "_std",
        "_range",
    ],
    "prototype": [
        "proto",
    ],
    "pair_conflict": [
        "pair_",
    ],
    "sleep_boundary_gate": [
        "s1_wake_recovery",
        "s2_sleep_consensus",
        "s3_onset_settle",
        "opportunity",
    ],
    "q_state_gate": [
        "q1_boundary",
        "q2_sleep_rolling",
        "q3_mobility",
        "q3_recovery",
        "energy_recovery",
        "opportunity",
    ],
    "s2_focus_gate": [
        "s2_sleep_consensus",
        "s3_onset_settle",
        "s1_wake_recovery",
        "pair_s2_sleep_consensus",
        "__s2_sleep_consensus",
    ],
    "relative_only": [
        "_subdev",
        "_subrz",
    ],
}


def selected_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_RULES[variant]
    cols = []
    for col in frame.columns:
        if not col.startswith("z_psg_"):
            continue
        if any(pattern in col for pattern in patterns):
            cols.append(col)
    return sorted(set(cols))


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


def write_variant(frame: pd.DataFrame, best: pd.DataFrame, variant: str, output_dir: Path) -> dict[str, object]:
    cols = selected_columns(frame, variant)
    if not cols:
        raise ValueError(f"No selected columns for {variant}")
    out = frame[KEY_COLUMNS + cols].copy()
    path = output_dir / f"domain_protected_state_gate_{variant}_v1.parquet"
    out.to_parquet(path, index=False)
    best_cols = [col for col in best.columns if col.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(out, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_path = output_dir / f"domain_best_plus_protected_state_gate_{variant}_v1.parquet"
    additive.to_parquet(additive_path, index=False)
    report = {
        "variant": variant,
        "output": str(path),
        "additive_output": str(additive_path),
        "rows": int(len(out)),
        "feature_count": int(len(cols)),
        "patterns": VARIANT_RULES[variant],
    }
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    stats = pd.DataFrame(
        {
            "feature": cols,
            "mean": [float(out[col].mean(skipna=True)) for col in cols],
            "std": [float(out[col].std(skipna=True)) for col in cols],
        }
    )
    path.with_suffix(".report.md").write_text(
        "\n".join(
            [
                f"# Protected State Gate Variant: {variant}",
                "",
                f"- Output: `{path}`",
                f"- Additive output: `{additive_path}`",
                f"- Rows: `{len(out)}`",
                f"- Feature count: `{len(cols)}`",
                "",
                "## Pattern Rules",
                "",
                ", ".join(f"`{p}`" for p in VARIANT_RULES[variant]),
                "",
                "## Feature Summary",
                "",
                dataframe_to_markdown(stats.head(80)),
            ]
        ),
        encoding="utf-8",
    )
    return report


def run(args: argparse.Namespace) -> None:
    frame = pd.read_parquet(args.input).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    best = pd.read_parquet(args.best).copy()
    best["subject_id"] = best["subject_id"].astype(str)
    best["lifelog_date"] = pd.to_datetime(best["lifelog_date"]).dt.strftime("%Y-%m-%d")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = [write_variant(frame, best, variant, output_dir) for variant in VARIANT_RULES]
    report_path = output_dir / "domain_protected_state_gate_pruned_variants_v1.report.json"
    report_path.write_text(json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.with_suffix(".md").write_text(
        "\n".join(
            [
                "# Protected State Gate Pruned Variants",
                "",
                "Split the broad protected-state gate latent into smaller gate families.",
                "",
                dataframe_to_markdown(pd.DataFrame(reports)[["variant", "output", "additive_output", "feature_count", "rows"]]),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build pruned variants of protected-state gate latents.")
    parser.add_argument("--input", default="artifacts/domain_protected_state_gate_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
