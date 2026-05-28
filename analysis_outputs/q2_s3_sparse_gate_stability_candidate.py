#!/usr/bin/env python3
"""Materialize the E74 full-pool alpha20 sparse Q2/S3 gate candidate."""

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
import q2_s3_sparse_gate_stability_probe as e74  # noqa: E402
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_IN = OUT / "q2_s3_sparse_gate_stability_probe_scan.csv"
SUB_OUT = OUT / "submission_e74_fullpool_a20_q2s3_gate_55455b60.csv"
REPORT_OUT = OUT / "submission_e74_fullpool_a20_q2s3_gate_55455b60_report.md"
SELECT_VARIANT_KIND = "reference"
SELECT_VARIANT_NAME = "full_pool"
SELECT_ALPHA = 20.0
EXPECTED_TAG = "e74_full_pool_20.00_55455b60"


def select_candidate(scan: pd.DataFrame) -> pd.Series:
    rows = scan[
        scan["variant_kind"].eq(SELECT_VARIANT_KIND)
        & scan["variant_name"].eq(SELECT_VARIANT_NAME)
        & scan["alpha"].eq(SELECT_ALPHA)
    ].copy()
    if len(rows) != 1:
        raise RuntimeError(
            "expected one E74 full-pool alpha20 row, "
            f"found {len(rows)} in {SCAN_IN.relative_to(ROOT)}"
        )
    row = rows.iloc[0]
    if str(row["tag"]) != EXPECTED_TAG:
        raise RuntimeError(f"unexpected selected tag: {row['tag']} != {EXPECTED_TAG}")
    if not bool(row["strict_gate"]) or not bool(row["deployable_gate"]):
        raise RuntimeError("selected E74 alpha20 row is not strict/deployable")
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
    rows, preds, _variants = e74.build_stability_candidates(cells, bases, deltas)
    matches = rows[rows["tag"].eq(tag)]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one regenerated row for {tag}, found {len(matches)}")
    pred = preds[int(matches.iloc[0]["pred_index"])]
    return sample, pred


def write_report(row: pd.Series) -> None:
    fields = [
        "tag",
        "variant_kind",
        "variant_name",
        "pool",
        "pool_size",
        "pool_support_mean",
        "pool_support2_count",
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
        "mean_abs_q2s3_logit_delta_vs_e73",
        "q2s3_topabs_jaccard_vs_e73",
        "gate_active_q2s3",
        "gate_weight_q2s3_mean",
        "strict_gate",
        "deployable_gate",
        "loose_gate",
    ]
    table = pd.DataFrame([{k: row[k] for k in fields}])
    lines = [
        "# E74 Submission Candidate: Full-Pool Alpha20 Sparse Q2/S3 Gate",
        "",
        "## Candidate",
        "",
        f"- File: `{SUB_OUT.relative_to(ROOT)}`",
        f"- Source scan: `{SCAN_IN.relative_to(ROOT)}`",
        "- Selection rule: the E74 reference/full_pool row at alpha20. This keeps the exact E73 13-cell source pool and changes only amplitude from 16 to 20.",
        "",
        "## Local Evidence",
        "",
        e56.markdown_table(table),
        "",
        "## Hidden-World Hypothesis",
        "",
        "This file bets that E73's sparse-magnitude Q2/S3 gate was directionally right but conservative: the same full-pool latent movement has a shallow amplitude ridge around alpha20 before alpha24 breaks strict consensus.",
        "",
        "## Public LB Interpretation",
        "",
        "- If public LB improves over E73: sparse Q2/S3 structure is public-aligned and the bottleneck is under-amplitude rather than gate selection.",
        "- If public LB worsens while E73 improves or holds: the gate shape is real but the amplitude ridge is a local-stress illusion; keep E73 and require stronger public-like amplitude calibration.",
        "- If both E73 and this file worsen: E74 stability is local-only, and sparse Q2/S3 movements should be demoted behind a different hidden-world branch.",
        "",
        "## Submission Order",
        "",
        "Secondary diagnostic after E73. It is higher-upside but higher-risk because alpha24 already fails strict consensus.",
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
