from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANT_RULES = {
    "q1_boundary_only": ["q1_boundary"],
    "q2_sleep_rolling_only": ["q2_sleep_rolling"],
    "q3_mobility_only": ["q3_mobility"],
    "q3_recovery_only": ["q3_recovery"],
    "opportunity_only": ["opportunity"],
    "energy_recovery_only": ["energy_recovery"],
    "sleep_opportunity_energy": ["q2_sleep_rolling", "opportunity", "energy_recovery"],
    "mobility_recovery_energy": ["q3_mobility", "q3_recovery", "energy_recovery"],
    "opportunity_mobility": ["opportunity", "q3_mobility", "q3_recovery"],
    "q_block_core": [
        "q1_boundary_mean",
        "q1_boundary_abs_mean",
        "q1_boundary_pca",
        "q2_sleep_rolling_mean",
        "q2_sleep_rolling_abs_mean",
        "q2_sleep_rolling_pca",
        "q3_mobility_mean",
        "q3_mobility_abs_mean",
        "q3_mobility_pca",
        "q3_recovery_mean",
        "q3_recovery_abs_mean",
        "q3_recovery_pca",
        "opportunity_mean",
        "opportunity_abs_mean",
        "opportunity_pca",
        "energy_recovery_mean",
        "energy_recovery_abs_mean",
        "energy_recovery_pca",
    ],
    "sleep_q_pairs": [
        "pair_q2_sleep_rolling__q3_mobility",
        "pair_q2_sleep_rolling__q3_recovery",
        "pair_q2_sleep_rolling__opportunity",
        "pair_q2_sleep_rolling__energy_recovery",
    ],
    "opportunity_pairs": [
        "pair_q1_boundary__opportunity",
        "pair_q2_sleep_rolling__opportunity",
        "pair_q3_mobility__opportunity",
        "pair_q3_recovery__opportunity",
        "pair_opportunity__energy_recovery",
    ],
    "recovery_pairs": [
        "pair_q3_mobility__q3_recovery",
        "pair_q3_mobility__energy_recovery",
        "pair_q3_recovery__energy_recovery",
        "pair_opportunity__energy_recovery",
    ],
    "relative_q_state": ["q1_boundary", "q2_sleep_rolling", "q3_mobility", "q3_recovery", "opportunity", "energy_recovery", "_subdev", "_subrz"],
}


def selected_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = VARIANT_RULES[variant]
    cols = []
    for col in frame.columns:
        if not col.startswith("z_psg_"):
            continue
        if variant == "relative_q_state":
            if any(axis in col for axis in patterns[:-2]) and (col.endswith("_subdev") or col.endswith("_subrz")):
                cols.append(col)
        elif variant.endswith("_pairs"):
            if any(pattern in col for pattern in patterns):
                cols.append(col)
        else:
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
    path = output_dir / f"domain_psg_q_state_s2_{variant}_v1.parquet"
    out.to_parquet(path, index=False)
    best_cols = [col for col in best.columns if col.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(out, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_path = output_dir / f"domain_best_plus_psg_q_state_s2_{variant}_v1.parquet"
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
                f"# PSG Q-State S2 Variant: {variant}",
                "",
                "## Purpose",
                "",
                "Split the S2-positive Q-state gate into smaller causal/state components.",
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
    report_path = output_dir / "domain_psg_q_state_s2_variants_v1.report.json"
    report_path.write_text(json.dumps({"input": args.input, "variants": reports}, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.with_suffix(".md").write_text(
        "\n".join(
            [
                "# PSG Q-State S2 Variants",
                "",
                "Split the broad S2-positive Q-state gate into smaller probeable state families.",
                "",
                dataframe_to_markdown(pd.DataFrame(reports)[["variant", "output", "additive_output", "feature_count", "rows"]]),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build S2-focused PSG Q-state variants.")
    parser.add_argument("--input", default="artifacts/domain_protected_state_gate_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
