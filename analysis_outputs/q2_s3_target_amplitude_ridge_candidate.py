#!/usr/bin/env python3
"""Materialize the best E75 target-specific Q2/S3 amplitude ridge candidate."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_target_amplitude_ridge_probe as e75  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_IN = OUT / "q2_s3_target_amplitude_ridge_probe_scan.csv"
SUB_OUT = OUT / "submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv"
REPORT_OUT = OUT / "submission_e75_q2a8_s3a28_sparse_amp_f07219b4_report.md"
EXPECTED_TAG = "e75_q2a8.0_s3a28.0_f07219b4"


def select_candidate(scan: pd.DataFrame) -> pd.Series:
    deployable = scan[scan["deployable_gate"]].copy()
    if deployable.empty:
        raise RuntimeError("E75 scan has no deployable rows")
    row = deployable.sort_values(
        [
            "all_delta_vs_mixmin",
            "worst_set_delta_vs_mixmin",
            "mean_abs_q2s3_logit_delta_vs_e74",
            "tag",
        ],
        ascending=[True, True, True, True],
    ).iloc[0]
    if str(row["tag"]) != EXPECTED_TAG:
        raise RuntimeError(f"unexpected selected tag: {row['tag']} != {EXPECTED_TAG}")
    if float(row["alpha_q2"]) != 8.0 or float(row["alpha_s3"]) != 28.0:
        raise RuntimeError("selected row is not the expected q2=8, s3=28 asymmetric ridge")
    return row


def materialize_prediction(tag: str) -> tuple[pd.DataFrame, np.ndarray]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    strict = e69.strict_rows()
    cells = e71.unique_strict_cells(strict)
    bases, _cands, deltas = e71.reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)
    rows, preds, _meta = e75.build_target_alpha_candidates(cells, bases, deltas)
    matches = rows[rows["tag"].eq(tag)]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one regenerated row for {tag}, found {len(matches)}")
    pred = preds[int(matches.iloc[0]["pred_index"])]
    return sample, pred


def write_report(row: pd.Series) -> None:
    fields = [
        "tag",
        "dominant_axis",
        "pool",
        "pool_size",
        "pool_support_mean",
        "pool_support2_count",
        "base_agg",
        "delta_agg",
        "gate",
        "alpha_q2",
        "alpha_s3",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "worst_set_delta_vs_mixmin",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "hidden_q2_minus_base",
        "hidden_s3_minus_base",
        "world_support_minus_base",
        "raw_energy_q_p90_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "mean_abs_logit_move_vs_mixmin",
        "mean_abs_q2s3_logit_move_vs_mixmin",
        "mean_abs_q2s3_logit_delta_vs_e73",
        "mean_abs_q2s3_logit_delta_vs_e74",
        "strict_gate",
        "deployable_gate",
        "loose_gate",
    ]
    table = pd.DataFrame([{k: row[k] for k in fields}])
    lines = [
        "# E75 Submission Candidate: Q2-Low/S3-High Sparse Amplitude Ridge",
        "",
        "## Candidate",
        "",
        f"- File: `{SUB_OUT.relative_to(ROOT)}`",
        f"- Source scan: `{SCAN_IN.relative_to(ROOT)}`",
        "- Selection rule: best E75 deployable row by all-combo delta, then worst-set delta and distance from E74.",
        "",
        "## Local Evidence",
        "",
        e56.markdown_table(table),
        "",
        "## Hidden-World Hypothesis",
        "",
        "This file bets that E73/E74 found the right sparse Q2/S3 gate but used the wrong target amplitude: Q2 should be shrunk while S3 should be expanded. The public-sensitive component is S3-heavy, while Q2 contributes more hidden/world support than public-combo edge.",
        "",
        "## Public LB Interpretation",
        "",
        "- If public LB improves over E73/E74: the sparse gate is real and public amplitude is target-asymmetric, with S3 carrying the readable public signal.",
        "- If E73 improves but this worsens: sparse-gate sign is real but S3-high/Q2-low amplitude is local combo overfit.",
        "- If this improves while E73/E74 do not: target-specific amplitude was the missing object, and future gates should separate Q2 hidden/world support from S3 public-combo support.",
        "",
        "## Submission Order",
        "",
        "High-information follow-up after E73. It may outrank E74 as a second sensor because it tests a sharper target-asymmetry hypothesis, but it is more aggressive than E73.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan = pd.read_csv(SCAN_IN)
    row = select_candidate(scan)
    sample, pred = materialize_prediction(str(row["tag"]))
    sub = sample.copy()
    sub[TARGETS] = pred
    sub.to_csv(SUB_OUT, index=False)
    write_report(row)
    print(
        f"wrote={SUB_OUT.relative_to(ROOT)} tag={row['tag']} "
        f"all_delta={row['all_delta_vs_mixmin']:.8g} "
        f"hidden_q2s3={row['hidden_q2s3_mean_minus_base']:.8g}"
    )


if __name__ == "__main__":
    main()
