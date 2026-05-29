#!/usr/bin/env python3
"""E96 public-miss budget tail scenarios.

E72 is the first post-mixmin public miss. E94/E95 converted that miss into a
hard-label tail lens. This script asks the sharper falsifier: if E72 lost only
0.0001011367 LogLoss, where could that loss have been concentrated, and which
candidate is robust across those plausible tail worlds?

This script does not fit public labels. It fixes only the observed E72-minus-
mixmin public miss as a total hard-tail budget, then allocates that budget over
E72-adverse cells under many scenario rules. Each live candidate is scored on
the same selected adverse hard labels.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
import e94_soft_health_hard_tail_audit as e94  # noqa: E402


MIXMIN_PUBLIC = 0.5763066405
E72_PUBLIC = 0.5764077772
E95_PUBLIC = 0.5762913298
E72_PUBLIC_MISS = E72_PUBLIC - MIXMIN_PUBLIC
E95_PUBLIC_GAIN = MIXMIN_PUBLIC - E95_PUBLIC
RANDOM_SEED = 20260529
RANDOM_SCENARIOS_PER_MASK_GAMMA = 120

FILES = {
    "mixmin": "submission_mixmin_0c916bb4.csv",
    "failed_e72": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "e85": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e86": "submission_e86_e85_consensus_a3f7c96f.csv",
    "noq2": "submission_e87_noq2_source_consensus_a85c4e39.csv",
    "e90": "submission_e90_e72pareto_28925de5.csv",
    "e89": "submission_e89_e72decontam_00d7807f.csv",
    "e95": "submission_e95_hardtail_541e3973.csv",
}

LIVE_CANDIDATES = ["e85", "e86", "noq2", "e90", "e89", "e95"]
REFERENCE_CANDIDATES = ["mixmin", "failed_e72"]
ALL_CANDIDATES = REFERENCE_CANDIDATES + LIVE_CANDIDATES

SCENARIO_OUT = OUT / "e96_public_miss_budget_scenarios.csv"
SUMMARY_OUT = OUT / "e96_public_miss_budget_summary.csv"
MASK_SUMMARY_OUT = OUT / "e96_public_miss_budget_mask_summary.csv"
REPORT_OUT = OUT / "e96_public_miss_budget_report.md"


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    rows: list[list[str]] = []
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
        rows.append(row)
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def adverse_delta_for_e72_direction(
    pred: np.ndarray,
    base: np.ndarray,
    wrong_is_zero: np.ndarray,
    wrong_is_one: np.ndarray,
) -> np.ndarray:
    d0, d1 = e94.hard_loss_deltas(pred, base)
    return np.where(wrong_is_zero, d0, np.where(wrong_is_one, d1, 0.0))


def target_mask(n_rows: int, names: list[str]) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for name in names:
        mask[:, TARGETS.index(name)] = True
    return mask


def high_positive_mask(values: np.ndarray, q: float) -> np.ndarray:
    positive = values[values > 1.0e-12]
    if len(positive) == 0:
        return np.zeros_like(values, dtype=bool)
    cut = float(np.quantile(positive, q))
    return values >= cut


def build_masks(preds: dict[str, np.ndarray], e72_pos: np.ndarray, e72_delta: np.ndarray) -> dict[str, np.ndarray]:
    n_rows = e72_pos.shape[0]
    one = np.ones_like(e72_pos, dtype=bool)
    e95_fallback = np.abs(logit(preds["e95"]) - logit(preds["e86"])) > 1.0e-9
    e95_moved = np.abs(logit(preds["e95"]) - logit(preds["mixmin"])) > 1.0e-9
    e86_moved = np.abs(logit(preds["e86"]) - logit(preds["mixmin"])) > 1.0e-9
    e90_moved = np.abs(logit(preds["e90"]) - logit(preds["mixmin"])) > 1.0e-9
    e89_moved = np.abs(logit(preds["e89"]) - logit(preds["mixmin"])) > 1.0e-9
    e72_top20 = high_positive_mask(np.abs(e72_delta), 0.80)
    e72_top50_hard = high_positive_mask(e72_pos, 0.50)

    masks = {
        "all": one,
        "q2": target_mask(n_rows, ["Q2"]),
        "s1": target_mask(n_rows, ["S1"]),
        "s2": target_mask(n_rows, ["S2"]),
        "s3": target_mask(n_rows, ["S3"]),
        "q2s3": target_mask(n_rows, ["Q2", "S3"]),
        "s1s2s3": target_mask(n_rows, ["S1", "S2", "S3"]),
        "live_q2s1s2s3": target_mask(n_rows, ["Q2", "S1", "S2", "S3"]),
        "e72_active": np.abs(e72_delta) > 1.0e-9,
        "e72_top20_abs": e72_top20,
        "e72_top50_hard": e72_top50_hard,
        "e95_fallback_cells": e95_fallback,
        "e95_nonfallback_cells": ~e95_fallback,
        "e95_fallback_q2s3": e95_fallback & target_mask(n_rows, ["Q2", "S3"]),
        "e95_fallback_s1s2s3": e95_fallback & target_mask(n_rows, ["S1", "S2", "S3"]),
        "e95_moved_vs_mixmin": e95_moved,
        "e86_moved_vs_mixmin": e86_moved,
        "e90_moved_vs_mixmin": e90_moved,
        "e89_moved_vs_mixmin": e89_moved,
    }
    return {name: mask.reshape(-1) for name, mask in masks.items()}


def take_budget(order: np.ndarray, e72_pos_flat: np.ndarray, budget_sum: float) -> tuple[np.ndarray, float, float, int]:
    weights = np.zeros_like(e72_pos_flat, dtype=np.float64)
    total = 0.0
    fractional_cells = 0.0
    full_cells = 0
    for idx in order:
        value = float(e72_pos_flat[idx])
        if value <= 1.0e-18:
            continue
        remaining = budget_sum - total
        if remaining <= 1.0e-14:
            break
        take = min(1.0, remaining / value)
        weights[idx] = take
        total += take * value
        fractional_cells += take
        if take >= 1.0 - 1.0e-12:
            full_cells += 1
        if total >= budget_sum - 1.0e-12:
            break
    return weights, total, fractional_cells, full_cells


def deterministic_order(indices: np.ndarray, e72_pos_flat: np.ndarray, mode: str) -> np.ndarray:
    values = e72_pos_flat[indices]
    if mode == "top":
        return indices[np.argsort(-values, kind="mergesort")]
    if mode == "bottom":
        return indices[np.argsort(values, kind="mergesort")]
    if mode == "median":
        median = float(np.median(values))
        return indices[np.argsort(np.abs(values - median), kind="mergesort")]
    raise KeyError(mode)


def weighted_random_order(indices: np.ndarray, e72_pos_flat: np.ndarray, gamma: float, rng: np.random.Generator) -> np.ndarray:
    values = np.maximum(e72_pos_flat[indices], 1.0e-18)
    weights = values ** gamma
    probs = weights / float(np.sum(weights))
    return rng.choice(indices, size=len(indices), replace=False, p=probs)


def add_scenario(
    *,
    scenario_id: str,
    family: str,
    mask_name: str,
    order_name: str,
    gamma: float | None,
    order: np.ndarray,
    mask: np.ndarray,
    e72_pos_flat: np.ndarray,
    adverse_flat: dict[str, np.ndarray],
    budget_sum: float,
    n_cells: int,
    meta_rows: list[dict[str, Any]],
    long_rows: list[dict[str, Any]],
) -> None:
    weights, achieved, fractional_cells, full_cells = take_budget(order, e72_pos_flat, budget_sum)
    positive_cells_available = int(np.sum(mask & (e72_pos_flat > 1.0e-12)))
    complete = achieved >= budget_sum * 0.999999
    meta_rows.append(
        {
            "scenario_id": scenario_id,
            "family": family,
            "mask_name": mask_name,
            "order_name": order_name,
            "gamma": gamma,
            "complete_budget": complete,
            "achieved_e72_delta": achieved / n_cells,
            "target_e72_delta": budget_sum / n_cells,
            "budget_coverage": achieved / budget_sum if budget_sum > 0 else np.nan,
            "positive_cells_available": positive_cells_available,
            "selected_full_cells": full_cells,
            "selected_fractional_cells": fractional_cells,
        }
    )
    for candidate, arr in adverse_flat.items():
        long_rows.append(
            {
                "scenario_id": scenario_id,
                "candidate": candidate,
                "delta_vs_mixmin": float(np.sum(weights * arr) / n_cells),
            }
        )


def build_scenarios(e72_pos_flat: np.ndarray, masks: dict[str, np.ndarray], adverse_flat: dict[str, np.ndarray], budget_sum: float, n_cells: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    meta_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    scenario_count = 0

    deterministic_masks = [
        "all",
        "q2",
        "s1",
        "s2",
        "s3",
        "q2s3",
        "s1s2s3",
        "live_q2s1s2s3",
        "e72_top20_abs",
        "e72_top50_hard",
        "e95_fallback_cells",
        "e95_nonfallback_cells",
        "e95_fallback_q2s3",
        "e95_fallback_s1s2s3",
        "e95_moved_vs_mixmin",
        "e86_moved_vs_mixmin",
        "e90_moved_vs_mixmin",
        "e89_moved_vs_mixmin",
    ]
    for mask_name in deterministic_masks:
        mask = masks[mask_name]
        indices = np.flatnonzero(mask & (e72_pos_flat > 1.0e-12))
        if len(indices) == 0:
            continue
        for mode in ["top", "bottom", "median"]:
            order = deterministic_order(indices, e72_pos_flat, mode)
            scenario_count += 1
            add_scenario(
                scenario_id=f"d{scenario_count:04d}",
                family="deterministic",
                mask_name=mask_name,
                order_name=mode,
                gamma=None,
                order=order,
                mask=mask,
                e72_pos_flat=e72_pos_flat,
                adverse_flat=adverse_flat,
                budget_sum=budget_sum,
                n_cells=n_cells,
                meta_rows=meta_rows,
                long_rows=long_rows,
            )

    rng = np.random.default_rng(RANDOM_SEED)
    random_masks = [
        "all",
        "q2s3",
        "s1s2s3",
        "live_q2s1s2s3",
        "e72_top50_hard",
        "e95_fallback_cells",
        "e95_moved_vs_mixmin",
        "e86_moved_vs_mixmin",
    ]
    for mask_name in random_masks:
        mask = masks[mask_name]
        indices = np.flatnonzero(mask & (e72_pos_flat > 1.0e-12))
        if len(indices) == 0:
            continue
        for gamma in [0.0, 0.5, 1.0, 2.0]:
            for rep in range(RANDOM_SCENARIOS_PER_MASK_GAMMA):
                order = weighted_random_order(indices, e72_pos_flat, gamma, rng)
                scenario_count += 1
                add_scenario(
                    scenario_id=f"r{scenario_count:04d}",
                    family="random_weighted",
                    mask_name=mask_name,
                    order_name=f"weighted_gamma_{gamma:g}_rep_{rep:03d}",
                    gamma=gamma,
                    order=order,
                    mask=mask,
                    e72_pos_flat=e72_pos_flat,
                    adverse_flat=adverse_flat,
                    budget_sum=budget_sum,
                    n_cells=n_cells,
                    meta_rows=meta_rows,
                    long_rows=long_rows,
                )

    return pd.DataFrame(meta_rows), pd.DataFrame(long_rows)


def candidate_summary(meta: pd.DataFrame, long: pd.DataFrame) -> pd.DataFrame:
    complete_ids = meta.loc[meta["complete_budget"], "scenario_id"]
    complete = long[long["scenario_id"].isin(complete_ids)]
    wide = complete.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    live = [c for c in LIVE_CANDIDATES if c in wide.columns]
    winners = wide[live].idxmin(axis=1)
    rows: list[dict[str, Any]] = []
    for candidate in ALL_CANDIDATES:
        if candidate not in wide.columns:
            continue
        delta = wide[candidate]
        row: dict[str, Any] = {
            "candidate": candidate,
            "complete_scenarios": int(delta.notna().sum()),
            "mean_delta": float(delta.mean()),
            "median_delta": float(delta.median()),
            "p10_delta": float(delta.quantile(0.10)),
            "p90_delta": float(delta.quantile(0.90)),
            "p95_delta": float(delta.quantile(0.95)),
            "max_delta": float(delta.max()),
            "min_delta": float(delta.min()),
            "improve_vs_mixmin_rate": float(np.mean(delta < -1.0e-12)),
            "beat_failed_e72_rate": float(np.mean(delta < wide["failed_e72"] - 1.0e-12)),
            "win_rate_live": float(np.mean(winners == candidate)) if candidate in live else np.nan,
        }
        for ref in ["e85", "e86", "noq2", "e90", "e89", "e95"]:
            if ref in wide.columns:
                row[f"mean_margin_vs_{ref}"] = float((delta - wide[ref]).mean())
                row[f"beat_{ref}_rate"] = float(np.mean(delta < wide[ref] - 1.0e-12))
        rows.append(row)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["rank_by_mean"] = out["mean_delta"].rank(method="min")
        out["rank_by_p95"] = out["p95_delta"].rank(method="min")
        out["rank_by_win"] = (-out["win_rate_live"].fillna(-1)).rank(method="min")
    return out


def mask_summary(meta: pd.DataFrame, long: pd.DataFrame) -> pd.DataFrame:
    complete_ids = meta.loc[meta["complete_budget"], "scenario_id"]
    complete_meta = meta[meta["scenario_id"].isin(complete_ids)].copy()
    complete = long[long["scenario_id"].isin(complete_ids)]
    wide = complete.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    live = [c for c in LIVE_CANDIDATES if c in wide.columns]
    detail = complete_meta.set_index("scenario_id").join(wide[live])
    detail["winner"] = wide[live].idxmin(axis=1)
    detail["e95_rank_live"] = wide[live].rank(axis=1, method="min")["e95"]
    detail["e95_minus_e89"] = wide["e95"] - wide["e89"]
    detail["e95_minus_e90"] = wide["e95"] - wide["e90"]
    detail["e95_minus_e86"] = wide["e95"] - wide["e86"]
    rows: list[dict[str, Any]] = []
    for (mask_name, family), group in detail.groupby(["mask_name", "family"], dropna=False):
        row: dict[str, Any] = {
            "mask_name": mask_name,
            "family": family,
            "complete_scenarios": int(len(group)),
            "winner_mode": str(group["winner"].mode().iloc[0]),
            "e95_win_rate": float(np.mean(group["winner"] == "e95")),
            "e95_rank_mean": float(group["e95_rank_live"].mean()),
            "e95_minus_e89_mean": float(group["e95_minus_e89"].mean()),
            "e95_minus_e90_mean": float(group["e95_minus_e90"].mean()),
            "e95_minus_e86_mean": float(group["e95_minus_e86"].mean()),
        }
        for candidate in live:
            row[f"{candidate}_mean_delta"] = float(group[candidate].mean())
            row[f"{candidate}_win_count"] = int(np.sum(group["winner"] == candidate))
        rows.append(row)
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["mask_name", "family"]).reset_index(drop=True)
    return out


def top_e95_failure_cases(meta: pd.DataFrame, long: pd.DataFrame) -> pd.DataFrame:
    complete_ids = meta.loc[meta["complete_budget"], "scenario_id"]
    complete = long[long["scenario_id"].isin(complete_ids)]
    wide = complete.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")
    meta_indexed = meta.set_index("scenario_id")
    view = meta_indexed.join(
        pd.DataFrame(
            {
                "e95": wide["e95"],
                "e89": wide["e89"],
                "e90": wide["e90"],
                "e86": wide["e86"],
                "e95_minus_e89": wide["e95"] - wide["e89"],
                "e95_minus_e90": wide["e95"] - wide["e90"],
                "e95_minus_e86": wide["e95"] - wide["e86"],
            }
        )
    )
    cols = [
        "scenario_id",
        "family",
        "mask_name",
        "order_name",
        "gamma",
        "selected_fractional_cells",
        "e95",
        "e89",
        "e90",
        "e86",
        "e95_minus_e89",
        "e95_minus_e90",
    ]
    return view.reset_index().sort_values("e95_minus_e89", ascending=False)[cols].head(12)


def write_report(
    meta: pd.DataFrame,
    long: pd.DataFrame,
    summary: pd.DataFrame,
    mask_sum: pd.DataFrame,
    n_cells: int,
) -> None:
    complete_count = int(meta["complete_budget"].sum())
    total_count = int(len(meta))
    live_summary = summary[summary["candidate"].isin(LIVE_CANDIDATES)].copy()
    live_summary = live_summary.sort_values(["p95_delta", "mean_delta"]).reset_index(drop=True)

    e95 = summary[summary["candidate"].eq("e95")].iloc[0]
    e89 = summary[summary["candidate"].eq("e89")].iloc[0]
    e90 = summary[summary["candidate"].eq("e90")].iloc[0]
    e86 = summary[summary["candidate"].eq("e86")].iloc[0]

    if float(e95["p95_delta"]) <= float(e89["p95_delta"]) and float(e95["mean_delta"]) <= float(e89["mean_delta"]):
        e95_read = "E95는 E89보다 평균과 p95 tail-risk가 낮다. hard-tail fallback이 E89의 단순 E72-cell fallback보다 넓은 조건부 세계에서 더 낫다는 쪽이다."
    elif float(e95["beat_e89_rate"]) > 0.50:
        e95_read = "E95는 E89를 과반 scenario에서 이기지만 p95/mean 중 하나는 아직 열세다. E95는 narrow hard-tail sensor로 유지하되 universal lower-risk라고 부르기는 어렵다."
    else:
        e95_read = "E95는 E89를 과반 scenario에서 이기지 못한다. E95 priority는 hard-tail localization 실험으로만 남고, lower-downside 후보는 E89/E85 쪽이 더 설득력 있다."

    if float(e86["mean_delta"]) < float(e95["mean_delta"]) and float(e86["p95_delta"]) > float(e95["p95_delta"]):
        upside_read = "E86은 평균 upside를 보존하지만 p95 risk가 크다. 이는 maximum-upside sensor와 lower-downside sensor를 계속 분리해야 한다는 신호다."
    elif float(e86["mean_delta"]) <= float(e95["mean_delta"]) and float(e86["p95_delta"]) <= float(e95["p95_delta"]):
        upside_read = "E86이 평균과 p95 모두에서 E95를 이긴다. 이 경우 hard-tail gate가 구조를 과도하게 버렸을 가능성이 커진다."
    else:
        upside_read = "E95는 E86의 tail-risk를 줄이지만 평균 구조 edge도 일부 포기한다. 이는 E95의 제출 의도가 upside가 아니라 downside 센서임을 재확인한다."

    top_failure = top_e95_failure_cases(meta, long)
    mask_view = mask_sum.sort_values(["e95_rank_mean", "e95_minus_e89_mean"]).head(18)

    report = f"""# E96 Public-Miss Budget Tail Scenarios

## Question

E72 public miss `+{E72_PUBLIC_MISS:.10f}`를 하나의 LogLoss budget으로 고정했을 때, 그 budget이 가능한 E72-adverse hard-label tail 어디에서 발생했느냐에 따라 E95/E89/E90/E86의 상대 risk가 어떻게 바뀌는가?

이 실험은 public label을 맞추지 않는다. 관측값은 E72의 public miss 크기 하나뿐이고, 각 scenario는 그 miss를 설명할 수 있는 hard-tail cell 집합을 다르게 배치한다.

## Method

- base: `submission_mixmin_0c916bb4.csv`
- failed sensor: `submission_e72_topabs50_q2s3_gate_4e48cba2.csv`
- budget: `E72 - mixmin = {E72_PUBLIC_MISS:.10f}`
- evaluated cells: `{n_cells}` test-target cells (`rows x 7 targets`)
- candidates scored per scenario: `{len(long) // max(len(meta), 1) if len(meta) else 0}`
- max full selected cells in a complete budget scenario: `{int(meta['selected_full_cells'].max())}`
- scenarios: `{total_count}` total, `{complete_count}` complete-budget
- deterministic orders: top, bottom, median E72-adverse hard-tail cells
- random orders: weighted permutations with gamma `0, 0.5, 1, 2`

Each candidate score is candidate-minus-mixmin LogLoss on the same selected E72-adverse hard labels. For complete scenarios, failed E72 reconstructs the observed public miss by construction.

## Candidate Summary

Sorted by p95 conditional tail delta.

{md_table(live_summary[[
    "candidate",
    "mean_delta",
    "median_delta",
    "p90_delta",
    "p95_delta",
    "max_delta",
    "improve_vs_mixmin_rate",
    "beat_failed_e72_rate",
    "beat_e89_rate",
    "beat_e90_rate",
    "beat_e86_rate",
    "win_rate_live",
]])}

## Mask / Family Summary

Lowest E95 rank families first.

{md_table(mask_view[[
    "mask_name",
    "family",
    "complete_scenarios",
    "winner_mode",
    "e95_win_rate",
    "e95_rank_mean",
    "e95_minus_e89_mean",
    "e95_minus_e90_mean",
    "e95_minus_e86_mean",
]])}

## Where E95 Loses Most To E89

{md_table(top_failure)}

## Interpretation

- {e95_read}
- {upside_read}
- E90 remains the row-coherent middle hypothesis: summary mean `{float(e90['mean_delta']):.9f}`, p95 `{float(e90['p95_delta']):.9f}`.
- E89 remains the direct E72-cell fallback baseline: summary mean `{float(e89['mean_delta']):.9f}`, p95 `{float(e89['p95_delta']):.9f}`.

## Decision

E96 does not create a new submission file. It is a conditional sensor audit for the post-E72 queue.

Submission reading:

- If the next public slot should minimize E72-style hard-tail downside, prefer whichever of E95/E89 has the lower p95 and mean in this report.
- If the next public slot should test whether hard-tail gating is over-penalizing useful structure, E86 is still the maximum-upside contrast.
- If public later rejects E95 but accepts E90/E86, H90 weakens: the hard-tail proxy was over-localized or public tail was not E72-adverse.
- If public accepts E95 while rejecting E86/E90, H90 strengthens: public loss is dominated by localized E72-adverse hard-tail cells rather than broad soft representation health.

## Post-E97 Public Update

E95 was submitted after this stress and scored public `{E95_PUBLIC:.10f}`, improving over mixmin by `{E95_PUBLIC_GAIN:.10f}`. That validates the E95 side of the E96 ranking as public-positive, while the small gain means this is still a localized hard-tail repair rather than hidden block-rate recovery.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(FILES["mixmin"]).sort_values(KEYS).reset_index(drop=True)
    preds = {name: load_pred(file_name, sample) for name, file_name in FILES.items()}
    base = preds["mixmin"]
    e72 = preds["failed_e72"]

    e72_delta = logit(e72) - logit(base)
    wrong_is_zero = e72_delta > 1.0e-9
    wrong_is_one = e72_delta < -1.0e-9
    adverse = {
        name: adverse_delta_for_e72_direction(pred, base, wrong_is_zero, wrong_is_one)
        for name, pred in preds.items()
    }
    e72_pos = np.maximum(adverse["failed_e72"], 0.0)
    n_cells = int(base.size)
    budget_sum = float(E72_PUBLIC_MISS * n_cells)

    masks = build_masks(preds, e72_pos, e72_delta)
    adverse_flat = {name: arr.reshape(-1) for name, arr in adverse.items()}
    meta, long = build_scenarios(
        e72_pos.reshape(-1),
        masks,
        adverse_flat,
        budget_sum,
        n_cells,
    )
    summary = candidate_summary(meta, long)
    mask_sum = mask_summary(meta, long)

    long_with_meta = long.merge(meta, on="scenario_id", how="left")
    long_with_meta.to_csv(SCENARIO_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    mask_sum.to_csv(MASK_SUMMARY_OUT, index=False)
    write_report(meta, long, summary, mask_sum, n_cells)

    print(f"wrote {SCENARIO_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {MASK_SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")
    print(f"complete scenarios: {int(meta['complete_budget'].sum())}/{len(meta)}")
    print(summary[summary['candidate'].isin(LIVE_CANDIDATES)].sort_values(['p95_delta', 'mean_delta']).to_string(index=False))


if __name__ == "__main__":
    main()
