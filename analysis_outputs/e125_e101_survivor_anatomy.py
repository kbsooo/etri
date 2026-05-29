#!/usr/bin/env python3
"""E125 anatomy of E101-plausible E124 worlds.

SAUNA question:
E124 showed that the E99 local+tail abstraction explains E72/E95 but mostly
fails E101. Before leaving the line, inspect the small set of E101-plausible
worlds. If they are genuinely Q2/S3 diffuse-tail worlds, the old E100/E101
story may still have a targeted continuation. If not, the missing variable is
not another Q2/S3 same-line selector.

This script does not generate submissions. It is a post-E124 falsification of
the residual worldview.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

SCENARIOS_IN = OUT / "e124_e101_conditioned_tail_transfer_scenarios.csv"
CATEGORY_OUT = OUT / "e125_e101_survivor_anatomy_category_summary.csv"
NUMERIC_OUT = OUT / "e125_e101_survivor_anatomy_numeric_summary.csv"
MASK_OUT = OUT / "e125_e101_survivor_anatomy_mask_summary.csv"
REPORT_OUT = OUT / "e125_e101_survivor_anatomy_report.md"


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def load() -> pd.DataFrame:
    df = pd.read_csv(SCENARIOS_IN)
    df["gamma_group"] = np.where(df["gamma"].isna(), "deterministic", "gamma_" + df["gamma"].map(lambda x: f"{x:g}"))
    tail_diff = df["tail_e101"] - df["tail_e95"]
    df["e101_tail_relation"] = np.select(
        [tail_diff < -1.0e-8, tail_diff > 1.0e-8],
        ["e101_lower_tail_than_e95", "e101_higher_tail_than_e95"],
        default="tail_equal",
    )
    df["alpha_group"] = pd.cut(
        df["alpha"],
        bins=[-np.inf, 0.5, 1.0, 2.0, 4.0, np.inf],
        labels=["alpha_le_0p5", "alpha_0p5_1", "alpha_1_2", "alpha_2_4", "alpha_gt_4"],
    ).astype(str)
    return df


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    broad = df[df["is_broad_plausible"]].copy()
    base_rate = float(broad["e101_sensor_plausible"].mean())
    rows: list[dict[str, object]] = []
    for col in ["family", "mask_name", "gamma_group", "alpha_group", "e101_tail_relation", "winner_future", "winner_live"]:
        tab = (
            broad.groupby(col, dropna=False)
            .agg(
                broad_count=("scenario_id", "size"),
                e101_count=("e101_sensor_plausible", "sum"),
                pred_e101_mean=("pred_e101", "mean"),
                pred_vs_e95_e101_mean=("pred_vs_e95_e101", "mean"),
                e101_residual_mean=("e101_residual", "mean"),
            )
            .reset_index()
            .rename(columns={col: "value"})
        )
        tab.insert(0, "category", col)
        tab["e101_rate"] = tab["e101_count"] / tab["broad_count"]
        tab["enrichment_vs_base"] = tab["e101_rate"] / base_rate
        rows.extend(tab.to_dict("records"))
    out = pd.DataFrame(rows)
    return out.sort_values(["e101_count", "enrichment_vs_base", "broad_count"], ascending=[False, False, False])


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    broad = df[df["is_broad_plausible"]].copy()
    e101 = broad[broad["e101_sensor_plausible"]].copy()
    cols = [
        "alpha",
        "lambda",
        "selected_full_cells",
        "selected_fractional_cells",
        "positive_cells_available",
        "tail_e101",
        "tail_e95",
        "tail_e89",
        "tail_e85",
        "pred_e101",
        "pred_vs_e95_e101",
        "e101_residual",
        "pred_vs_e95_e89",
        "pred_vs_e95_e85",
    ]
    rows = []
    for col in cols:
        broad_mean = float(broad[col].mean())
        broad_median = float(broad[col].median())
        e101_mean = float(e101[col].mean())
        e101_median = float(e101[col].median())
        pooled_std = float(broad[col].std(ddof=0))
        rows.append(
            {
                "metric": col,
                "broad_mean": broad_mean,
                "broad_median": broad_median,
                "e101_mean": e101_mean,
                "e101_median": e101_median,
                "mean_shift": e101_mean - broad_mean,
                "median_shift": e101_median - broad_median,
                "std_shift": (e101_mean - broad_mean) / pooled_std if pooled_std > 0 else np.nan,
            }
        )
    rows.append(
        {
            "metric": "tail_e101_minus_e95",
            "broad_mean": float((broad["tail_e101"] - broad["tail_e95"]).mean()),
            "broad_median": float((broad["tail_e101"] - broad["tail_e95"]).median()),
            "e101_mean": float((e101["tail_e101"] - e101["tail_e95"]).mean()),
            "e101_median": float((e101["tail_e101"] - e101["tail_e95"]).median()),
            "mean_shift": float((e101["tail_e101"] - e101["tail_e95"]).mean() - (broad["tail_e101"] - broad["tail_e95"]).mean()),
            "median_shift": float((e101["tail_e101"] - e101["tail_e95"]).median() - (broad["tail_e101"] - broad["tail_e95"]).median()),
            "std_shift": np.nan,
        }
    )
    return pd.DataFrame(rows)


def mask_summary(df: pd.DataFrame) -> pd.DataFrame:
    broad = df[df["is_broad_plausible"]].copy()
    out = (
        broad.groupby("mask_name", dropna=False)
        .agg(
            broad_count=("scenario_id", "size"),
            e101_count=("e101_sensor_plausible", "sum"),
            order_match_rate=("e101_order_match", "mean"),
            close10_rate=("e101_close_pm10e6", "mean"),
            pred_e101_mean=("pred_e101", "mean"),
            pred_vs_e95_e101_mean=("pred_vs_e95_e101", "mean"),
            e101_residual_mean=("e101_residual", "mean"),
            tail_diff_mean=("tail_e101", "mean"),
            tail_e95_mean=("tail_e95", "mean"),
            alpha_median=("alpha", "median"),
            lambda_median=("lambda", "median"),
            selected_full_median=("selected_full_cells", "median"),
        )
        .reset_index()
    )
    out["tail_e101_minus_e95_mean"] = out["tail_diff_mean"] - out["tail_e95_mean"]
    out["e101_rate"] = out["e101_count"] / out["broad_count"]
    return out.sort_values(["e101_count", "e101_rate", "broad_count"], ascending=[False, False, False])


def write_report(df: pd.DataFrame, category: pd.DataFrame, numeric: pd.DataFrame, masks: pd.DataFrame) -> None:
    broad = df[df["is_broad_plausible"]].copy()
    e101 = broad[broad["e101_sensor_plausible"]].copy()
    n_broad = int(len(broad))
    n_e101 = int(len(e101))
    survival_rate = n_e101 / n_broad
    q2s3 = masks[masks["mask_name"].eq("q2s3")].iloc[0]
    all_or_top = int(e101["mask_name"].isin(["all", "e72_top50_hard"]).sum())
    gamma_low = int((e101["gamma"].isna() | e101["gamma"].isin([0.0])).sum())

    top_categories = category[
        (category["category"].isin(["mask_name", "gamma_group", "alpha_group", "e101_tail_relation"]))
        & (category["e101_count"] > 0)
    ].head(18)
    key_numeric = numeric[numeric["metric"].isin(["alpha", "lambda", "selected_full_cells", "tail_e101", "tail_e95", "tail_e101_minus_e95", "pred_vs_e95_e101"])]
    key_masks = masks[masks["mask_name"].isin(["all", "e72_top50_hard", "q2s3", "s1s2s3", "live_q2s1s2s3", "e95_fallback_cells"])]

    report = f"""# E125 E101 survivor anatomy

## Question

E124 left only `{n_e101}` E101-plausible worlds out of `{n_broad}` broad-plausible
E99 worlds. If the old Q2/S3 diffuse-tail story is still the residual law,
the survivor set should be enriched for the `q2s3` mask. If the survivor set is
instead broad/all-tail and transfer-shrunk, the same-family line is not missing
only a better Q2/S3 selector.

## Key Observations

- E101-plausible survival rate: `{survival_rate:.6f}`.
- `all` or `e72_top50_hard` masks account for `{all_or_top}/{n_e101}` survivors.
- `q2s3` mask has `{int(q2s3['e101_count'])}/{int(q2s3['broad_count'])}` survivors.
- deterministic or `gamma=0` worlds account for `{gamma_low}/{n_e101}` survivors.
- Broad median alpha is `{float(broad['alpha'].median()):.6f}`; E101-plausible median alpha is `{float(e101['alpha'].median()):.6f}`.
- Broad median `tail_e101 - tail_e95` is `{float((broad['tail_e101'] - broad['tail_e95']).median()):.9f}`; E101-plausible median is `{float((e101['tail_e101'] - e101['tail_e95']).median()):.9f}`.

## Category Enrichment

{md_table(top_categories[[
    'category',
    'value',
    'broad_count',
    'e101_count',
    'e101_rate',
    'enrichment_vs_base',
    'pred_vs_e95_e101_mean',
]], '.6f')}

## Numeric Contrast

{md_table(key_numeric[[
    'metric',
    'broad_mean',
    'broad_median',
    'e101_mean',
    'e101_median',
    'mean_shift',
    'median_shift',
    'std_shift',
]], '.9f')}

## Mask Contrast

{md_table(key_masks[[
    'mask_name',
    'broad_count',
    'e101_count',
    'e101_rate',
    'order_match_rate',
    'close10_rate',
    'pred_vs_e95_e101_mean',
    'tail_e101_minus_e95_mean',
    'alpha_median',
    'selected_full_median',
]], '.9f')}

## Interpretation

The survivor set is not a Q2/S3 diffuse-tail subset. The `q2s3` mask has zero
E101-plausible scenarios and predicts E101 far too favorable relative to E95.
E101-plausible worlds mostly come from broad/all or high-hard-tail budget
allocations, with much lower alpha and almost no E101-vs-E95 tail advantage.

That means E101's small loss is not explained by simply finding a better Q2/S3
cell gate. The missing variable looks like public transfer shrinkage plus
tail-budget allocation outside the active Q2/S3 cells. This strengthens the
decision to leave the same-family line unless a genuinely new S3-specific
sensor appears.

## Decision

No submission. E125 turns E124's negative result into a sharper rule: do not
use Q2/S3-mask E99 worlds, full E89, or same-line rollback variants as default
successors. The next experiment should test a different hidden structure, or a
new sensor that explains why public transfer alpha collapses near the
E95/E101 boundary.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    df = load()
    category = category_summary(df)
    numeric = numeric_summary(df)
    masks = mask_summary(df)
    category.to_csv(CATEGORY_OUT, index=False)
    numeric.to_csv(NUMERIC_OUT, index=False)
    masks.to_csv(MASK_OUT, index=False)
    write_report(df, category, numeric, masks)
    print("Wrote:")
    for path in [CATEGORY_OUT, NUMERIC_OUT, MASK_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    broad = df[df["is_broad_plausible"]]
    e101 = broad[broad["e101_sensor_plausible"]]
    print(f"broad={len(broad)} e101_plausible={len(e101)}")
    print(masks.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
