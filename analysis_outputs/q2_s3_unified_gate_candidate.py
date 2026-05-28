#!/usr/bin/env python3
"""Materialize the best E72 deployable Q2/S3 gate as a submission candidate."""

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
import q2_s3_unified_gate_geometry_probe as e72  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_IN = OUT / "q2_s3_unified_gate_geometry_probe_scan.csv"
SUB_OUT = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
REPORT_OUT = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2_report.md"


def select_candidate(scan: pd.DataFrame) -> pd.Series:
    deployable = scan[scan["deployable_gate"]].copy()
    if deployable.empty:
        raise RuntimeError("E72 scan has no deployable rows")
    deployable = deployable.sort_values(
        [
            "all_delta_vs_mixmin",
            "worst_set_delta_vs_mixmin",
            "mean_abs_logit_move_vs_mixmin",
            "tag",
        ],
        ascending=[True, True, True, True],
    )
    return deployable.iloc[0]


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
    rows, preds = e72.build_adaptive_candidates(cells, bases, deltas)
    matches = rows[rows["tag"].eq(tag)]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one regenerated row for {tag}, found {len(matches)}")
    pred = preds[int(matches.iloc[0]["pred_index"])]
    return sample, pred


def write_report(row: pd.Series) -> None:
    fields = [
        "tag",
        "pool",
        "pool_size",
        "pool_support_mean",
        "base_agg",
        "delta_agg",
        "gate",
        "alpha",
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
        "gate_active_q2s3",
        "gate_weight_q2s3_mean",
    ]
    table = pd.DataFrame([{k: row[k] for k in fields}])
    lines = [
        "# E73 Submission Candidate: E72 TopAbs50 Q2/S3 Gate",
        "",
        "## Candidate",
        "",
        f"- File: `{SUB_OUT.relative_to(ROOT)}`",
        f"- Source scan: `{SCAN_IN.relative_to(ROOT)}`",
        "- Selection rule: best E72 deployable row sorted by all-combo delta, worst-set delta, and movement size.",
        "",
        "## Local Evidence",
        "",
        e56.markdown_table(table),
        "",
        "## Hidden-World Hypothesis",
        "",
        "This file bets that the deployable part of the Q2/S3 consensus is sparse-magnitude rather than sign-agreement based: `top_abs50` keeps only the strongest half of the unified Q2/S3 consensus movement and clears all strict local gates.",
        "",
        "## Public LB Interpretation",
        "",
        "- If public LB improves: E71's `gate=none` failure was mostly a gate-shape problem, and sparse top-magnitude Q2/S3 consensus is public-aligned.",
        "- If public LB worsens: E72 is still overfitting local combo/hidden/world stress, and the next branch should require a stronger independent public-subset or structural block target before submission.",
        "",
        "## Submission Order",
        "",
        "Priority 1 diagnostic candidate after `submission_mixmin_0c916bb4.csv`; not a replacement until public observation confirms it.",
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
    print(f"wrote={SUB_OUT.relative_to(ROOT)} tag={row['tag']} all_delta={row['all_delta_vs_mixmin']:.8g}")


if __name__ == "__main__":
    main()
