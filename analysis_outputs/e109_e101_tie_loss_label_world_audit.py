#!/usr/bin/env python3
"""E109 E101 tie/loss hard-label world audit.

E108 pre-materialized the branch for an E101 public win. The remaining blind
spot is the other side: if E101 ties or loses, what must be true about the 50
active Q2/S3 hard labels, and does any same-amplitude family remain locally
coherent?

This script does not use public labels. It samples hidden labels for the E101
active cells under global and subject train priors, buckets worlds by their
E101-vs-E95 active-cell contribution, and measures which candidate families
benefit inside each bucket. All candidate deltas here are active-cell-only; they
are a diagnostic for branch choice, not a public LB forecast.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402


TRAIN_IN = ROOT / "data" / "ch2026_metrics_train.csv"
CELLS_IN = OUT / "e105_e101_public_label_breakeven_cells.csv"

SUMMARY_OUT = OUT / "e109_e101_tie_loss_label_world_summary.csv"
CANDIDATE_OUT = OUT / "e109_e101_tie_loss_label_world_candidates.csv"
CELL_POSTERIOR_OUT = OUT / "e109_e101_tie_loss_label_world_cell_posterior.csv"
REPORT_OUT = OUT / "e109_e101_tie_loss_label_world_report.md"

TOTAL_TEST_CELLS = 250 * len(TARGETS)
N_SIMS = 200_000
RNG_SEED = 109
EPS = 1.0e-15

CANDIDATE_FILES = {
    "e95": "submission_e95_hardtail_541e3973.csv",
    "e101": "submission_e101_q2s3tail_177569bc.csv",
    "e108_amp050": "submission_e108_if_e101win_amp050_079aab57.csv",
    "e108_strict_amp038": "submission_e108_if_e101win_strict_amp038_64514c53.csv",
    "e89": "submission_e89_e72decontam_00d7807f.csv",
    "e85": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e90": "submission_e90_e72pareto_28925de5.csv",
    "e86": "submission_e86_e85_consensus_a3f7c96f.csv",
    "mixmin": "submission_mixmin_0c916bb4.csv",
}

OUTCOME_BINS = [
    ("edge_or_stronger_win", -np.inf, -1.10e-5),
    ("small_win", -1.10e-5, -3.00e-6),
    ("tie", -3.00e-6, 3.00e-6),
    ("small_loss", 3.00e-6, 2.00e-5),
    ("large_loss", 2.00e-5, np.inf),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
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


def load_candidate_probs(sample: pd.DataFrame, cells: pd.DataFrame) -> dict[str, np.ndarray]:
    target_index = {target: i for i, target in enumerate(TARGETS)}
    row_idx = cells["sub_idx"].to_numpy(dtype=int)
    col_idx = cells["target"].map(target_index).to_numpy(dtype=int)
    probs: dict[str, np.ndarray] = {}
    for name, file_name in CANDIDATE_FILES.items():
        arr = clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))
        probs[name] = arr[row_idx, col_idx]

    if not np.allclose(probs["e95"], cells["prob_e95"].to_numpy(dtype=np.float64), atol=1.0e-10):
        raise RuntimeError("E95 active-cell alignment mismatch")
    if not np.allclose(probs["e101"], cells["prob_e101"].to_numpy(dtype=np.float64), atol=1.0e-10):
        raise RuntimeError("E101 active-cell alignment mismatch")
    return probs


def candidate_label_deltas(probs: dict[str, np.ndarray], base: str = "e95") -> dict[str, tuple[np.ndarray, np.ndarray]]:
    base_p = clip_prob(probs[base])
    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, prob in probs.items():
        p = clip_prob(prob)
        d1 = np.log(base_p / p)
        d0 = np.log((1.0 - base_p) / (1.0 - p))
        out[name] = (d0, d1)
    return out


def attach_priors(cells: pd.DataFrame) -> pd.DataFrame:
    train = pd.read_csv(TRAIN_IN)
    global_prior = train[TARGETS].mean()
    subject_prior = train.groupby("subject_id")[TARGETS].mean()

    out = cells.copy()
    out["global_prior_y1"] = [float(global_prior.loc[t]) for t in out["target"]]
    out["subject_prior_y1"] = [
        float(subject_prior.loc[s, t]) for s, t in zip(out["subject_id"], out["target"])
    ]
    return out


def simulate_labels(cells: pd.DataFrame, prior_name: str) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED + (0 if prior_name == "global" else 1000))
    pi = cells[f"{prior_name}_prior_y1"].to_numpy(dtype=np.float64)
    return rng.random((N_SIMS, len(cells))) < pi


def assign_outcomes(delta: np.ndarray) -> np.ndarray:
    out = np.full(delta.shape, "unassigned", dtype=object)
    for name, lo, hi in OUTCOME_BINS:
        out[(delta > lo) & (delta <= hi)] = name
    if np.any(out == "unassigned"):
        raise RuntimeError("unassigned outcome bucket")
    return out


def world_summary(cells: pd.DataFrame, labels: np.ndarray, e101_delta: np.ndarray, prior_name: str) -> pd.DataFrame:
    outcomes = assign_outcomes(e101_delta)
    support_label = cells["support_label"].to_numpy(dtype=bool)
    support = labels == support_label.reshape(1, -1)
    top10 = cells["flip_rank"].to_numpy(dtype=int) <= 10
    top23 = cells["flip_rank"].to_numpy(dtype=int) <= 23
    s3 = cells["target"].eq("S3").to_numpy()
    q2 = cells["target"].eq("Q2").to_numpy()
    edge = cells["edge_distance"].to_numpy(dtype=float) <= 1.0
    flip = cells["flip_benefit"].to_numpy(dtype=np.float64)
    total_flip = float(flip.sum())

    rows: list[dict[str, Any]] = []
    for outcome, _, _ in OUTCOME_BINS:
        sel = outcomes == outcome
        n = int(sel.sum())
        if n == 0:
            rows.append({"prior": prior_name, "outcome": outcome, "n_worlds": 0})
            continue
        support_sel = support[sel]
        labels_sel = labels[sel]
        flip_share = (support_sel * flip.reshape(1, -1)).sum(axis=1) / total_flip
        rows.append(
            {
                "prior": prior_name,
                "outcome": outcome,
                "n_worlds": n,
                "world_rate": n / len(e101_delta),
                "e101_delta_mean": float(e101_delta[sel].mean()),
                "e101_delta_p05": float(np.quantile(e101_delta[sel], 0.05)),
                "e101_delta_p50": float(np.quantile(e101_delta[sel], 0.50)),
                "e101_delta_p95": float(np.quantile(e101_delta[sel], 0.95)),
                "support_cells_mean": float(support_sel.sum(axis=1).mean()),
                "support_cells_p05": float(np.quantile(support_sel.sum(axis=1), 0.05)),
                "support_cells_p95": float(np.quantile(support_sel.sum(axis=1), 0.95)),
                "top10_support_rate": float(support_sel[:, top10].mean()),
                "top23_support_rate": float(support_sel[:, top23].mean()),
                "support_flip_share_mean": float(flip_share.mean()),
                "support_flip_share_p05": float(np.quantile(flip_share, 0.05)),
                "support_flip_share_p95": float(np.quantile(flip_share, 0.95)),
                "s3_support_rate": float(support_sel[:, s3].mean()),
                "q2_support_rate": float(support_sel[:, q2].mean()),
                "edge_support_rate": float(support_sel[:, edge].mean()),
                "interior_support_rate": float(support_sel[:, ~edge].mean()),
                "s3_label1_rate": float(labels_sel[:, s3].mean()),
                "q2_label1_rate": float(labels_sel[:, q2].mean()),
            }
        )
    return pd.DataFrame(rows)


def candidate_summary(
    labels: np.ndarray,
    e101_delta: np.ndarray,
    prior_name: str,
    deltas: dict[str, tuple[np.ndarray, np.ndarray]],
) -> pd.DataFrame:
    outcomes = assign_outcomes(e101_delta)
    pred_delta: dict[str, np.ndarray] = {}
    for name, (d0, d1) in deltas.items():
        pred_delta[name] = np.where(labels, d1.reshape(1, -1), d0.reshape(1, -1)).sum(axis=1) / TOTAL_TEST_CELLS

    rows: list[dict[str, Any]] = []
    for outcome, _, _ in OUTCOME_BINS:
        sel = outcomes == outcome
        if int(sel.sum()) == 0:
            continue
        for name, delta in pred_delta.items():
            vs_e95 = delta[sel]
            vs_e101 = vs_e95 - pred_delta["e101"][sel]
            rows.append(
                {
                    "prior": prior_name,
                    "outcome": outcome,
                    "candidate": name,
                    "n_worlds": int(sel.sum()),
                    "active_mean_vs_e95": float(vs_e95.mean()),
                    "active_p05_vs_e95": float(np.quantile(vs_e95, 0.05)),
                    "active_p50_vs_e95": float(np.quantile(vs_e95, 0.50)),
                    "active_p95_vs_e95": float(np.quantile(vs_e95, 0.95)),
                    "active_beat_e95_rate": float((vs_e95 < -1.0e-12).mean()),
                    "active_mean_vs_e101": float(vs_e101.mean()),
                    "active_p95_vs_e101": float(np.quantile(vs_e101, 0.95)),
                    "active_beat_e101_rate": float((vs_e101 < -1.0e-12).mean()),
                }
            )
    out = pd.DataFrame(rows)
    out["rank_vs_e101"] = out.groupby(["prior", "outcome"])["active_mean_vs_e101"].rank(method="first")
    return out


def cell_posterior(cells: pd.DataFrame, labels: np.ndarray, e101_delta: np.ndarray, prior_name: str) -> pd.DataFrame:
    outcomes = assign_outcomes(e101_delta)
    support_label = cells["support_label"].to_numpy(dtype=bool)
    support = labels == support_label.reshape(1, -1)
    rows: list[pd.DataFrame] = []
    keep_cols = [
        "sub_idx",
        "target",
        "subject_id",
        "hidden_block_id",
        "lifelog_date",
        "edge_distance",
        "flip_rank",
        "flip_benefit",
        "support_label",
        "subject_prior_y1",
        "global_prior_y1",
    ]
    base = cells[keep_cols].copy()
    for outcome, _, _ in OUTCOME_BINS:
        sel = outcomes == outcome
        if int(sel.sum()) == 0:
            continue
        part = base.copy()
        part.insert(0, "outcome", outcome)
        part.insert(0, "prior", prior_name)
        part["posterior_support_rate"] = support[sel].mean(axis=0)
        part["posterior_label1_rate"] = labels[sel].mean(axis=0)
        part["support_rate_lift_vs_subject_prior"] = (
            part["posterior_support_rate"]
            - np.where(
                part["support_label"].astype(int).eq(1),
                part["subject_prior_y1"],
                1.0 - part["subject_prior_y1"],
            )
        )
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def write_report(summary: pd.DataFrame, candidates: pd.DataFrame, posterior: pd.DataFrame) -> None:
    summary_cols = [
        "prior",
        "outcome",
        "n_worlds",
        "world_rate",
        "e101_delta_mean",
        "support_cells_mean",
        "top10_support_rate",
        "top23_support_rate",
        "support_flip_share_mean",
        "s3_support_rate",
        "q2_support_rate",
        "edge_support_rate",
    ]
    focus_candidates = [
        "e95",
        "e101",
        "e108_amp050",
        "e108_strict_amp038",
        "e89",
        "e85",
        "e90",
        "e86",
        "mixmin",
    ]
    cand_focus = candidates[
        candidates["candidate"].isin(focus_candidates)
        & candidates["outcome"].isin(["tie", "small_loss", "large_loss"])
    ].sort_values(["prior", "outcome", "rank_vs_e101"])
    cand_cols = [
        "prior",
        "outcome",
        "candidate",
        "active_mean_vs_e95",
        "active_p95_vs_e95",
        "active_beat_e95_rate",
        "active_mean_vs_e101",
        "active_p95_vs_e101",
        "active_beat_e101_rate",
        "rank_vs_e101",
    ]
    posterior_focus = (
        posterior[
            posterior["prior"].eq("subject")
            & posterior["outcome"].isin(["tie", "small_loss", "large_loss"])
        ]
        .sort_values(["outcome", "support_rate_lift_vs_subject_prior"])
        .groupby("outcome", as_index=False)
        .head(8)
    )
    posterior_cols = [
        "outcome",
        "sub_idx",
        "target",
        "subject_id",
        "hidden_block_id",
        "edge_distance",
        "flip_rank",
        "support_label",
        "posterior_support_rate",
        "support_rate_lift_vs_subject_prior",
    ]

    report = f"""# E109 E101 Tie/Loss Label-World Audit

## Question

E108 pre-materialized what to do if E101 wins. This audit asks the opposite:
if E101 ties or loses, what hard-label world on the 50 active cells is implied,
and does a larger E101-style amplitude remain coherent?

All candidate deltas below are active-cell-only diagnostics, not full public LB
forecasts.

## Outcome Summary

{md_table(summary[summary_cols], '.9f')}

## Candidate Behavior In Tie/Loss Buckets

{md_table(cand_focus[cand_cols], '.9f')}

## Subject-Prior Cells Most Suppressed In Tie/Loss Worlds

{md_table(posterior_focus[posterior_cols], '.9f')}

## Interpretation

- E101 tie/loss worlds are mostly worlds where high-impact S3 support labels do
  not appear often enough. That is a hard-label realization issue, not a new
  subject/block selector.
- In tie/loss buckets, E108 amp050 and strict amp038 should not be used as a
  rescue unless their active-cell `active_mean_vs_e101` is negative inside the
  observed outcome bucket. The expected condition from E107 is that tie/loss
  has positive p95 and weak or tense support.
- If E101 loses, the next branch should be model revision or a different public
  sensor such as full E89 only if the question remains diffuse Q2/S3 allocation,
  not a larger active-all rollback.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    cells = attach_priors(pd.read_csv(CELLS_IN))
    probs = load_candidate_probs(sample, cells)
    deltas = candidate_label_deltas(probs)

    d0_e101, d1_e101 = deltas["e101"]
    summary_parts: list[pd.DataFrame] = []
    candidate_parts: list[pd.DataFrame] = []
    posterior_parts: list[pd.DataFrame] = []
    for prior_name in ["global", "subject"]:
        labels = simulate_labels(cells, prior_name)
        e101_delta = np.where(labels, d1_e101.reshape(1, -1), d0_e101.reshape(1, -1)).sum(axis=1) / TOTAL_TEST_CELLS
        summary_parts.append(world_summary(cells, labels, e101_delta, prior_name))
        candidate_parts.append(candidate_summary(labels, e101_delta, prior_name, deltas))
        posterior_parts.append(cell_posterior(cells, labels, e101_delta, prior_name))

    summary = pd.concat(summary_parts, ignore_index=True)
    candidates = pd.concat(candidate_parts, ignore_index=True)
    posterior = pd.concat(posterior_parts, ignore_index=True)

    summary.to_csv(SUMMARY_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    posterior.to_csv(CELL_POSTERIOR_OUT, index=False)
    write_report(summary, candidates, posterior)

    subject_loss = summary[summary["prior"].eq("subject") & summary["outcome"].eq("small_loss")].iloc[0]
    subject_tie = summary[summary["prior"].eq("subject") & summary["outcome"].eq("tie")].iloc[0]
    assert int(subject_loss["n_worlds"]) > 0
    assert int(subject_tie["n_worlds"]) > 0
    amp050_loss = candidates[
        candidates["prior"].eq("subject")
        & candidates["outcome"].eq("small_loss")
        & candidates["candidate"].eq("e108_amp050")
    ].iloc[0]
    assert float(amp050_loss["active_p95_vs_e101"]) > 0.0

    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {CANDIDATE_OUT}")
    print(f"wrote {CELL_POSTERIOR_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
