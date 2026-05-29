#!/usr/bin/env python3
"""E124 E101-conditioned tail transfer audit.

SAUNA question:
E99 used a deliberately small transfer model, local structural margin plus
E72-adverse hard-tail exposure, to explain two public observations: E72 failed
and E95 won. E101 is now a third public observation. Does the same two-term
world explain E101's small loss? If yes, which non-same-line candidate remains
live? If not, the next submission should not be chosen by the E99 abstraction.

This is not a submission generator. E101 is treated as a held-out public sensor
for the existing E96/E99 world family.
"""

from __future__ import annotations

from pathlib import Path
import math
import sys
from typing import Callable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e96_public_miss_budget_tail_scenarios as e96  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660

OBS_DELTA = {
    "mixmin": 0.0,
    "failed_e72": E72_PUBLIC - MIXMIN_PUBLIC,
    "e95": E95_PUBLIC - MIXMIN_PUBLIC,
    "e101": E101_PUBLIC - MIXMIN_PUBLIC,
}

FILES = {
    **e96.FILES,
    "e101": "submission_e101_q2s3tail_177569bc.csv",
}

LOCAL_DELTA = {
    "mixmin": 0.0,
    "failed_e72": -0.0000105458,
    "e85": -0.00002387582191021309,
    "e86": -0.000027705869828476004,
    "noq2": -0.000026946089001889106,
    "e90": -0.000026932385085221,
    "e89": -0.000025895951955900998,
    "e95": -0.000026207391227939247,
    "e101": -0.00002537240527333839,
}

SENSOR_CANDIDATES = ["e101"]
FUTURE_CANDIDATES = ["e85", "e86", "noq2", "e90", "e89"]
LIVE_CANDIDATES = [*FUTURE_CANDIDATES, "e95"]
ALL_CANDIDATES = ["mixmin", "failed_e72", *FUTURE_CANDIDATES, "e95", *SENSOR_CANDIDATES]

SCENARIO_OUT = OUT / "e124_e101_conditioned_tail_transfer_scenarios.csv"
SUMMARY_OUT = OUT / "e124_e101_conditioned_tail_transfer_summary.csv"
FILTER_OUT = OUT / "e124_e101_conditioned_tail_transfer_filter_summary.csv"
REPORT_OUT = OUT / "e124_e101_conditioned_tail_transfer_report.md"


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
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


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def solve_transfer(row: pd.Series) -> tuple[float, float, bool, float]:
    x = np.array(
        [
            [LOCAL_DELTA["failed_e72"], float(row["failed_e72"])],
            [LOCAL_DELTA["e95"], float(row["e95"])],
        ],
        dtype=np.float64,
    )
    y = np.array([OBS_DELTA["failed_e72"], OBS_DELTA["e95"]], dtype=np.float64)
    det = float(np.linalg.det(x))
    if not math.isfinite(det) or abs(det) < 1.0e-16:
        return np.nan, np.nan, False, det
    alpha, lam = np.linalg.solve(x, y)
    ok = bool(math.isfinite(float(alpha)) and math.isfinite(float(lam)))
    return float(alpha), float(lam), ok, det


def build_scenarios_with_e101() -> pd.DataFrame:
    sample = load_sub(FILES["mixmin"]).sort_values(KEYS).reset_index(drop=True)
    preds = {name: load_pred(file_name, sample) for name, file_name in FILES.items()}
    base = preds["mixmin"]
    e72 = preds["failed_e72"]

    e72_delta = logit(e72) - logit(base)
    wrong_is_zero = e72_delta > 1.0e-9
    wrong_is_one = e72_delta < -1.0e-9
    adverse = {
        name: e96.adverse_delta_for_e72_direction(pred, base, wrong_is_zero, wrong_is_one)
        for name, pred in preds.items()
    }
    e72_pos = np.maximum(adverse["failed_e72"], 0.0)
    n_cells = int(base.size)
    budget_sum = float(OBS_DELTA["failed_e72"] * n_cells)
    masks = e96.build_masks(preds, e72_pos, e72_delta)
    adverse_flat = {name: arr.reshape(-1) for name, arr in adverse.items()}
    meta, long = e96.build_scenarios(e72_pos.reshape(-1), masks, adverse_flat, budget_sum, n_cells)
    complete = long.merge(meta, on="scenario_id", how="left")
    complete = complete[complete["complete_budget"].astype(bool)].copy()
    wide = complete.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    meta_idx = meta.set_index("scenario_id")
    cols = [
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
    table = meta_idx[cols].join(wide[ALL_CANDIDATES], how="inner").reset_index()
    return table


def apply_transfer(table: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for rec in table.to_dict("records"):
        row = pd.Series(rec)
        alpha, lam, solved, det = solve_transfer(row)
        out = dict(rec)
        out.update({"alpha": alpha, "lambda": lam, "solved": solved, "det": det})
        for cand in ALL_CANDIDATES:
            tail = float(row[cand])
            pred = alpha * LOCAL_DELTA[cand] + lam * tail if solved else np.nan
            if cand in ["mixmin", "failed_e72", "e95"]:
                pred = OBS_DELTA[cand]
            out[f"tail_{cand}"] = tail
            out[f"pred_{cand}"] = float(pred)
            out[f"pred_vs_e95_{cand}"] = float(pred - OBS_DELTA["e95"])
        if solved:
            future_preds = {cand: float(out[f"pred_{cand}"]) for cand in FUTURE_CANDIDATES}
            live_preds = {cand: float(out[f"pred_{cand}"]) for cand in LIVE_CANDIDATES}
            out["winner_future"] = min(future_preds, key=future_preds.get)
            out["winner_live"] = min(live_preds, key=live_preds.get)
            out["best_future_delta"] = min(future_preds.values())
            out["best_live_delta"] = min(live_preds.values())
        else:
            out["winner_future"] = ""
            out["winner_live"] = ""
            out["best_future_delta"] = np.nan
            out["best_live_delta"] = np.nan
        records.append(out)
    out = pd.DataFrame(records)
    out["e101_residual"] = out["pred_e101"] - OBS_DELTA["e101"]
    out["e101_abs_residual"] = out["e101_residual"].abs()
    out["e101_order_match"] = (out["pred_e95"] < out["pred_e101"]) & (out["pred_e101"] < 0.0)
    out["e101_close_pm5e6"] = out["e101_abs_residual"] <= 5.0e-6
    out["e101_close_pm10e6"] = out["e101_abs_residual"] <= 10.0e-6
    out["e101_sensor_plausible"] = out["e101_order_match"] & out["e101_close_pm10e6"]
    out["is_positive_transfer"] = (out["alpha"] > 0.0) & (out["lambda"] > 0.0)
    out["is_broad_plausible"] = (
        out["solved"] & (out["alpha"] > 0.0) & (out["alpha"] <= 8.0) & (out["lambda"] > 0.0) & (out["lambda"] <= 4.0)
    )
    out["is_tight_plausible"] = (
        out["solved"] & (out["alpha"] >= 0.25) & (out["alpha"] <= 6.0) & (out["lambda"] >= 0.25) & (out["lambda"] <= 3.0)
    )
    return out


def filter_defs() -> dict[str, Callable[[pd.DataFrame], pd.Series]]:
    return {
        "solved_all": lambda x: x["solved"],
        "broad_plausible": lambda x: x["is_broad_plausible"],
        "tight_plausible": lambda x: x["is_tight_plausible"],
        "e101_order_match": lambda x: x["is_broad_plausible"] & x["e101_order_match"],
        "e101_close_pm10e6": lambda x: x["is_broad_plausible"] & x["e101_close_pm10e6"],
        "e101_close_pm5e6": lambda x: x["is_broad_plausible"] & x["e101_close_pm5e6"],
        "e101_sensor_plausible": lambda x: x["is_broad_plausible"] & x["e101_sensor_plausible"],
    }


def summarize(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    filter_rows: list[dict[str, object]] = []
    for name, fn in filter_defs().items():
        subset = table[fn(table)].copy()
        if subset.empty:
            filter_rows.append({"filter": name, "n_scenarios": 0})
            continue
        filter_rows.append(
            {
                "filter": name,
                "n_scenarios": int(len(subset)),
                "alpha_median": float(subset["alpha"].median()),
                "lambda_median": float(subset["lambda"].median()),
                "e101_residual_mean": float(subset["e101_residual"].mean()),
                "e101_abs_residual_median": float(subset["e101_abs_residual"].median()),
                "e101_order_match_rate": float(subset["e101_order_match"].mean()),
                "winner_live_mode": str(subset["winner_live"].mode().iloc[0]),
                "winner_future_mode": str(subset["winner_future"].mode().iloc[0]),
            }
        )
        for cand in [*FUTURE_CANDIDATES, "e95", "e101"]:
            pred = subset[f"pred_{cand}"].astype(float)
            vs_e95 = subset[f"pred_vs_e95_{cand}"].astype(float)
            rows.append(
                {
                    "filter": name,
                    "candidate": cand,
                    "n_scenarios": int(len(subset)),
                    "mean_pred_delta": float(pred.mean()),
                    "median_pred_delta": float(pred.median()),
                    "p10_pred_delta": float(pred.quantile(0.10)),
                    "p90_pred_delta": float(pred.quantile(0.90)),
                    "p95_pred_delta": float(pred.quantile(0.95)),
                    "mean_vs_e95": float(vs_e95.mean()),
                    "median_vs_e95": float(vs_e95.median()),
                    "p90_vs_e95": float(vs_e95.quantile(0.90)),
                    "p95_vs_e95": float(vs_e95.quantile(0.95)),
                    "beat_e95_rate": float((pred < OBS_DELTA["e95"] - 1.0e-12).mean()),
                    "win_rate_live": float((subset["winner_live"] == cand).mean()) if cand in LIVE_CANDIDATES else np.nan,
                    "win_rate_future": float((subset["winner_future"] == cand).mean()) if cand in FUTURE_CANDIDATES else np.nan,
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(filter_rows)


def write_report(table: pd.DataFrame, summary: pd.DataFrame, filters: pd.DataFrame) -> None:
    broad = filters[filters["filter"].eq("broad_plausible")].iloc[0]
    e101_plaus = filters[filters["filter"].eq("e101_sensor_plausible")]
    e101_count = int(e101_plaus.iloc[0]["n_scenarios"]) if len(e101_plaus) else 0
    view_filters = ["broad_plausible", "e101_order_match", "e101_close_pm10e6", "e101_sensor_plausible"]
    view = summary[summary["filter"].isin(view_filters)].copy()
    view = view[view["candidate"].isin([*FUTURE_CANDIDATES, "e95", "e101"])]
    filter_view = filters[filters["filter"].isin(view_filters)].copy()
    future_plaus = view[(view["filter"].eq("e101_sensor_plausible")) & (view["candidate"].isin(FUTURE_CANDIDATES))]
    if not future_plaus.empty:
        future_best = future_plaus.sort_values(["beat_e95_rate", "mean_vs_e95"], ascending=[False, True]).iloc[0]
        future_mode = future_plaus.sort_values(["win_rate_future", "mean_vs_e95"], ascending=[False, True]).iloc[0]
        best_line = (
            f"Highest beat-E95 future candidate under the E101-plausible subset is `{future_best['candidate']}` "
            f"with beat-E95 rate `{future_best['beat_e95_rate']:.6f}` and mean vs E95 `{future_best['mean_vs_e95']:.9f}`. "
            f"Highest future winner-mode candidate is `{future_mode['candidate']}` with future win rate "
            f"`{future_mode['win_rate_future']:.6f}`."
        )
    else:
        best_line = "No E101-plausible subset survives, so E99's two-term world cannot rank the future candidates after E101."

    bad_pred = table[table["is_broad_plausible"]].copy()
    e101_pred_mean = float(bad_pred["pred_e101"].mean())
    e101_pred_p95 = float(bad_pred["pred_e101"].quantile(0.95))
    report = f"""# E124 E101-conditioned tail transfer audit

## Question

E99 explained E72 failure and E95 success with a two-term world:

`public_delta = alpha * local_margin + lambda * E72_hard_tail_delta`.

E101 is now a third public observation. The question is whether this same world
family also predicts E101's small loss, and whether conditioning on E101 changes
the next public-sensor queue.

Observed public deltas versus mixmin:

- E72: `{OBS_DELTA['failed_e72']:.10f}`
- E95: `{OBS_DELTA['e95']:.10f}`
- E101: `{OBS_DELTA['e101']:.10f}`

## Filter Health

{md_table(filter_view, '.9f')}

In broad-plausible E99 worlds, mean predicted E101 delta is `{e101_pred_mean:.9f}`
and p95 is `{e101_pred_p95:.9f}` versus actual `{OBS_DELTA['e101']:.9f}`.

E101-plausible scenario count: `{e101_count}`.

## Candidate Summary

{md_table(view[[
    'filter',
    'candidate',
    'n_scenarios',
    'mean_pred_delta',
    'p90_pred_delta',
    'p95_pred_delta',
    'mean_vs_e95',
    'p95_vs_e95',
    'beat_e95_rate',
    'win_rate_live',
    'win_rate_future',
]], '.9f')}

## Interpretation

- If E101-plausible scenarios are rare or empty, the E99 two-term abstraction is
  missing a boundary variable: it can explain E72/E95 but not E101.
- If many E101-plausible scenarios survive and still keep E95 best, the hard-tail
  plateau explanation strengthens.
- If a future candidate beats E95 often inside the E101-plausible subset, that
  candidate becomes the next information sensor, not because of CV but because it
  tests the residual world left after E101.

{best_line}

## Decision

Do not create a submission from E124. Use it as the post-E101 validity check for
the old E99 transfer world. If the E101-plausible subset is weak, the next
experiment should leave `local + E72 hard-tail` transfer and test a different
hidden structure rather than submit E89/E85/E90/E86 by inherited pre-E101 order.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    base = build_scenarios_with_e101()
    table = apply_transfer(base)
    summary, filters = summarize(table)
    table.to_csv(SCENARIO_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    filters.to_csv(FILTER_OUT, index=False)
    write_report(table, summary, filters)

    print("Wrote:")
    for path in [SCENARIO_OUT, SUMMARY_OUT, FILTER_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    print(filters.to_string(index=False))
    broad = summary[summary["filter"].eq("e101_sensor_plausible")]
    if len(broad):
        print(broad.sort_values(["beat_e95_rate", "mean_vs_e95"], ascending=[False, True]).to_string(index=False))


if __name__ == "__main__":
    main()
