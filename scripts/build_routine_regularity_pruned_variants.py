from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]

VARIANTS = {
    "profile_distance": [
        r"profile_.*subject",
        r"weekday_gap",
        r"best_shift",
    ],
    "phase_shift": [
        r"phase_.*shift",
        r"active_(start|end)_hour.*shift",
        r"sleep_(onset|midpoint)_hour.*shift",
        r"wake_hour.*shift",
    ],
    "sleep_regular_break": [
        r"sleep_(onset|midpoint)_hour",
        r"wake_hour",
        r"tst_min",
        r"sleep_eff",
        r"n_awakenings",
        r"longest_block",
        r"sol_proxy",
    ],
    "routine_state": [
        r"routine_transition",
        r"routine_state_entropy",
    ],
    "short_rolling_volatility": [
        r"past(3|7)_(delta|abs_delta|volatility)",
    ],
    "long_rolling_volatility": [
        r"past(14|28)_(delta|abs_delta|volatility)",
    ],
    "phone_rhythm": [
        r"phone_",
    ],
    "mobility_body_rhythm": [
        r"mobility_",
        r"body_",
    ],
    "coverage_rhythm": [
        r"coverage_",
    ],
    "night_evening_balance": [
        r"night_ratio",
        r"evening_ratio",
    ],
}


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def select_columns(frame: pd.DataFrame, variant: str) -> list[str]:
    patterns = [re.compile(pattern) for pattern in VARIANTS[variant]]
    selected = []
    for col in frame.columns:
        if not col.startswith("z_rr_"):
            continue
        if any(pattern.search(col) for pattern in patterns):
            selected.append(col)
    return sorted(selected)


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        values = []
        for col in cols:
            value = row[col]
            values.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_frame(path: Path, frame: pd.DataFrame, report: dict[str, object], purpose: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    path.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    z_cols = [col for col in frame.columns if col.startswith("z_")]
    stats = pd.DataFrame(
        {
            "feature": z_cols,
            "mean": [float(frame[col].mean(skipna=True)) for col in z_cols],
            "std": [float(frame[col].std(skipna=True)) for col in z_cols],
        }
    )
    md = [
        f"# {report['name']}",
        "",
        "## Purpose",
        "",
        purpose,
        "",
        f"- Output: `{path}`",
        f"- Rows: `{len(frame)}`",
        f"- Feature count: `{len(z_cols)}`",
        "",
        "## Pattern Rules",
        "",
        ", ".join(f"`{pattern}`" for pattern in report["patterns"]),
        "",
        "## Feature Summary",
        "",
        dataframe_to_markdown(stats.head(50)),
    ]
    path.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def best_columns(best: pd.DataFrame) -> list[str]:
    return [col for col in best.columns if col.startswith("z_")]


def run(args: argparse.Namespace) -> None:
    source = normalize_keys(pd.read_parquet(args.input))
    best = normalize_keys(pd.read_parquet(args.best))
    best_z_cols = best_columns(best)
    if source[KEY_COLUMNS].duplicated().any():
        raise ValueError(f"Duplicate keys in {args.input}")
    if best[KEY_COLUMNS].duplicated().any():
        raise ValueError(f"Duplicate keys in {args.best}")
    if not best_z_cols:
        raise ValueError(f"No z_* columns in {args.best}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    purpose = (
        "Split the broad routine-regularity latent into compact, domain-readable S4/S2 hypotheses. "
        "This tests pruning rather than adding broader interaction products; labels are not used."
    )

    for variant in VARIANTS:
        selected = select_columns(source, variant)
        if not selected:
            raise ValueError(f"No columns selected for {variant}")
        raw = source[KEY_COLUMNS + selected].copy()
        raw_path = output_dir / f"domain_routine_regularity_{variant}_v1.parquet"
        raw_report = {
            "name": f"Routine Regularity Variant: {variant}",
            "variant": variant,
            "kind": "raw",
            "output": str(raw_path),
            "rows": int(len(raw)),
            "feature_count": int(len(selected)),
            "patterns": VARIANTS[variant],
            "input": args.input,
        }
        write_frame(raw_path, raw, raw_report, purpose)

        additive = best[KEY_COLUMNS + best_z_cols].merge(raw, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        additive_path = output_dir / f"domain_best_plus_routine_regularity_{variant}_v1.parquet"
        additive_report = {
            "name": f"Best Plus Routine Regularity Variant: {variant}",
            "variant": variant,
            "kind": "best_plus",
            "output": str(additive_path),
            "rows": int(len(additive)),
            "feature_count": int(len(additive.columns) - len(KEY_COLUMNS)),
            "routine_feature_count": int(len(selected)),
            "best_feature_count": int(len(best_z_cols)),
            "patterns": VARIANTS[variant],
            "input": args.input,
            "best": args.best,
        }
        write_frame(additive_path, additive, additive_report, purpose)
        summaries.extend([raw_report, additive_report])

    report = {"input": args.input, "best": args.best, "variants": summaries}
    report_path = output_dir / "domain_routine_regularity_pruned_variants_v1.report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    table = pd.DataFrame(summaries)[["variant", "kind", "output", "feature_count", "rows"]]
    report_path.with_suffix(".md").write_text(
        "\n".join(
            [
                "# Routine Regularity Pruned Variants",
                "",
                "## Purpose",
                "",
                purpose,
                "",
                dataframe_to_markdown(table),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split routine-regularity latents into compact hypothesis variants.")
    parser.add_argument("--input", default="artifacts/domain_routine_regularity_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output-dir", default="artifacts")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
