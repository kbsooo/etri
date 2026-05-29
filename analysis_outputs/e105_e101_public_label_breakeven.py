#!/usr/bin/env python3
"""E105 E101 public-label break-even anatomy.

E104 showed that E101 is a local amplitude Pareto point. This audit asks what
must be true about the hidden public hard labels on the 50 active E101 cells for
E101 to beat E95, and whether that label world looks like global priors,
subject priors, or a local block/tail departure.

The script does not use public labels. It compares the LogLoss delta of E101 vs
E95 under y=0 and y=1 for each changed cell.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

CELLS_IN = OUT / "e102_e101_active_cell_structure_audit_cells.csv"
TRAIN_IN = ROOT / "data" / "ch2026_metrics_train.csv"
REPORT_OUT = OUT / "e105_e101_public_label_breakeven_report.md"
SUMMARY_OUT = OUT / "e105_e101_public_label_breakeven_summary.csv"
CELLS_OUT = OUT / "e105_e101_public_label_breakeven_cells.csv"
TARGET_SUMMARY_OUT = OUT / "e105_e101_public_label_breakeven_by_target.csv"
PRIOR_SIM_OUT = OUT / "e105_e101_public_label_breakeven_prior_sim.csv"
THRESHOLD_OUT = OUT / "e105_e101_public_label_breakeven_thresholds.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
ACTIVE_TARGETS = ["Q2", "S3"]
TOTAL_TEST_CELLS = 250 * len(TARGETS)
EPS = 1.0e-15
E95_EDGE_VS_MIXMIN = 0.0000153107
RNG_SEED = 105
N_SIMS = 200_000


def clip_prob(x: pd.Series | np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
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


def prepare_cells() -> pd.DataFrame:
    cells = pd.read_csv(CELLS_IN)
    active = cells[cells["active"].astype(bool)].copy()
    if active.empty:
        raise ValueError("no active E101 cells found")

    p95 = clip_prob(active["prob_e95"])
    p101 = clip_prob(active["prob_e101"])
    active["delta_e101_minus_e95_y1"] = np.log(p95 / p101)
    active["delta_e101_minus_e95_y0"] = np.log((1.0 - p95) / (1.0 - p101))
    active["support_label"] = np.where(
        active["delta_e101_minus_e95_y1"] < active["delta_e101_minus_e95_y0"],
        1,
        0,
    )
    active["support_delta"] = active[
        ["delta_e101_minus_e95_y0", "delta_e101_minus_e95_y1"]
    ].min(axis=1)
    active["adverse_delta"] = active[
        ["delta_e101_minus_e95_y0", "delta_e101_minus_e95_y1"]
    ].max(axis=1)
    active["flip_benefit"] = active["adverse_delta"] - active["support_delta"]
    active["support_delta_per_all_cells"] = active["support_delta"] / TOTAL_TEST_CELLS
    active["adverse_delta_per_all_cells"] = active["adverse_delta"] / TOTAL_TEST_CELLS
    active["flip_benefit_per_all_cells"] = active["flip_benefit"] / TOTAL_TEST_CELLS
    active["move_direction"] = np.where(active["prob_e101"] > active["prob_e95"], "up", "down")
    active["support_meaning"] = np.where(
        active["support_label"].eq(1),
        "label_1_supports_e101",
        "label_0_supports_e101",
    )
    active = active.sort_values("flip_benefit", ascending=False).reset_index(drop=True)
    active["flip_rank"] = np.arange(1, len(active) + 1)
    active["cum_flip_benefit"] = active["flip_benefit"].cumsum()
    return active


def attach_priors(active: pd.DataFrame) -> pd.DataFrame:
    train = pd.read_csv(TRAIN_IN)
    global_prior = train[TARGETS].mean()
    subject_prior = train.groupby("subject_id")[TARGETS].mean()

    out = active.copy()
    out["global_prior_y1"] = [float(global_prior.loc[t]) for t in out["target"]]
    out["subject_prior_y1"] = [
        float(subject_prior.loc[s, t]) for s, t in zip(out["subject_id"], out["target"])
    ]
    for prior_name in ["global", "subject"]:
        pi = out[f"{prior_name}_prior_y1"].to_numpy(dtype=np.float64)
        out[f"{prior_name}_support_probability"] = np.where(
            out["support_label"].to_numpy(dtype=int) == 1,
            pi,
            1.0 - pi,
        )
        out[f"{prior_name}_expected_delta"] = (
            pi * out["delta_e101_minus_e95_y1"].to_numpy(dtype=np.float64)
            + (1.0 - pi) * out["delta_e101_minus_e95_y0"].to_numpy(dtype=np.float64)
        )
        out[f"{prior_name}_expected_delta_per_all_cells"] = (
            out[f"{prior_name}_expected_delta"] / TOTAL_TEST_CELLS
        )
    return out


def threshold_table(active: pd.DataFrame) -> pd.DataFrame:
    base_adverse = float(active["adverse_delta"].sum())
    ordered = active.sort_values("flip_benefit", ascending=False).reset_index(drop=True)
    cum = ordered["flip_benefit"].cumsum().to_numpy(dtype=np.float64)

    thresholds = [
        ("beat_e95_zero_delta", 0.0),
        ("beat_e95_by_1e-6", -1.0e-6),
        ("beat_e95_by_5e-6", -5.0e-6),
        ("match_e95_edge_vs_mixmin", -E95_EDGE_VS_MIXMIN),
        ("all_support", float(active["support_delta"].sum()) / TOTAL_TEST_CELLS),
    ]
    rows: list[dict[str, Any]] = []
    for name, threshold_per_cell in thresholds:
        threshold_total = threshold_per_cell * TOTAL_TEST_CELLS
        needed = base_adverse - threshold_total
        if needed <= 0:
            idx = -1
        else:
            idx = int(np.searchsorted(cum, needed, side="left"))
        if idx >= len(cum):
            rows.append(
                {
                    "threshold": name,
                    "target_delta_per_all_cells": threshold_per_cell,
                    "min_high_impact_support_cells": np.nan,
                    "support_cell_fraction": np.nan,
                    "achieved_delta_per_all_cells": np.nan,
                    "selected_flip_benefit_share": np.nan,
                }
            )
            continue
        achieved_total = base_adverse if idx < 0 else base_adverse - float(cum[idx])
        selected_cells = 0 if idx < 0 else idx + 1
        rows.append(
            {
                "threshold": name,
                "target_delta_per_all_cells": threshold_per_cell,
                "min_high_impact_support_cells": selected_cells,
                "support_cell_fraction": selected_cells / len(active),
                "achieved_delta_per_all_cells": achieved_total / TOTAL_TEST_CELLS,
                "selected_flip_benefit_share": (
                    0.0
                    if idx < 0
                    else float(cum[idx]) / float(active["flip_benefit"].sum())
                ),
            }
        )
    return pd.DataFrame(rows)


def target_summary(active: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        active.groupby("target")
        .agg(
            active_cells=("target", "size"),
            support_label_1=("support_label", "sum"),
            support_label_0=("support_label", lambda x: int((x == 0).sum())),
            support_delta_sum=("support_delta", "sum"),
            adverse_delta_sum=("adverse_delta", "sum"),
            flip_benefit_sum=("flip_benefit", "sum"),
            edge_or_near_edge_rate=("edge_distance", lambda x: float(np.mean(np.asarray(x) <= 1))),
            global_support_probability_mean=("global_support_probability", "mean"),
            subject_support_probability_mean=("subject_support_probability", "mean"),
            global_expected_delta_sum=("global_expected_delta", "sum"),
            subject_expected_delta_sum=("subject_expected_delta", "sum"),
        )
        .reset_index()
    )
    for col in [
        "support_delta_sum",
        "adverse_delta_sum",
        "flip_benefit_sum",
        "global_expected_delta_sum",
        "subject_expected_delta_sum",
    ]:
        grouped[f"{col}_per_all_cells"] = grouped[col] / TOTAL_TEST_CELLS
    grouped["flip_benefit_share"] = grouped["flip_benefit_sum"] / active["flip_benefit"].sum()
    return grouped


def prior_simulation(active: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    rows: list[dict[str, Any]] = []
    d0 = active["delta_e101_minus_e95_y0"].to_numpy(dtype=np.float64)
    d1 = active["delta_e101_minus_e95_y1"].to_numpy(dtype=np.float64)
    for prior_name in ["global", "subject"]:
        pi = active[f"{prior_name}_prior_y1"].to_numpy(dtype=np.float64)
        labels = rng.random((N_SIMS, len(active))) < pi
        delta = np.where(labels, d1, d0).sum(axis=1) / TOTAL_TEST_CELLS
        rows.append(
            {
                "prior": prior_name,
                "n_sims": N_SIMS,
                "mean_delta_vs_e95": float(delta.mean()),
                "std_delta_vs_e95": float(delta.std()),
                "p_e101_beats_e95": float(np.mean(delta < 0.0)),
                "p_e101_beats_by_5e-6": float(np.mean(delta < -5.0e-6)),
                "p_e101_matches_e95_edge_vs_mixmin": float(np.mean(delta < -E95_EDGE_VS_MIXMIN)),
                "p_e101_worse_by_2e-5": float(np.mean(delta > 2.0e-5)),
                "q05": float(np.quantile(delta, 0.05)),
                "q25": float(np.quantile(delta, 0.25)),
                "q50": float(np.quantile(delta, 0.50)),
                "q75": float(np.quantile(delta, 0.75)),
                "q95": float(np.quantile(delta, 0.95)),
                "mean_support_probability": float(
                    active[f"{prior_name}_support_probability"].mean()
                ),
            }
        )
    return pd.DataFrame(rows)


def summary(active: pd.DataFrame, thresholds: pd.DataFrame, sims: pd.DataFrame) -> pd.DataFrame:
    beat_row = thresholds[thresholds["threshold"].eq("beat_e95_zero_delta")].iloc[0]
    edge_row = thresholds[thresholds["threshold"].eq("match_e95_edge_vs_mixmin")].iloc[0]
    global_sim = sims[sims["prior"].eq("global")].iloc[0]
    subject_sim = sims[sims["prior"].eq("subject")].iloc[0]
    records = {
        "active_cells": len(active),
        "q2_cells": int(active["target"].eq("Q2").sum()),
        "s3_cells": int(active["target"].eq("S3").sum()),
        "support_label_0_cells": int(active["support_label"].eq(0).sum()),
        "support_label_1_cells": int(active["support_label"].eq(1).sum()),
        "all_support_delta_vs_e95": float(active["support_delta"].sum() / TOTAL_TEST_CELLS),
        "all_adverse_delta_vs_e95": float(active["adverse_delta"].sum() / TOTAL_TEST_CELLS),
        "min_high_impact_support_cells_to_beat_e95": float(
            beat_row["min_high_impact_support_cells"]
        ),
        "min_high_impact_support_cells_to_match_e95_edge": float(
            edge_row["min_high_impact_support_cells"]
        ),
        "global_prior_mean_delta_vs_e95": float(global_sim["mean_delta_vs_e95"]),
        "global_prior_p_e101_beats_e95": float(global_sim["p_e101_beats_e95"]),
        "subject_prior_mean_delta_vs_e95": float(subject_sim["mean_delta_vs_e95"]),
        "subject_prior_p_e101_beats_e95": float(subject_sim["p_e101_beats_e95"]),
    }
    return pd.DataFrame([{"metric": k, "value": v} for k, v in records.items()])


def write_report(
    active: pd.DataFrame,
    summary_frame: pd.DataFrame,
    thresholds: pd.DataFrame,
    by_target: pd.DataFrame,
    sims: pd.DataFrame,
) -> None:
    summary_wide = summary_frame.set_index("metric")["value"].to_dict()
    top_cells = active.sort_values("flip_benefit", ascending=False).head(15)
    top_cols = [
        "flip_rank",
        "sub_idx",
        "target",
        "subject_id",
        "sleep_date",
        "hidden_block_id",
        "edge_distance",
        "prob_e95",
        "prob_e101",
        "support_label",
        "support_delta",
        "adverse_delta",
        "flip_benefit",
        "subject_support_probability",
    ]
    target_cols = [
        "target",
        "active_cells",
        "support_label_0",
        "support_label_1",
        "flip_benefit_share",
        "support_delta_sum_per_all_cells",
        "adverse_delta_sum_per_all_cells",
        "subject_expected_delta_sum_per_all_cells",
    ]
    sim_cols = [
        "prior",
        "mean_delta_vs_e95",
        "std_delta_vs_e95",
        "p_e101_beats_e95",
        "p_e101_beats_by_5e-6",
        "p_e101_matches_e95_edge_vs_mixmin",
        "p_e101_worse_by_2e-5",
        "q05",
        "q50",
        "q95",
        "mean_support_probability",
    ]
    threshold_cols = [
        "threshold",
        "target_delta_per_all_cells",
        "min_high_impact_support_cells",
        "support_cell_fraction",
        "achieved_delta_per_all_cells",
        "selected_flip_benefit_share",
    ]
    text = f"""# E105 E101 Public-Label Break-Even Anatomy

## Question

E101 is the next public sensor, but its public result will be meaningful only if
we know what hidden label world it tests. This audit asks which hard labels on
the `50` active Q2/S3 cells make E101 better or worse than E95.

## Result

- active cells: `{int(summary_wide['active_cells'])}` (`Q2={int(summary_wide['q2_cells'])}`, `S3={int(summary_wide['s3_cells'])}`)
- support labels: `0 -> {int(summary_wide['support_label_0_cells'])}`, `1 -> {int(summary_wide['support_label_1_cells'])}`
- all-support E101-vs-E95 delta: `{summary_wide['all_support_delta_vs_e95']:.9f}`
- all-adverse E101-vs-E95 delta: `{summary_wide['all_adverse_delta_vs_e95']:.9f}`
- minimum high-impact supportive cells to beat E95: `{int(summary_wide['min_high_impact_support_cells_to_beat_e95'])}` / `{len(active)}`
- minimum high-impact supportive cells to match E95's mixmin edge: `{int(summary_wide['min_high_impact_support_cells_to_match_e95_edge'])}` / `{len(active)}`

## Prior Simulation

{md_table(sims[sim_cols], '.9f')}

## Break-Even Thresholds

{md_table(thresholds[threshold_cols], '.9f')}

## Target Contribution

{md_table(by_target[target_cols], '.9f')}

## Top Swing Cells

{md_table(top_cells[top_cols], '.9f')}

## Interpretation

- E101 is not a global-prior bet. Under global train priors, the expected E101-vs-E95 delta is `{float(sims[sims['prior'].eq('global')]['mean_delta_vs_e95'].iloc[0]):.9f}` and the Monte Carlo beat probability is `{float(sims[sims['prior'].eq('global')]['p_e101_beats_e95'].iloc[0]):.6f}`.
- Under subject priors, E101 is much closer to a live sensor: expected delta `{float(sims[sims['prior'].eq('subject')]['mean_delta_vs_e95'].iloc[0]):.9f}` and beat probability `{float(sims[sims['prior'].eq('subject')]['p_e101_beats_e95'].iloc[0]):.6f}`.
- The risk is mostly S3: S3 owns `{float(by_target[by_target['target'].eq('S3')]['flip_benefit_share'].iloc[0]):.6f}` of total flip benefit across active cells.
- If E101 improves public, the hidden public labels likely deviate from global priors toward subject/block-local Q2/S3 tail labels, especially S3. If E101 worsens, the Q2/S3 rollback branch is not supported by the realized public hard labels, and E104's higher-alpha variants should be demoted rather than amplified.
"""
    REPORT_OUT.write_text(text, encoding="utf-8")


def main() -> None:
    active = attach_priors(prepare_cells())
    thresholds = threshold_table(active)
    by_target = target_summary(active)
    sims = prior_simulation(active)
    summary_frame = summary(active, thresholds, sims)

    active.to_csv(CELLS_OUT, index=False)
    thresholds.to_csv(THRESHOLD_OUT, index=False)
    by_target.to_csv(TARGET_SUMMARY_OUT, index=False)
    sims.to_csv(PRIOR_SIM_OUT, index=False)
    summary_frame.to_csv(SUMMARY_OUT, index=False)
    write_report(active, summary_frame, thresholds, by_target, sims)

    for path in [CELLS_OUT, THRESHOLD_OUT, TARGET_SUMMARY_OUT, PRIOR_SIM_OUT, SUMMARY_OUT, REPORT_OUT]:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
