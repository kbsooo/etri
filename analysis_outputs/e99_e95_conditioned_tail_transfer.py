#!/usr/bin/env python3
"""E99 E95-conditioned tail transfer audit.

E96 allocated the observed E72 public miss across many plausible hard-label tail
worlds, but it did not force those worlds to also explain the new E95 public
gain. This audit asks a narrower question:

Can a two-term transfer model, local structural margin plus E72-tail exposure,
simultaneously explain the failed E72 public miss and the successful E95 public
gain? If yes, which unresolved candidate wins inside those E95-consistent
worlds?

The model is intentionally small:

    public_delta(candidate) = alpha * local_delta(candidate)
                            + lambda * e96_tail_delta(candidate)

For each complete E96 tail scenario, alpha and lambda are solved exactly from
the two public observations E72 and E95. This is not a leaderboard regressor; it
is a falsifier for whether the E96 tail worlds remain coherent after the E95
sensor is observed.
"""

from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
E95_PUBLIC = 0.5762913298

OBSERVED_PUBLIC_DELTA = {
    "mixmin": 0.0,
    "failed_e72": E72_PUBLIC - MIXMIN_PUBLIC,
    "e95": E95_PUBLIC - MIXMIN_PUBLIC,
}

# Local all-combo deltas versus mixmin from the stress reports that created each
# materialized file. Negative is locally better than mixmin.
LOCAL_DELTA = {
    "mixmin": 0.0,
    "failed_e72": -0.0000105458,
    "e85": -0.00002387582191021309,
    "e86": -0.000027705869828476004,
    "noq2": -0.000026946089001889106,
    "e90": -0.000026932385085221,
    "e89": -0.000025895951955900998,
    "e95": -0.000026207391227939247,
}

LIVE_CANDIDATES = ["e85", "e86", "noq2", "e90", "e89", "e95"]
ALL_CANDIDATES = ["mixmin", "failed_e72", *LIVE_CANDIDATES]

SCENARIO_IN = OUT / "e96_public_miss_budget_scenarios.csv"
SCENARIO_OUT = OUT / "e99_e95_conditioned_tail_transfer_scenarios.csv"
SUMMARY_OUT = OUT / "e99_e95_conditioned_tail_transfer_summary.csv"
FILTER_SUMMARY_OUT = OUT / "e99_e95_conditioned_tail_transfer_filter_summary.csv"
REPORT_OUT = OUT / "e99_e95_conditioned_tail_transfer_report.md"


FILTERS = {
    "solved_all": lambda x: x["solved"],
    "positive_transfer": lambda x: x["solved"] & (x["alpha"] > 0) & (x["lambda"] > 0),
    "broad_plausible": lambda x: (
        x["solved"]
        & (x["alpha"] > 0)
        & (x["alpha"] <= 8)
        & (x["lambda"] > 0)
        & (x["lambda"] <= 4)
    ),
    "tight_plausible": lambda x: (
        x["solved"]
        & (x["alpha"] >= 0.25)
        & (x["alpha"] <= 6)
        & (x["lambda"] >= 0.25)
        & (x["lambda"] <= 3)
    ),
    "near_unit_tail": lambda x: (
        x["solved"]
        & (x["alpha"] >= 0.5)
        & (x["alpha"] <= 5)
        & (x["lambda"] >= 0.5)
        & (x["lambda"] <= 2.5)
    ),
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


def load_wide_scenarios() -> pd.DataFrame:
    raw = pd.read_csv(SCENARIO_IN)
    raw = raw[raw["complete_budget"].astype(bool)].copy()
    meta_cols = [
        "scenario_id",
        "family",
        "mask_name",
        "order_name",
        "gamma",
        "complete_budget",
        "achieved_e72_delta",
        "target_e72_delta",
        "budget_coverage",
        "positive_cells_available",
        "selected_full_cells",
        "selected_fractional_cells",
    ]
    meta = raw[meta_cols].drop_duplicates("scenario_id").set_index("scenario_id")
    wide = raw.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    missing = [c for c in ALL_CANDIDATES if c not in wide.columns]
    if missing:
        raise RuntimeError(f"Missing candidates in {SCENARIO_IN}: {missing}")
    wide = wide[ALL_CANDIDATES]
    return meta.join(wide)


def solve_transfer(row: pd.Series) -> tuple[float, float, bool, float]:
    local = np.array(
        [
            [LOCAL_DELTA["failed_e72"], float(row["failed_e72"])],
            [LOCAL_DELTA["e95"], float(row["e95"])],
        ],
        dtype=np.float64,
    )
    public = np.array(
        [
            OBSERVED_PUBLIC_DELTA["failed_e72"],
            OBSERVED_PUBLIC_DELTA["e95"],
        ],
        dtype=np.float64,
    )
    det = float(np.linalg.det(local))
    if not math.isfinite(det) or abs(det) < 1.0e-16:
        return np.nan, np.nan, False, det
    alpha, lam = np.linalg.solve(local, public)
    solved = bool(math.isfinite(float(alpha)) and math.isfinite(float(lam)))
    return float(alpha), float(lam), solved, det


def build_transfer_table(wide: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for scenario_id, row in wide.iterrows():
        alpha, lam, solved, det = solve_transfer(row)
        rec: dict[str, object] = {
            "scenario_id": scenario_id,
            "family": row["family"],
            "mask_name": row["mask_name"],
            "order_name": row["order_name"],
            "gamma": row["gamma"],
            "complete_budget": bool(row["complete_budget"]),
            "achieved_e72_delta": float(row["achieved_e72_delta"]),
            "target_e72_delta": float(row["target_e72_delta"]),
            "budget_coverage": float(row["budget_coverage"]),
            "positive_cells_available": int(row["positive_cells_available"]),
            "selected_full_cells": int(row["selected_full_cells"]),
            "selected_fractional_cells": float(row["selected_fractional_cells"]),
            "alpha": alpha,
            "lambda": lam,
            "solved": solved,
            "det": det,
        }
        if solved:
            for cand in ALL_CANDIDATES:
                tail = float(row[cand])
                pred = alpha * LOCAL_DELTA[cand] + lam * tail
                if cand in OBSERVED_PUBLIC_DELTA:
                    pred = OBSERVED_PUBLIC_DELTA[cand]
                rec[f"tail_{cand}"] = tail
                rec[f"pred_{cand}"] = float(pred)
                rec[f"pred_vs_e95_{cand}"] = float(pred - OBSERVED_PUBLIC_DELTA["e95"])
            live_preds = {cand: float(rec[f"pred_{cand}"]) for cand in LIVE_CANDIDATES}
            rec["winner_live"] = min(live_preds, key=live_preds.get)
            rec["best_live_delta"] = min(live_preds.values())
        else:
            for cand in ALL_CANDIDATES:
                rec[f"tail_{cand}"] = float(row[cand])
                rec[f"pred_{cand}"] = np.nan
                rec[f"pred_vs_e95_{cand}"] = np.nan
            rec["winner_live"] = ""
            rec["best_live_delta"] = np.nan
        rows.append(rec)
    table = pd.DataFrame(rows)
    table["abs_e72_residual"] = np.abs(
        table["pred_failed_e72"] - OBSERVED_PUBLIC_DELTA["failed_e72"]
    )
    table["abs_e95_residual"] = np.abs(table["pred_e95"] - OBSERVED_PUBLIC_DELTA["e95"])
    table["is_positive_transfer"] = (table["alpha"] > 0) & (table["lambda"] > 0)
    table["is_broad_plausible"] = FILTERS["broad_plausible"](table)
    table["is_tight_plausible"] = FILTERS["tight_plausible"](table)
    table["is_near_unit_tail"] = FILTERS["near_unit_tail"](table)
    return table


def summarize_candidates(table: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for filter_name, filter_fn in FILTERS.items():
        subset = table[filter_fn(table)].copy()
        if subset.empty:
            continue
        for cand in LIVE_CANDIDATES:
            pred = subset[f"pred_{cand}"].astype(float)
            vs_e95 = subset[f"pred_vs_e95_{cand}"].astype(float)
            rows.append(
                {
                    "filter": filter_name,
                    "candidate": cand,
                    "n_scenarios": len(subset),
                    "mean_pred_delta": pred.mean(),
                    "median_pred_delta": pred.median(),
                    "p10_pred_delta": pred.quantile(0.10),
                    "p90_pred_delta": pred.quantile(0.90),
                    "p95_pred_delta": pred.quantile(0.95),
                    "min_pred_delta": pred.min(),
                    "max_pred_delta": pred.max(),
                    "mean_vs_e95": vs_e95.mean(),
                    "median_vs_e95": vs_e95.median(),
                    "p90_vs_e95": vs_e95.quantile(0.90),
                    "p95_vs_e95": vs_e95.quantile(0.95),
                    "beat_e95_rate": (pred < OBSERVED_PUBLIC_DELTA["e95"] - 1.0e-12).mean(),
                    "win_rate_live": (subset["winner_live"] == cand).mean(),
                }
            )
    return pd.DataFrame(rows)


def summarize_filters(table: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for filter_name, filter_fn in FILTERS.items():
        subset = table[filter_fn(table)].copy()
        if subset.empty:
            rows.append(
                {
                    "filter": filter_name,
                    "n_scenarios": 0,
                    "alpha_median": np.nan,
                    "alpha_p10": np.nan,
                    "alpha_p90": np.nan,
                    "lambda_median": np.nan,
                    "lambda_p10": np.nan,
                    "lambda_p90": np.nan,
                    "winner_mode": "",
                    "best_mean_candidate": "",
                    "best_p95_candidate": "",
                    "e90_beat_e95_rate": np.nan,
                    "e86_beat_e95_rate": np.nan,
                    "e85_beat_e95_rate": np.nan,
                }
            )
            continue
        sub_summary = summary[summary["filter"] == filter_name].copy()
        best_mean = sub_summary.sort_values("mean_pred_delta").iloc[0]["candidate"]
        best_p95 = sub_summary.sort_values("p95_pred_delta").iloc[0]["candidate"]
        mode = subset["winner_live"].mode()
        rows.append(
            {
                "filter": filter_name,
                "n_scenarios": len(subset),
                "alpha_median": subset["alpha"].median(),
                "alpha_p10": subset["alpha"].quantile(0.10),
                "alpha_p90": subset["alpha"].quantile(0.90),
                "lambda_median": subset["lambda"].median(),
                "lambda_p10": subset["lambda"].quantile(0.10),
                "lambda_p90": subset["lambda"].quantile(0.90),
                "winner_mode": "" if mode.empty else str(mode.iloc[0]),
                "best_mean_candidate": str(best_mean),
                "best_p95_candidate": str(best_p95),
                "e90_beat_e95_rate": float(
                    sub_summary.loc[sub_summary["candidate"] == "e90", "beat_e95_rate"].iloc[0]
                ),
                "e86_beat_e95_rate": float(
                    sub_summary.loc[sub_summary["candidate"] == "e86", "beat_e95_rate"].iloc[0]
                ),
                "e85_beat_e95_rate": float(
                    sub_summary.loc[sub_summary["candidate"] == "e85", "beat_e95_rate"].iloc[0]
                ),
            }
        )
    return pd.DataFrame(rows)


def write_report(table: pd.DataFrame, summary: pd.DataFrame, filter_summary: pd.DataFrame) -> None:
    solved = table[table["solved"]].copy()
    broad = summary[summary["filter"] == "broad_plausible"].copy()
    tight = summary[summary["filter"] == "tight_plausible"].copy()
    near = summary[summary["filter"] == "near_unit_tail"].copy()

    lines: list[str] = []
    lines.append("# E99 E95-Conditioned Tail Transfer Audit")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append(
        "E96 explains the E72 public miss with hard-tail worlds. After E95 became public-positive, "
        "do those worlds still rank E90/E86/E85 the same way when they must also explain E95?"
    )
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "For every complete E96 scenario, solve `public_delta = alpha * local_delta + "
        "lambda * e96_tail_delta` exactly on failed E72 and E95. Then score unresolved "
        "candidates in the same scenario. Positive alpha/lambda means both local structural "
        "margin and hard-tail exposure have interpretable signs."
    )
    lines.append("")
    lines.append("## Filter Summary")
    lines.append("")
    lines.append(md_table(filter_summary, ".9f"))
    lines.append("")
    lines.append("## Broad Plausible Candidate Summary")
    lines.append("")
    lines.append(
        md_table(
            broad[
                [
                    "candidate",
                    "n_scenarios",
                    "mean_pred_delta",
                    "p90_pred_delta",
                    "p95_pred_delta",
                    "mean_vs_e95",
                    "p95_vs_e95",
                    "beat_e95_rate",
                    "win_rate_live",
                ]
            ].sort_values(["mean_pred_delta", "p95_pred_delta"]),
            ".9f",
        )
    )
    lines.append("")
    lines.append("## Tight Plausible Candidate Summary")
    lines.append("")
    lines.append(
        md_table(
            tight[
                [
                    "candidate",
                    "n_scenarios",
                    "mean_pred_delta",
                    "p90_pred_delta",
                    "p95_pred_delta",
                    "mean_vs_e95",
                    "p95_vs_e95",
                    "beat_e95_rate",
                    "win_rate_live",
                ]
            ].sort_values(["mean_pred_delta", "p95_pred_delta"])
            if not tight.empty
            else tight,
            ".9f",
        )
    )
    lines.append("")
    lines.append("## Near-Unit Tail Candidate Summary")
    lines.append("")
    lines.append(
        md_table(
            near[
                [
                    "candidate",
                    "n_scenarios",
                    "mean_pred_delta",
                    "p90_pred_delta",
                    "p95_pred_delta",
                    "mean_vs_e95",
                    "p95_vs_e95",
                    "beat_e95_rate",
                    "win_rate_live",
                ]
            ].sort_values(["mean_pred_delta", "p95_pred_delta"])
            if not near.empty
            else near,
            ".9f",
        )
    )
    lines.append("")
    lines.append("## Transfer Geometry")
    lines.append("")
    if solved.empty:
        lines.append("No E96 scenario produced a numerically stable two-observation transfer solve.")
    else:
        lines.append(
            f"Solved scenarios: `{len(solved)}`. Positive-transfer scenarios: "
            f"`{int(table['is_positive_transfer'].sum())}`. Broad-plausible scenarios: "
            f"`{int(table['is_broad_plausible'].sum())}`."
        )
        lines.append(
            f"Alpha median/p10/p90: `{solved['alpha'].median():.9f}`, "
            f"`{solved['alpha'].quantile(0.10):.9f}`, "
            f"`{solved['alpha'].quantile(0.90):.9f}`."
        )
        lines.append(
            f"Lambda median/p10/p90: `{solved['lambda'].median():.9f}`, "
            f"`{solved['lambda'].quantile(0.10):.9f}`, "
            f"`{solved['lambda'].quantile(0.90):.9f}`."
        )
        lines.append(
            f"Max public-anchor residual after solving: E72 "
            f"`{table['abs_e72_residual'].max():.3e}`, E95 "
            f"`{table['abs_e95_residual'].max():.3e}`."
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    broad_filter = filter_summary[filter_summary["filter"] == "broad_plausible"]
    if broad_filter.empty or int(broad_filter.iloc[0]["n_scenarios"]) == 0:
        lines.append(
            "The two-term transfer model is rejected as an interpretable E95-conditioned selector: "
            "no broad-plausible alpha/lambda worlds survive. The next submission should be chosen "
            "as an information sensor, not from this model."
        )
    else:
        best_mean = broad.sort_values("mean_pred_delta").iloc[0]
        best_p95 = broad.sort_values("p95_pred_delta").iloc[0]
        e90 = broad[broad["candidate"] == "e90"].iloc[0]
        e86 = broad[broad["candidate"] == "e86"].iloc[0]
        e85 = broad[broad["candidate"] == "e85"].iloc[0]
        lines.append(
            f"Under broad-plausible E95-conditioned worlds, best mean candidate is "
            f"`{best_mean['candidate']}` and best p95 candidate is `{best_p95['candidate']}`."
        )
        lines.append(
            f"E90/E86/E85 beat-E95 rates are `{e90['beat_e95_rate']:.6f}`, "
            f"`{e86['beat_e95_rate']:.6f}`, `{e85['beat_e95_rate']:.6f}`."
        )
        lines.append(
            "Read negative `mean_vs_e95` as predicted public improvement over the current E95 "
            "frontier and positive `p95_vs_e95` as downside tail relative to E95."
        )
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- Scenario table: `{SCENARIO_OUT.name}`")
    lines.append(f"- Candidate summary: `{SUMMARY_OUT.name}`")
    lines.append(f"- Filter summary: `{FILTER_SUMMARY_OUT.name}`")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    wide = load_wide_scenarios()
    table = build_transfer_table(wide)
    summary = summarize_candidates(table)
    filter_summary = summarize_filters(table, summary)
    table.to_csv(SCENARIO_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    filter_summary.to_csv(FILTER_SUMMARY_OUT, index=False)
    write_report(table, summary, filter_summary)

    print(f"Wrote {SCENARIO_OUT}")
    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {FILTER_SUMMARY_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(filter_summary.to_string(index=False))
    broad = summary[summary["filter"] == "broad_plausible"].sort_values(
        ["mean_pred_delta", "p95_pred_delta"]
    )
    if not broad.empty:
        print("")
        print("Broad-plausible candidate order:")
        print(
            broad[
                [
                    "candidate",
                    "mean_pred_delta",
                    "p95_pred_delta",
                    "mean_vs_e95",
                    "beat_e95_rate",
                    "win_rate_live",
                ]
            ].to_string(index=False)
        )


if __name__ == "__main__":
    main()
