#!/usr/bin/env python3
"""E73 public-failure split: pure Q2/S3 graft versus broad base movement.

The submitted E73 file scored worse on public LB, but movement auditing shows
it changed all seven targets versus mixmin. This probe separates the live
questions:

- Does the isolated E73 Q2/S3 movement still survive local stress when grafted
  onto the validated mixmin anchor?
- Was the public failure more plausibly caused by non-Q2/S3 base movement?
- Is the public observation strong enough to justify an inverse Q2/S3 sign
  hypothesis, or does local stress reject that as pure leaderboard reaction?

No submission is written unless a pure graft is strict/deployable under the
existing consensus stress.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import q2_s3_target_amplitude_ridge_probe as e75  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


E73_FILE = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
SCAN_OUT = OUT / "e73_pure_q2s3_graft_probe_scan.csv"
SUMMARY_OUT = OUT / "e73_pure_q2s3_graft_probe_summary.csv"
REPORT_OUT = OUT / "e73_pure_q2s3_graft_probe_report.md"

EPS = 1.0e-6
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def tag_from_pred(name: str, pred: np.ndarray) -> str:
    return e70.e68.e67.stable_tag(pred, prefix=f"e80_{name}_")


def replace_targets(base: np.ndarray, donor: np.ndarray, target_idxs: list[int]) -> np.ndarray:
    out = np.asarray(base, dtype=np.float64).copy()
    out[:, target_idxs] = donor[:, target_idxs]
    return clip_prob(out)


def invert_targets(base: np.ndarray, donor: np.ndarray, target_idxs: list[int]) -> np.ndarray:
    base_logit = logit(base)
    donor_logit = logit(donor)
    out_logit = base_logit.copy()
    out_logit[:, target_idxs] = base_logit[:, target_idxs] - (donor_logit[:, target_idxs] - base_logit[:, target_idxs])
    return clip_prob(sigmoid(out_logit))


def movement_summary(preds: list[np.ndarray], names: list[str], mixmin: np.ndarray) -> pd.DataFrame:
    mix_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    for name, pred in zip(names, preds):
        delta = logit(pred) - mix_logit
        moved = np.abs(delta) > 1.0e-12
        active_targets = [t for i, t in enumerate(TARGETS) if moved[:, i].any()]
        rows.append(
            {
                "name": name,
                "active_cells": int(moved.sum()),
                "active_rows": int(moved.any(axis=1).sum()),
                "active_targets": ",".join(active_targets),
                "mean_abs_logit_move": float(np.abs(delta).mean()),
                "mean_abs_q2s3_logit_move": float(np.abs(delta[:, QS_IDXS]).mean()),
                "q2_cells": int(moved[:, Q2_IDX].sum()),
                "s3_cells": int(moved[:, S3_IDX].sum()),
                "q2_increases": int((delta[:, Q2_IDX] > 1.0e-12).sum()),
                "q2_decreases": int((delta[:, Q2_IDX] < -1.0e-12).sum()),
                "s3_increases": int((delta[:, S3_IDX] > 1.0e-12).sum()),
                "s3_decreases": int((delta[:, S3_IDX] < -1.0e-12).sum()),
            }
        )
    return pd.DataFrame(rows)


def build_candidates(mixmin: np.ndarray, e73: np.ndarray) -> tuple[pd.DataFrame, list[np.ndarray], list[str]]:
    names = [
        "mixmin_base",
        "e73_full_submitted",
        "pure_q2s3_graft",
        "pure_q2_only_graft",
        "pure_s3_only_graft",
        "non_q2s3_only_graft",
        "inverse_q2s3_public_sensor",
        "inverse_q2_only_public_sensor",
        "inverse_s3_only_public_sensor",
    ]
    preds = [
        mixmin,
        e73,
        replace_targets(mixmin, e73, QS_IDXS),
        replace_targets(mixmin, e73, [Q2_IDX]),
        replace_targets(mixmin, e73, [S3_IDX]),
        replace_targets(e73, mixmin, QS_IDXS),
        invert_targets(mixmin, e73, QS_IDXS),
        invert_targets(mixmin, e73, [Q2_IDX]),
        invert_targets(mixmin, e73, [S3_IDX]),
    ]
    rows: list[dict[str, Any]] = []
    move = movement_summary(preds, names, mixmin).set_index("name")
    for pred_index, name in enumerate(names[1:], start=1):
        rows.append(
            {
                "pred_index": pred_index,
                "base_index": 0,
                "name": name,
                "tag": tag_from_pred(name, preds[pred_index]),
                "base_tag": tag_from_pred("mixmin_base", preds[0]),
                "movement_family": "submitted_full"
                if name == "e73_full_submitted"
                else "pure_graft"
                if "graft" in name
                else "public_inverse_sensor",
                "active_cells": int(move.loc[name, "active_cells"]),
                "active_rows": int(move.loc[name, "active_rows"]),
                "active_targets": str(move.loc[name, "active_targets"]),
                "mean_abs_logit_move": float(move.loc[name, "mean_abs_logit_move"]),
                "mean_abs_q2s3_logit_move": float(move.loc[name, "mean_abs_q2s3_logit_move"]),
            }
        )
    return pd.DataFrame(rows), preds, names


def score_candidates(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    mixmin: np.ndarray,
) -> pd.DataFrame:
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    _components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    return e75.score_rows(rows, preds, sample, mixmin, labels, worlds, views, state)


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "name",
        "movement_family",
        "active_cells",
        "active_rows",
        "active_targets",
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
        "strict_gate",
        "deployable_gate",
        "loose_gate",
    ]
    return scan[cols].sort_values(
        ["deployable_gate", "loose_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, movement: pd.DataFrame) -> None:
    pure = scan[scan["name"].str.contains("pure_", regex=False)].sort_values("all_delta_vs_mixmin")
    inverse = scan[scan["movement_family"].eq("public_inverse_sensor")].sort_values("all_delta_vs_mixmin")
    lines = [
        "# E73 Pure Q2/S3 Graft Probe",
        "",
        "## Observe",
        "",
        "`submission_e72_topabs50_q2s3_gate_4e48cba2.csv` worsened public LB, but it was not a pure Q2/S3 test because it moved every target family.",
        "",
        "## Wonder",
        "",
        "Is public rejecting the isolated Q2/S3 sparse movement, the broad non-Q2/S3 base movement, or a coupled interaction between them?",
        "",
        "## Candidate Movement Audit",
        "",
        e56.markdown_table(movement),
        "",
        "## Stress Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Pure Graft Rows",
        "",
        e56.markdown_table(pure),
        "",
        "## Public-Inverse Sensor Rows",
        "",
        e56.markdown_table(inverse),
        "",
        "## Decision",
        "",
    ]
    deployable = summary[summary["deployable_gate"]]
    pure_deployable = deployable[deployable["name"].str.contains("pure_q2s3", regex=False)]
    if len(pure_deployable):
        lines.append("- A pure mixmin-anchored Q2/S3 graft survived strict/deployable stress; it is eligible as the next public sensor.")
    else:
        lines.append("- No pure Q2/S3 graft survived strict/deployable stress. The E73 public failure should pause E74/E75 direct follow-ups rather than trigger an immediate pure-graft submission.")
    if bool((inverse["loose_gate"]).any()):
        lines.append("- At least one inverse public-sensor row survived loose stress, so public-opposition remains a diagnostic branch, but it is not strict enough to submit by default.")
    else:
        lines.append("- The inverse public-sensor rows do not survive local stress; do not turn one public miss into direct sign inversion.")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e73 = load_sub(E73_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)

    rows, preds, names = build_candidates(mixmin, e73)
    movement = movement_summary(preds, names, mixmin)
    scan = score_candidates(rows, preds, sample, mixmin)
    summary = summarize(scan)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, movement)
    print(
        f"rows={len(scan)} deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} best={scan.sort_values('all_delta_vs_mixmin').iloc[0]['name']} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.8g} wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
