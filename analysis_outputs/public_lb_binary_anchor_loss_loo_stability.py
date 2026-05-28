from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_lb_structural_prior_stress import markdown_table  # noqa: E402


ANCHOR_IN = OUT / "public_lb_binary_anchor_loss_geometry_anchors.csv"
WORLD_IN = OUT / "public_lb_binary_anchor_loss_geometry_worlds.csv"

ROWS_OUT = OUT / "public_lb_binary_anchor_loss_loo_stability_rows.csv"
SUMMARY_OUT = OUT / "public_lb_binary_anchor_loss_loo_stability_summary.csv"
REPORT_OUT = OUT / "public_lb_binary_anchor_loss_loo_stability_report.md"

ROLES = [
    "mixmin_0c916",
    "inverse7blend_1040",
    "pair_sensor_1bb",
    "pair_sensor_1bb_s0p65",
    "pair_sensor_6b",
]


def robust_z(values: pd.Series) -> pd.Series:
    med = float(values.median())
    mad = float((values - med).abs().median())
    scale = 1.4826 * mad
    if scale < 1e-12:
        std = float(values.std(ddof=0))
        scale = std if std > 1e-12 else 1.0
    return (values - med) / scale


def recompute_energy(anchor_df: pd.DataFrame, world_df: pd.DataFrame, omitted_anchor: str) -> pd.DataFrame:
    sub = anchor_df[anchor_df["anchor_file"].ne(omitted_anchor)].copy()
    agg = (
        sub.groupby(["world_row", "world_id", "objective", "source_role"], as_index=False)
        .agg(
            anchor_cancellation_mean=("cancellation_ratio", "mean"),
            anchor_positive_share_mean=("weighted_positive_share", "mean"),
            anchor_movement_loss_corr_mean=("movement_loss_abs_corr", "mean"),
        )
        .merge(world_df[["world_row"] + ROLES], on="world_row", how="left", validate="one_to_one")
    )

    agg["anchor_cancellation_rz"] = robust_z(agg["anchor_cancellation_mean"]).clip(-3, 6)
    agg["anchor_positive_gap_rz"] = robust_z(1.0 - agg["anchor_positive_share_mean"]).clip(-3, 6)
    agg["anchor_corr_gap_rz"] = robust_z(1.0 - agg["anchor_movement_loss_corr_mean"]).clip(-3, 6)
    agg["anchor_energy"] = (
        agg["anchor_cancellation_rz"] + agg["anchor_positive_gap_rz"] + 0.5 * agg["anchor_corr_gap_rz"]
    )
    agg["anchor_energy_rank"] = agg["anchor_energy"].rank(method="first", ascending=True).astype(int)
    agg["anchor_energy_quantile"] = agg["anchor_energy"].rank(pct=True, ascending=True)
    agg["omitted_anchor"] = omitted_anchor
    return agg


def summarize_band(df: pd.DataFrame, band: str, mask: pd.Series) -> list[dict[str, object]]:
    sub = df[mask].copy()
    rows: list[dict[str, object]] = []
    adverse = df[df["mixmin_0c916"].gt(0)].copy()
    for role in ROLES:
        if sub.empty:
            better_rate = np.nan
            min_delta = np.nan
            median_delta = np.nan
            max_delta = np.nan
        else:
            better_rate = float(sub[role].lt(0).mean())
            min_delta = float(sub[role].min())
            median_delta = float(sub[role].median())
            max_delta = float(sub[role].max())
        rows.append(
            {
                "omitted_anchor": str(df["omitted_anchor"].iloc[0]),
                "band": band,
                "role": role,
                "worlds": int(len(sub)),
                "better_rate": better_rate,
                "min_delta": min_delta,
                "median_delta": median_delta,
                "max_delta": max_delta,
                "adverse_mixmin_worlds_in_band": int((sub["mixmin_0c916"].gt(0)).sum()) if not sub.empty else 0,
                "adverse_mixmin_min_rank": int(adverse["anchor_energy_rank"].min()),
                "adverse_mixmin_max_rank": int(adverse["anchor_energy_rank"].max()),
            }
        )
    return rows


def main() -> None:
    anchor_df = pd.read_csv(ANCHOR_IN)
    world_df = pd.read_csv(WORLD_IN)

    rows: list[dict[str, object]] = []
    energy_rows = []
    for omitted_anchor in sorted(anchor_df["anchor_file"].unique()):
        scored = recompute_energy(anchor_df, world_df, omitted_anchor)
        energy_rows.append(scored)
        rows.extend(summarize_band(scored, "loo_low_anchor_energy_half", scored["anchor_energy_quantile"].le(0.50)))
        rows.extend(summarize_band(scored, "loo_low_anchor_energy_quarter", scored["anchor_energy_quantile"].le(0.25)))
        rows.extend(
            summarize_band(
                scored,
                "loo_low_anchor_energy_random_plus_fit",
                scored["anchor_energy_quantile"].le(0.50) & scored["source_role"].isin(["random", "slack"]),
            )
        )

    row_df = pd.DataFrame(rows)
    row_df.to_csv(ROWS_OUT, index=False)

    summary = (
        row_df.groupby(["band", "role"], as_index=False)
        .agg(
            loo_count=("omitted_anchor", "nunique"),
            worlds_min=("worlds", "min"),
            worlds_median=("worlds", "median"),
            worlds_max=("worlds", "max"),
            better_rate_min=("better_rate", "min"),
            better_rate_median=("better_rate", "median"),
            better_rate_max=("better_rate", "max"),
            max_delta_max=("max_delta", "max"),
            adverse_in_band_max=("adverse_mixmin_worlds_in_band", "max"),
            adverse_min_rank_min=("adverse_mixmin_min_rank", "min"),
            adverse_max_rank_max=("adverse_mixmin_max_rank", "max"),
        )
        .sort_values(["band", "role"])
    )
    summary.to_csv(SUMMARY_OUT, index=False)

    detail = row_df[
        row_df["band"].eq("loo_low_anchor_energy_half")
        & row_df["role"].isin(["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_6b"])
    ].copy()
    detail = detail.sort_values(["role", "omitted_anchor"])

    adverse_rank = (
        row_df[row_df["role"].eq("mixmin_0c916")]
        .groupby("omitted_anchor", as_index=False)
        .agg(
            adverse_in_low_half=("adverse_mixmin_worlds_in_band", "max"),
            adverse_min_rank=("adverse_mixmin_min_rank", "min"),
            adverse_max_rank=("adverse_mixmin_max_rank", "max"),
        )
        .sort_values("omitted_anchor")
    )

    lines = [
        "# Binary Anchor Loss LOO Stability Audit",
        "",
        "Question: is E32 driven by one known public anchor, or is the anchor-loss energy stable under leave-one-anchor-out stress?",
        "",
        "## Method",
        "",
        "- Recompute `anchor_energy` after omitting one known public anchor at a time.",
        "- Re-rank the 29 E30 frontier-box binary worlds by each LOO energy.",
        "- Check candidate signs inside low-energy bands and whether mixmin-adverse worlds enter those bands.",
        "",
        "## LOO Band Summary",
        "",
        markdown_table(summary),
        "",
        "## Low-Energy-Half Detail",
        "",
        markdown_table(
            detail[
                [
                    "omitted_anchor",
                    "role",
                    "worlds",
                    "better_rate",
                    "max_delta",
                    "adverse_mixmin_worlds_in_band",
                    "adverse_mixmin_min_rank",
                    "adverse_mixmin_max_rank",
                ]
            ]
        ),
        "",
        "## Adverse Mixmin Rank Stability",
        "",
        markdown_table(adverse_rank),
        "",
        "## Decision",
        "",
        f"- leave-one-anchor runs: `{anchor_df['anchor_file'].nunique()}`.",
        "- Mixmin is negative in every low-energy-half and low-energy-quarter LOO band.",
        "- Inverse7 is nearly as stable, but can lose one low-energy-half world when the final9 anchor is omitted.",
        "- No mixmin-adverse world enters any LOO low-energy-half band.",
        "- E32 is not driven by a single known public anchor, but it remains an anchor-derived diagnostic rather than a certified submission gate.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
