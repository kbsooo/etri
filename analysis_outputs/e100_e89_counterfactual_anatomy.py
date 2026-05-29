#!/usr/bin/env python3
"""E100 E89 counterfactual anatomy after E99.

E99 made E89 the only unresolved candidate with a material E95-beat rate under
E95-conditioned local+tail worlds. This script asks what those worlds look like.

The goal is not to produce a new submission. The goal is to pre-register the
interpretation of an E89 public result before the public LB is observed:

- If E89 beats E95, what hidden-tail allocation did public likely resemble?
- If E89 fails, which counterfactual has been killed?
- Are E89 wins broad, or concentrated in a narrow scenario family?
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

SCENARIO_IN = OUT / "e99_e95_conditioned_tail_transfer_scenarios.csv"
SLICE_OUT = OUT / "e100_e89_counterfactual_anatomy_slices.csv"
CASE_OUT = OUT / "e100_e89_counterfactual_anatomy_cases.csv"
REPORT_OUT = OUT / "e100_e89_counterfactual_anatomy_report.md"

LOCAL_E89 = -0.000025895951955900998
LOCAL_E95 = -0.000026207391227939247
LOCAL_GAP_E89_MINUS_E95 = LOCAL_E89 - LOCAL_E95

FILTERS = {
    "broad_plausible": "is_broad_plausible",
    "tight_plausible": "is_tight_plausible",
    "near_unit_tail": "is_near_unit_tail",
}


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in frame.to_dict("records"):
        row: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                row.append("")
            elif isinstance(value, (float, np.floating)):
                row.append(format(float(value), floatfmt))
            else:
                row.append(str(value))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def load_table() -> pd.DataFrame:
    df = pd.read_csv(SCENARIO_IN)
    df["gamma_label"] = df["gamma"].apply(lambda x: "deterministic" if pd.isna(x) else f"{x:g}")
    df["mask_order"] = df["mask_name"].astype(str) + " / " + df["order_name"].astype(str)
    df["family_mask"] = df["family"].astype(str) + " / " + df["mask_name"].astype(str)
    df["family_mask_order"] = (
        df["family"].astype(str)
        + " / "
        + df["mask_name"].astype(str)
        + " / "
        + df["order_name"].astype(str)
    )
    df["e89_minus_e95"] = df["pred_e89"] - df["pred_e95"]
    df["e89_beats_e95"] = df["e89_minus_e95"] < -1.0e-12
    df["e89_wins_live"] = df["winner_live"].eq("e89")
    df["e95_wins_live"] = df["winner_live"].eq("e95")
    df["tail_advantage_e89"] = df["tail_e95"] - df["tail_e89"]
    df["tail_gap_e89_minus_e95"] = df["tail_e89"] - df["tail_e95"]
    df["needed_tail_advantage_e89"] = (
        df["alpha"] * LOCAL_GAP_E89_MINUS_E95 / df["lambda"]
    )
    df["tail_advantage_surplus_e89"] = (
        df["tail_advantage_e89"] - df["needed_tail_advantage_e89"]
    )
    return df


def summarize_slice(subset: pd.DataFrame, filter_name: str, col: str, min_n: int) -> pd.DataFrame:
    total_n = len(subset)
    base_beat = float(subset["e89_beats_e95"].mean()) if total_n else np.nan
    rows: list[dict[str, object]] = []
    for value, g in subset.groupby(col, dropna=False):
        if len(g) < min_n:
            continue
        rows.append(
            {
                "filter": filter_name,
                "slice_type": col,
                "slice_value": str(value),
                "n": len(g),
                "share": len(g) / total_n if total_n else np.nan,
                "e89_beat_rate": g["e89_beats_e95"].mean(),
                "e89_win_rate": g["e89_wins_live"].mean(),
                "e95_win_rate": g["e95_wins_live"].mean(),
                "beat_rate_lift": g["e89_beats_e95"].mean() - base_beat,
                "mean_e89_minus_e95": g["e89_minus_e95"].mean(),
                "p10_e89_minus_e95": g["e89_minus_e95"].quantile(0.10),
                "p90_e89_minus_e95": g["e89_minus_e95"].quantile(0.90),
                "mean_tail_advantage": g["tail_advantage_e89"].mean(),
                "mean_needed_tail_advantage": g["needed_tail_advantage_e89"].mean(),
                "mean_tail_surplus": g["tail_advantage_surplus_e89"].mean(),
                "alpha_median": g["alpha"].median(),
                "lambda_median": g["lambda"].median(),
                "selected_fractional_cells_mean": g["selected_fractional_cells"].mean(),
            }
        )
    return pd.DataFrame(rows)


def build_slice_summary(df: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for filter_name, filter_col in FILTERS.items():
        subset = df[df[filter_col].astype(bool)].copy()
        for col, min_n in [
            ("family", 5),
            ("mask_name", 5),
            ("order_name", 5),
            ("gamma_label", 5),
            ("mask_order", 5),
            ("family_mask", 5),
            ("family_mask_order", 5),
        ]:
            frames.append(summarize_slice(subset, filter_name, col, min_n))
    out = pd.concat(frames, ignore_index=True)
    out["rank_by_lift"] = out.groupby("filter")["beat_rate_lift"].rank(
        ascending=False, method="first"
    )
    out["rank_by_mean"] = out.groupby("filter")["mean_e89_minus_e95"].rank(
        ascending=True, method="first"
    )
    return out.sort_values(["filter", "rank_by_lift", "rank_by_mean"]).reset_index(drop=True)


def build_case_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for filter_name, filter_col in FILTERS.items():
        subset = df[df[filter_col].astype(bool)].copy()
        if subset.empty:
            continue
        beats = subset[subset["e89_beats_e95"]].copy()
        nonbeats = subset[~subset["e89_beats_e95"]].copy()
        for case_name, g in [("e89_beats_e95", beats), ("e89_not_beats_e95", nonbeats)]:
            rows.append(
                {
                    "filter": filter_name,
                    "case": case_name,
                    "n": len(g),
                    "share": len(g) / len(subset),
                    "mean_e89_minus_e95": g["e89_minus_e95"].mean(),
                    "median_e89_minus_e95": g["e89_minus_e95"].median(),
                    "mean_tail_advantage": g["tail_advantage_e89"].mean(),
                    "mean_needed_tail_advantage": g["needed_tail_advantage_e89"].mean(),
                    "mean_tail_surplus": g["tail_advantage_surplus_e89"].mean(),
                    "alpha_median": g["alpha"].median(),
                    "lambda_median": g["lambda"].median(),
                    "selected_fractional_cells_mean": g["selected_fractional_cells"].mean(),
                    "winner_mode": "" if g.empty else str(g["winner_live"].mode().iloc[0]),
                    "top_mask": "" if g.empty else str(g["mask_name"].mode().iloc[0]),
                    "top_order": "" if g.empty else str(g["order_name"].mode().iloc[0]),
                }
            )
    return pd.DataFrame(rows)


def write_report(df: pd.DataFrame, slices: pd.DataFrame, cases: pd.DataFrame) -> None:
    broad = df[df["is_broad_plausible"].astype(bool)].copy()
    broad_slices = slices[slices["filter"] == "broad_plausible"].copy()
    top_lift = broad_slices.sort_values(["beat_rate_lift", "e89_beat_rate", "n"], ascending=[False, False, False]).head(15)
    top_mean = broad_slices.sort_values(["mean_e89_minus_e95", "e89_beat_rate"]).head(15)
    broad_cases = cases[cases["filter"] == "broad_plausible"].copy()

    e89_beat_rate = broad["e89_beats_e95"].mean()
    e89_win_rate = broad["e89_wins_live"].mean()
    e95_win_rate = broad["e95_wins_live"].mean()

    lines: list[str] = []
    lines.append("# E100 E89 Counterfactual Anatomy")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append(
        "E99 made E89 the only unresolved nontrivial E95 counterfactual. This audit "
        "identifies which E95-conditioned tail worlds make E89 better than E95."
    )
    lines.append("")
    lines.append("## Broad-Plausible Overview")
    lines.append("")
    lines.append(
        f"Broad-plausible scenarios: `{len(broad)}`. E89 beat-E95 rate: "
        f"`{e89_beat_rate:.6f}`. E89 live win-rate: `{e89_win_rate:.6f}`. "
        f"E95 live win-rate: `{e95_win_rate:.6f}`."
    )
    lines.append(
        f"Mean E89-minus-E95 public delta: `{broad['e89_minus_e95'].mean():.9f}`. "
        f"Mean E89 tail advantage over E95: `{broad['tail_advantage_e89'].mean():.9f}`. "
        f"Mean required tail advantage: `{broad['needed_tail_advantage_e89'].mean():.9f}`."
    )
    lines.append("")
    lines.append("## Case Split")
    lines.append("")
    lines.append(md_table(broad_cases, ".9f"))
    lines.append("")
    lines.append("## Top E89-Favorable Slices By Beat-Rate Lift")
    lines.append("")
    lines.append(
        md_table(
            top_lift[
                [
                    "slice_type",
                    "slice_value",
                    "n",
                    "share",
                    "e89_beat_rate",
                    "e89_win_rate",
                    "beat_rate_lift",
                    "mean_e89_minus_e95",
                    "mean_tail_surplus",
                    "alpha_median",
                    "lambda_median",
                ]
            ],
            ".9f",
        )
    )
    lines.append("")
    lines.append("## Top E89-Favorable Slices By Mean Delta")
    lines.append("")
    lines.append(
        md_table(
            top_mean[
                [
                    "slice_type",
                    "slice_value",
                    "n",
                    "share",
                    "e89_beat_rate",
                    "e89_win_rate",
                    "mean_e89_minus_e95",
                    "p10_e89_minus_e95",
                    "p90_e89_minus_e95",
                    "mean_tail_surplus",
                ]
            ],
            ".9f",
        )
    )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    if e89_beat_rate < 0.05:
        lines.append(
            "E89 wins are too rare to justify a public slot as an improvement bet. "
            "Use E89 only if the explicit goal is a narrow falsification of E95 over-localization."
        )
    elif e89_beat_rate < 0.30:
        lines.append(
            "E89 is not the mean-optimal file, but its win pocket is large enough to be the "
            "sharpest E95 counterfactual. A public E89 improvement would imply the public tail "
            "is closer to diffuse E72-cell fallback than to E95's selected hard-tail cells."
        )
    else:
        lines.append(
            "E89's win pocket is broad. That would make it a stronger next submission candidate "
            "rather than only a diagnostic counterfactual."
        )
    lines.append(
        "The decisive quantity is tail advantage surplus: E89 is locally slightly worse than E95, "
        "so it must gain enough E96-tail advantage to overcome that local disadvantage."
    )
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- Slice summary: `{SLICE_OUT.name}`")
    lines.append(f"- Case summary: `{CASE_OUT.name}`")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    df = load_table()
    slices = build_slice_summary(df)
    cases = build_case_summary(df)
    slices.to_csv(SLICE_OUT, index=False)
    cases.to_csv(CASE_OUT, index=False)
    write_report(df, slices, cases)
    print(f"Wrote {SLICE_OUT}")
    print(f"Wrote {CASE_OUT}")
    print(f"Wrote {REPORT_OUT}")
    broad_cases = cases[cases["filter"] == "broad_plausible"]
    print(broad_cases.to_string(index=False))
    print("")
    print("Top broad-plausible E89-favorable slices:")
    broad_slices = slices[slices["filter"] == "broad_plausible"].copy()
    print(
        broad_slices.sort_values(["beat_rate_lift", "e89_beat_rate", "n"], ascending=[False, False, False])
        .head(12)[
            [
                "slice_type",
                "slice_value",
                "n",
                "e89_beat_rate",
                "e89_win_rate",
                "beat_rate_lift",
                "mean_e89_minus_e95",
                "mean_tail_surplus",
            ]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
