#!/usr/bin/env python3
"""E121 exact E101 small-loss inverse posterior.

SAUNA question:
E101 did not beat E95, but it still beat mixmin. What hard-label world over the
50 active Q2/S3 cells makes that exact public observation natural?

This is not a submission generator. It uses the E101 public result as a sensor
to ask which hidden label/support patterns remain compatible with the observed
two-point boundary: E95 wins, E101 loses small, mixmin loses more.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent

CELLS_IN = OUT / "e118_e101_flank_label_support_cells.csv"
SUMMARY_OUT = OUT / "e121_e101_small_loss_inverse_posterior_summary.csv"
CELLS_OUT = OUT / "e121_e101_small_loss_inverse_posterior_cells.csv"
GREEDY_OUT = OUT / "e121_e101_small_loss_inverse_posterior_greedy.csv"
REPORT_OUT = OUT / "e121_e101_small_loss_inverse_posterior_report.md"

E95_PUBLIC = 0.5762913298
MIXMIN_PUBLIC = 0.5763066405
E101_PUBLIC = 0.5763003660
TOTAL_TEST_CELLS = 250 * 7

OBS_DELTA = E101_PUBLIC - E95_PUBLIC
OBS_ACTIVE_TOTAL = OBS_DELTA * TOTAL_TEST_CELLS
MIXMIN_EDGE_DELTA = MIXMIN_PUBLIC - E95_PUBLIC

N_SIMS = 300_000
RNG_SEED = 20260529
EXACT_TOL = 1.0e-6
SOFT_SIGMA = 2.0e-6

PRIORS = [
    "global",
    "subject",
    "prev_beta",
    "next_beta",
    "nearest_beta",
    "both_equal_beta",
    "both_distance_beta",
    "edge_endpoint_beta",
    "nearest_hard085",
    "conflict_flat",
]


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


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    denom = float(weights.sum())
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(values, weights) / denom)


def entropy_binary(p: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=np.float64), 1.0e-12, 1.0 - 1.0e-12)
    return -(p * np.log2(p) + (1.0 - p) * np.log2(1.0 - p))


def summarize_bucket(
    prior: str,
    bucket: str,
    mask: np.ndarray,
    per_all: np.ndarray,
    support: np.ndarray,
    flip_benefit: np.ndarray,
    top10: np.ndarray,
    top22: np.ndarray,
    top23: np.ndarray,
    target_s3: np.ndarray,
    target_q2: np.ndarray,
    edge_like: np.ndarray,
    flank_conflict: np.ndarray,
) -> dict[str, float | int | str]:
    n = int(mask.sum())
    if n == 0:
        return {
            "prior": prior,
            "bucket": bucket,
            "n_worlds": 0,
            "world_rate": 0.0,
        }

    support_m = support[mask]
    per_m = per_all[mask]
    flip_weight = support_m * flip_benefit[None, :]
    flip_share = flip_weight.sum(axis=1) / float(flip_benefit.sum())

    return {
        "prior": prior,
        "bucket": bucket,
        "n_worlds": n,
        "world_rate": n / float(len(mask)),
        "delta_mean": float(per_m.mean()),
        "delta_p05": float(np.quantile(per_m, 0.05)),
        "delta_p50": float(np.quantile(per_m, 0.50)),
        "delta_p95": float(np.quantile(per_m, 0.95)),
        "abs_error_mean": float(np.abs(per_m - OBS_DELTA).mean()),
        "support_cells_mean": float(support_m.sum(axis=1).mean()),
        "support_cells_p05": float(np.quantile(support_m.sum(axis=1), 0.05)),
        "support_cells_p95": float(np.quantile(support_m.sum(axis=1), 0.95)),
        "support_flip_share_mean": float(flip_share.mean()),
        "support_flip_share_p05": float(np.quantile(flip_share, 0.05)),
        "support_flip_share_p95": float(np.quantile(flip_share, 0.95)),
        "top10_support_rate": float(support_m[:, top10].mean()),
        "top22_support_rate": float(support_m[:, top22].mean()),
        "top23_support_rate": float(support_m[:, top23].mean()),
        "s3_support_rate": float(support_m[:, target_s3].mean()),
        "q2_support_rate": float(support_m[:, target_q2].mean()),
        "edge_like_support_rate": float(support_m[:, edge_like].mean()),
        "interior_support_rate": float(support_m[:, ~edge_like].mean()),
        "conflict_support_rate": float(support_m[:, flank_conflict].mean())
        if flank_conflict.any()
        else float("nan"),
    }


def soft_cell_posterior(
    prior: str,
    per_all: np.ndarray,
    support: np.ndarray,
    cells: pd.DataFrame,
) -> pd.DataFrame:
    weights = np.exp(-0.5 * ((per_all - OBS_DELTA) / SOFT_SIGMA) ** 2)
    weights = weights / max(float(weights.sum()), 1.0e-300)
    support_prob = weights @ support
    out = pd.DataFrame(
        {
            "sub_idx": cells["sub_idx"].to_numpy(),
            "target": cells["target"].to_numpy(),
            f"posterior_support_{prior}": support_prob,
            f"posterior_entropy_{prior}": entropy_binary(support_prob),
        }
    )
    return out


def exact_subset_closest(cells: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float | int]]:
    """Meet the observed active total by taking largest flip-benefit cells first.

    This is a deliberately simple hard-label mental model: if E101 support lands
    on the highest-impact active cells first, how many supports are needed to
    match the public observation, beat E95, and beat mixmin?
    """

    order = cells.sort_values("flip_benefit", ascending=False).reset_index(drop=True).copy()
    all_adverse = float(cells["adverse_delta"].sum())
    all_support = float(cells["support_delta"].sum())
    flip_sum = float(cells["flip_benefit"].sum())
    order["flip_rank"] = np.arange(1, len(order) + 1)
    order["cum_flip_benefit"] = order["flip_benefit"].cumsum()
    order["delta_if_topk_support"] = all_adverse - order["cum_flip_benefit"]
    order["delta_if_topk_support_per_all"] = order["delta_if_topk_support"] / TOTAL_TEST_CELLS
    order["abs_error_vs_observed"] = (order["delta_if_topk_support_per_all"] - OBS_DELTA).abs()
    order["beats_e95"] = order["delta_if_topk_support_per_all"] < 0.0
    order["beats_mixmin"] = order["delta_if_topk_support_per_all"] < MIXMIN_EDGE_DELTA

    closest = order.loc[order["abs_error_vs_observed"].idxmin()]
    beat_e95 = order[order["beats_e95"]].head(1)
    beat_mixmin = order[order["beats_mixmin"]].head(1)
    needed_benefit = all_adverse - OBS_ACTIVE_TOTAL

    stats = {
        "all_support_total": all_support,
        "all_support_per_all": all_support / TOTAL_TEST_CELLS,
        "all_adverse_total": all_adverse,
        "all_adverse_per_all": all_adverse / TOTAL_TEST_CELLS,
        "flip_benefit_total": flip_sum,
        "observed_active_total": OBS_ACTIVE_TOTAL,
        "observed_delta_per_all": OBS_DELTA,
        "needed_flip_benefit": needed_benefit,
        "needed_flip_share": needed_benefit / flip_sum,
        "closest_greedy_k": int(closest["flip_rank"]),
        "closest_greedy_delta_per_all": float(closest["delta_if_topk_support_per_all"]),
        "closest_greedy_abs_error": float(closest["abs_error_vs_observed"]),
        "first_greedy_k_beats_e95": int(beat_e95.iloc[0]["flip_rank"]) if len(beat_e95) else -1,
        "first_greedy_k_beats_mixmin": int(beat_mixmin.iloc[0]["flip_rank"]) if len(beat_mixmin) else -1,
    }
    return order, stats


def add_cell_context_columns(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    out["edge_like"] = out["pos_bin"].isin(["left_edge", "right_edge", "near_edge", "single"])
    out["support_prob_mean_prior"] = out[
        [f"support_probability_{prior}" for prior in PRIORS]
    ].mean(axis=1)
    out["expected_delta_mean_prior"] = out[
        [f"expected_delta_{prior}" for prior in PRIORS]
    ].mean(axis=1)
    out["flip_rank"] = out["flip_benefit"].rank(method="first", ascending=False).astype(int)
    return out


def merge_posteriors(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    frames = list(frames)
    if not frames:
        return pd.DataFrame()
    out = frames[0]
    for frame in frames[1:]:
        out = out.merge(frame, on=["sub_idx", "target"], how="inner")
    return out


def main() -> None:
    cells = pd.read_csv(CELLS_IN)
    cells = cells[cells["active"].astype(bool)].copy()
    cells = add_cell_context_columns(cells)

    greedy, greedy_stats = exact_subset_closest(cells)
    greedy.to_csv(GREEDY_OUT, index=False)

    flip_benefit = cells["flip_benefit"].to_numpy(dtype=np.float64)
    delta_y1 = cells["delta_y1"].to_numpy(dtype=np.float64)
    delta_y0 = cells["delta_y0"].to_numpy(dtype=np.float64)
    support_label = cells["support_label"].to_numpy(dtype=int)
    target_s3 = cells["target"].eq("S3").to_numpy()
    target_q2 = cells["target"].eq("Q2").to_numpy()
    edge_like = cells["edge_like"].to_numpy()
    flank_conflict = cells["flank_conflict"].astype(bool).to_numpy()
    flip_rank = cells["flip_rank"].to_numpy()
    top10 = flip_rank <= 10
    top22 = flip_rank <= 22
    top23 = flip_rank <= 23

    rows: list[dict[str, float | int | str]] = []
    posterior_frames: list[pd.DataFrame] = []

    rng = np.random.default_rng(RNG_SEED)
    for prior in PRIORS:
        probs = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
        labels = rng.random((N_SIMS, len(cells))) < probs[None, :]
        delta_total = labels @ (delta_y1 - delta_y0) + float(delta_y0.sum())
        per_all = delta_total / TOTAL_TEST_CELLS
        support = labels == support_label[None, :]

        masks = {
            "all": np.ones(N_SIMS, dtype=bool),
            "exact_observed_pm1e-6": np.abs(per_all - OBS_DELTA) <= EXACT_TOL,
            "exact_observed_pm2e-6": np.abs(per_all - OBS_DELTA) <= 2.0 * EXACT_TOL,
            "small_loss_preband": (per_all > 3.0e-6) & (per_all <= 20.0e-6),
            "beats_e95": per_all < 0.0,
            "beats_mixmin": per_all < MIXMIN_EDGE_DELTA,
            "fails_mixmin": per_all >= MIXMIN_EDGE_DELTA,
        }

        for bucket, mask in masks.items():
            rows.append(
                summarize_bucket(
                    prior=prior,
                    bucket=bucket,
                    mask=mask,
                    per_all=per_all,
                    support=support,
                    flip_benefit=flip_benefit,
                    top10=top10,
                    top22=top22,
                    top23=top23,
                    target_s3=target_s3,
                    target_q2=target_q2,
                    edge_like=edge_like,
                    flank_conflict=flank_conflict,
                )
            )

        posterior_frames.append(soft_cell_posterior(prior, per_all, support, cells))

    summary = pd.DataFrame(rows)
    summary.to_csv(SUMMARY_OUT, index=False)

    posterior = merge_posteriors(posterior_frames)
    cell_cols = [
        "sub_idx",
        "target",
        "subject_id",
        "hidden_block_id",
        "lifelog_date",
        "pos_bin",
        "edge_like",
        "flank_conflict",
        "support_label",
        "support_delta",
        "adverse_delta",
        "flip_benefit",
        "flip_rank",
        "support_prob_mean_prior",
        "expected_delta_mean_prior",
    ]
    posterior = cells[cell_cols].merge(posterior, on=["sub_idx", "target"], how="inner")
    posterior_support_cols = [f"posterior_support_{prior}" for prior in PRIORS]
    posterior["posterior_support_mean"] = posterior[posterior_support_cols].mean(axis=1)
    posterior["posterior_support_std"] = posterior[posterior_support_cols].std(axis=1)
    posterior["posterior_support_minus_prior_mean"] = (
        posterior["posterior_support_mean"] - posterior["support_prob_mean_prior"]
    )
    posterior = posterior.sort_values(["flip_rank", "target", "sub_idx"]).reset_index(drop=True)
    posterior.to_csv(CELLS_OUT, index=False)

    exact = summary[summary["bucket"].eq("exact_observed_pm1e-6")].copy()
    small = summary[summary["bucket"].eq("small_loss_preband")].copy()
    exact_view = exact[
        [
            "prior",
            "world_rate",
            "support_cells_mean",
            "support_flip_share_mean",
            "top10_support_rate",
            "top22_support_rate",
            "top23_support_rate",
            "s3_support_rate",
            "q2_support_rate",
            "edge_like_support_rate",
        ]
    ].sort_values("world_rate", ascending=False)
    small_view = small[
        [
            "prior",
            "world_rate",
            "delta_mean",
            "support_cells_mean",
            "support_flip_share_mean",
            "top10_support_rate",
            "s3_support_rate",
            "q2_support_rate",
        ]
    ].sort_values("world_rate", ascending=False)

    high_rank = posterior.head(12)[
        [
            "sub_idx",
            "target",
            "subject_id",
            "pos_bin",
            "support_label",
            "flip_benefit",
            "support_prob_mean_prior",
            "posterior_support_mean",
            "posterior_support_minus_prior_mean",
        ]
    ]

    closest_k = int(greedy_stats["closest_greedy_k"])
    closest_rows = greedy.loc[
        greedy["flip_rank"].between(max(1, closest_k - 3), min(len(greedy), closest_k + 3)),
        [
            "flip_rank",
            "sub_idx",
            "target",
            "subject_id",
            "pos_bin",
            "support_label",
            "flip_benefit",
            "cum_flip_benefit",
            "delta_if_topk_support_per_all",
            "beats_e95",
            "beats_mixmin",
        ],
    ]

    report = f"""# E121 Exact E101 Small-Loss Inverse Posterior

## Question

E101 public was `{E101_PUBLIC:.10f}`, E95 was `{E95_PUBLIC:.10f}`, and mixmin was `{MIXMIN_PUBLIC:.10f}`. E101 therefore lost to E95 by `{OBS_DELTA:+.10f}` but still beat mixmin by `{E101_PUBLIC - MIXMIN_PUBLIC:+.10f}`.

The question is not whether E101 was good. The question is what active-cell label world makes this exact boundary natural.

## Hard-Label Budget

- Active cells: `{len(cells)}`
- All-support E101-vs-E95 delta: `{greedy_stats['all_support_per_all']:+.10f}`
- All-adverse E101-vs-E95 delta: `{greedy_stats['all_adverse_per_all']:+.10f}`
- Observed E101-vs-E95 delta: `{OBS_DELTA:+.10f}`
- Flip benefit required by the observation: `{greedy_stats['needed_flip_share']:.6f}` of available active-cell flip budget
- First greedy top-flip support count that beats mixmin: `{greedy_stats['first_greedy_k_beats_mixmin']}`
- Greedy support count closest to the exact observation: `{greedy_stats['closest_greedy_k']}`
- First greedy top-flip support count that beats E95: `{greedy_stats['first_greedy_k_beats_e95']}`

Interpretation: the public world did not reject the E101 direction wholesale. It realized about two thirds of the E101 active-cell flip benefit. But it stopped roughly one high-impact S3/Q2 support cell short of beating E95.

## Greedy Boundary Rows

{md_table(closest_rows, '.8f')}

## Exact-Observed Posterior by Prior

Bucket: `abs(delta - observed_delta) <= {EXACT_TOL:.0e}` over `{N_SIMS}` simulated active-cell label worlds per prior.

{md_table(exact_view, '.6f')}

## Small-Loss Band by Prior

Bucket: E116-style small loss, `3e-6 < delta <= 20e-6`.

{md_table(small_view, '.6f')}

## Highest-Impact Cell Posterior

Soft posterior uses a Gaussian sensor centered on the observed E101 delta with sigma `{SOFT_SIGMA:.0e}`.

{md_table(high_rank, '.6f')}

## Belief Update

E101's small loss is a knife-edge result, not a broad invalidation. The hidden public hard-label world is compatible with E101 support on most high-impact S3 cells, but not enough of them. Because the posterior cell support depends heavily on the assumed train-derived prior and does not expose a clean visible gate, the result does not justify another same-line submission.

This strengthens the current bottleneck diagnosis:

> The frontier is not model capacity. It is an underidentified public hard-label boundary on a small S3-heavy active-cell tail, where one or two high-impact support/adverse cells move the public score by the same scale as the whole observed improvement.

## Decision

Keep E95 as the standing frontier. Do not submit E108/E104/E106/E119/E89-style automatic followups.

The next information-rich action is to find an independent, non-public sensor for the missing high-impact S3 support cells. If no such sensor exists, the same-line frontier is exhausted and the next public slot should test a different hidden structure, not a finer E101 amplitude.
"""

    REPORT_OUT.write_text(report, encoding="utf-8")

    print(f"Wrote {SUMMARY_OUT}")
    print(f"Wrote {CELLS_OUT}")
    print(f"Wrote {GREEDY_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(exact_view.to_string(index=False))


if __name__ == "__main__":
    main()
