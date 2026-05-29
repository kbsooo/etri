#!/usr/bin/env python3
"""E172: rollback stress for E169 critical-tail cells.

E171 split E169 into a visible-prior-favorable broad body and a visible-prior
adverse critical tail. This script asks whether rolling back that critical tail
toward E95 preserves the broad body while reducing prior-tail risk.

No model is trained. A submission is materialized only if a rollback keeps
E169-style breadth and improves visible-prior tail health without collapsing the
focus-prior edge.
"""

from __future__ import annotations

import hashlib
from math import erf, sqrt
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
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import e166_broad_survivor_scale_probe as e166  # noqa: E402
import e171_e169_critical_cell_prior_audit as e171  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E169_FILE = "submission_e169_ctx_veto_c5e806e3.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

SCAN_OUT = OUT / "e172_e169_critical_tail_rollback_probe_scan.csv"
SHORTLIST_OUT = OUT / "e172_e169_critical_tail_rollback_probe_shortlist.csv"
REPORT_OUT = OUT / "e172_e169_critical_tail_rollback_probe_report.md"

EPS = 1.0e-12
N_PUBLIC_CELLS = 250 * len(TARGETS)
PRIORS = ["focus_mean", "visible_mean", "subject", "flank_mean", "nearest_hard085"]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return 0.0
    return float(np.dot(aa, bb) / den)


def normal_cdf(x: float, mean: float, std: float) -> float:
    if std <= EPS:
        return float(x >= mean)
    return 0.5 * (1.0 + erf((x - mean) / (std * sqrt(2.0))))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return e166.load_prob_path(OUT / file_name, sample)


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = clip_prob(p_new)
    p_base = clip_prob(p_base)
    return -np.log(p_new) + np.log(p_base), -np.log(1.0 - p_new) + np.log(1.0 - p_base)


def mask_to_matrix(cells: pd.DataFrame, mask: np.ndarray, keep: float) -> np.ndarray:
    mat = np.ones((250, len(TARGETS)), dtype=np.float64)
    part = cells.loc[mask]
    mat[part["sub_idx"].to_numpy(dtype=int), part["target_idx"].to_numpy(dtype=int)] = float(keep)
    return mat


def build_variant_specs(cells: pd.DataFrame) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [{"policy": "baseline_e169", "mask": np.zeros(len(cells), dtype=bool), "keep": 1.0}]
    base_masks: list[tuple[str, np.ndarray]] = []
    for n in [4, 8, 16, 32, 64]:
        top = cells["swing_rank"].le(n).to_numpy()
        base_masks.append((f"top{n}_swing", top))
        base_masks.append((f"top{n}_visible_lt0p5", top & cells["support_probability_visible_mean"].lt(0.5).to_numpy()))
        base_masks.append((f"top{n}_visible_lt0p3", top & cells["support_probability_visible_mean"].lt(0.3).to_numpy()))
    base_masks.extend(
        [
            ("all_visible_lt0p2", cells["support_probability_visible_mean"].lt(0.2).to_numpy()),
            ("all_visible_lt0p3", cells["support_probability_visible_mean"].lt(0.3).to_numpy()),
            (
                "all_visible_lt0p3_tophalf_swing",
                cells["support_probability_visible_mean"].lt(0.3).to_numpy()
                & cells["swing_rank"].le(int(len(cells) * 0.5)).to_numpy(),
            ),
            (
                "top32_visible_adverse_s_targets",
                cells["swing_rank"].le(32).to_numpy()
                & cells["support_probability_visible_mean"].lt(0.5).to_numpy()
                & cells["target_group"].eq("S").to_numpy(),
            ),
            (
                "top32_visible_adverse_q_targets",
                cells["swing_rank"].le(32).to_numpy()
                & cells["support_probability_visible_mean"].lt(0.5).to_numpy()
                & cells["target_group"].eq("Q").to_numpy(),
            ),
            (
                "top32_expected_positive_visible",
                cells["swing_rank"].le(32).to_numpy() & cells["expected_delta_visible_mean"].gt(0).to_numpy(),
            ),
            (
                "visible_positive_all",
                cells["expected_delta_visible_mean"].gt(0).to_numpy(),
            ),
        ]
    )
    for name, mask in base_masks:
        if int(mask.sum()) == 0:
            continue
        for keep in [0.0, 0.25, 0.50]:
            specs.append({"policy": f"{name}_keep{str(keep).replace('.', 'p')}", "mask": mask, "keep": keep})
    return specs


def prior_moments(cells: pd.DataFrame, pred: np.ndarray, e95: np.ndarray, prior: str) -> dict[str, float]:
    r = cells["sub_idx"].to_numpy(dtype=int)
    c = cells["target_idx"].to_numpy(dtype=int)
    d1, d0 = hard_loss_deltas(pred[r, c], e95[r, c])
    d1 = d1 / N_PUBLIC_CELLS
    d0 = d0 / N_PUBLIC_CELLS
    p = cells[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    mean_i = p * d1 + (1.0 - p) * d0
    mean = float(mean_i.sum())
    var = float(np.sum(p * (1.0 - p) * (d1 - d0) ** 2))
    std = sqrt(max(var, 0.0))
    return {
        f"mean_delta_{prior}": mean,
        f"std_delta_{prior}": std,
        f"p05_delta_norm_{prior}": mean - 1.6448536269514722 * std,
        f"p95_delta_norm_{prior}": mean + 1.6448536269514722 * std,
        f"win_rate_norm_{prior}": normal_cdf(0.0, mean, std),
        f"e95_edge_or_better_norm_{prior}": normal_cdf(e170_edge_vs_mixmin(), mean, std),
        f"worse_than_e101_norm_{prior}": 1.0 - normal_cdf(e170_e101_delta(), mean, std),
        f"worse_than_mixmin_norm_{prior}": 1.0 - normal_cdf(e170_mixmin_delta(), mean, std),
    }


def e170_edge_vs_mixmin() -> float:
    import e170_e169_public_feedback_decoder as e170

    return float(e170.E95_EDGE_VS_MIXMIN)


def e170_e101_delta() -> float:
    import e170_e169_public_feedback_decoder as e170

    return float(e170.E101_DELTA_VS_E95)


def e170_mixmin_delta() -> float:
    import e170_e169_public_feedback_decoder as e170

    return float(e170.MIXMIN_DELTA_VS_E95)


def score_variant(
    policy: str,
    keep_matrix: np.ndarray,
    sample: pd.DataFrame,
    cells: pd.DataFrame,
    z95: np.ndarray,
    z169: np.ndarray,
    e95: np.ndarray,
    e154_axis: np.ndarray,
    e101_axis: np.ndarray,
    mixmin_axis: np.ndarray,
    bad_names: list[str],
    bad_basis: np.ndarray,
    rollback_cells: int,
) -> tuple[dict[str, Any], np.ndarray]:
    z = z95 + keep_matrix * (z169 - z95)
    pred = clip_prob(sigmoid(z))
    move = z - z95
    hard = e164.hard_breadth_metrics(pred, e95, e162_priors(sample))
    bad_cos = {f"cos_bad_{name}": cosine(move, bad_basis[i]) for i, name in enumerate(bad_names)}
    max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
    max_bad_cos = float(bad_cos[f"cos_bad_{max_bad_name}"])
    bad_energy, bad_resid = e165.span_energy(move.reshape(-1), bad_basis)
    rec: dict[str, Any] = {
        "policy": policy,
        "rollback_cells": int(rollback_cells),
        "expected_delta_focus_mean": float(hard["expected_delta_focus_mean"]),
        "moved_cells": int(hard["moved_cells"]),
        "moved_rows": int(hard["moved_rows"]),
        "cells_to_flip_expected": int(hard["cells_to_flip_expected_focus_mean"]),
        "top1_over_abs_expected": float(hard["top1_over_abs_expected"]),
        "cells_for_2e6_guard": int(hard["cells_for_2e6_guard"]),
        "cells_for_e95_edge": int(hard["cells_for_e95_edge"]),
        "support_prob_swing_weighted_focus": float(hard["support_prob_swing_weighted_focus_mean"]),
        "bad_span_energy": bad_energy,
        "bad_span_residual": bad_resid,
        "max_bad_axis": max_bad_name,
        "max_bad_cos": max_bad_cos,
        "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move))),
        "max_abs_logit_move_vs_e95": float(np.max(np.abs(move))),
        "q2s3_share_vs_e95": e164.target_group_share(move, {"Q2", "S3"}),
        "cos_e154_axis": cosine(move, e154_axis),
        "cos_e101_axis": cosine(move, e101_axis),
        "cos_mixmin_axis": cosine(move, mixmin_axis),
    }
    for prior in PRIORS:
        rec.update(prior_moments(cells, pred, e95, prior))
    rec.update(bad_cos)
    return rec, pred


_PRIORS_CACHE: dict[int, dict[str, np.ndarray]] = {}


def e162_priors(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    key = id(sample)
    if key not in _PRIORS_CACHE:
        import e162_branch_readability_flip_thresholds as e162

        _PRIORS_CACHE[key] = e162.prior_arrays(sample)
    return _PRIORS_CACHE[key]


def materialize(sample: pd.DataFrame, pred: np.ndarray, policy: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    safe = (
        policy.replace("top", "t")
        .replace("visible", "vis")
        .replace("swing", "sw")
        .replace("expected", "exp")
        .replace("positive", "pos")
        .replace("__", "_")
    )
    safe = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in safe)[:80]
    file_name = f"submission_e172_{safe}_{digest}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(OUT / file_name, index=False)
    return file_name


def run() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    e95 = load_prob(E95_FILE, sample)
    e169 = load_prob(E169_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e101 = load_prob(E101_FILE, sample)
    mixmin = load_prob(MIXMIN_FILE, sample)
    z95 = logit(e95)
    z169 = logit(e169)
    e154_axis = (logit(e154) - z95).reshape(-1)
    e101_axis = (logit(e101) - z95).reshape(-1)
    mixmin_axis = (logit(mixmin) - z95).reshape(-1)
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    cells = e171.build_cells()

    rows: list[dict[str, Any]] = []
    preds: dict[str, np.ndarray] = {}
    for spec in build_variant_specs(cells):
        keep_matrix = mask_to_matrix(cells, spec["mask"], spec["keep"])
        rec, pred = score_variant(
            str(spec["policy"]),
            keep_matrix,
            sample,
            cells,
            z95,
            z169,
            e95,
            e154_axis,
            e101_axis,
            mixmin_axis,
            bad_names,
            bad_basis,
            int(np.asarray(spec["mask"]).sum()),
        )
        rec["rollback_keep"] = float(spec["keep"])
        preds[str(spec["policy"])] = pred
        rows.append(rec)

    scan = pd.DataFrame(rows)
    baseline = scan[scan["policy"].eq("baseline_e169")].iloc[0]
    scan["delta_mean_visible_vs_e169"] = scan["mean_delta_visible_mean"] - float(baseline["mean_delta_visible_mean"])
    scan["delta_p95_visible_vs_e169"] = scan["p95_delta_norm_visible_mean"] - float(
        baseline["p95_delta_norm_visible_mean"]
    )
    scan["delta_worse_e101_visible_vs_e169"] = scan["worse_than_e101_norm_visible_mean"] - float(
        baseline["worse_than_e101_norm_visible_mean"]
    )
    scan["broad_body_retained"] = (
        scan["moved_cells"].ge(820)
        & scan["cells_to_flip_expected"].ge(24)
        & scan["expected_delta_focus_mean"].le(-8.0e-5)
    )
    scan["tail_repair"] = (
        scan["delta_p95_visible_vs_e169"].lt(-1.0e-6)
        & scan["delta_worse_e101_visible_vs_e169"].lt(-0.01)
    )
    scan["stress_gate"] = (
        scan["broad_body_retained"]
        & scan["tail_repair"]
        & scan["top1_over_abs_expected"].le(0.060)
        & scan["bad_span_energy"].lt(0.60)
        & scan["max_bad_cos"].lt(0.50)
        & scan["mean_abs_logit_move_vs_e95"].le(0.0030)
        & scan["q2s3_share_vs_e95"].le(0.40)
    )
    scan = scan.sort_values(
        ["stress_gate", "delta_p95_visible_vs_e169", "expected_delta_focus_mean"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    shortlist = scan[scan["stress_gate"].fillna(False)].copy()
    if not shortlist.empty:
        best_policy = str(shortlist.iloc[0]["policy"])
        shortlist.loc[shortlist["policy"].eq(best_policy), "materialized_file"] = materialize(
            sample, preds[best_policy], best_policy
        )
    scan.to_csv(SCAN_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    write_report(scan, shortlist, baseline)
    print(SCAN_OUT)
    print(SHORTLIST_OUT)
    print(REPORT_OUT)
    if not shortlist.empty and "materialized_file" in shortlist:
        for file_name in shortlist["materialized_file"].dropna().astype(str).tolist():
            print(OUT / file_name)


def write_report(scan: pd.DataFrame, shortlist: pd.DataFrame, baseline: pd.Series) -> None:
    cols = [
        "policy",
        "rollback_cells",
        "rollback_keep",
        "stress_gate",
        "expected_delta_focus_mean",
        "mean_delta_visible_mean",
        "delta_mean_visible_vs_e169",
        "p95_delta_norm_visible_mean",
        "delta_p95_visible_vs_e169",
        "worse_than_e101_norm_visible_mean",
        "delta_worse_e101_visible_vs_e169",
        "moved_cells",
        "cells_to_flip_expected",
        "top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_axis",
        "max_bad_cos",
        "q2s3_share_vs_e95",
        "materialized_file",
    ]
    top = scan.head(30).copy()
    report = f"""# E172 E169 Critical-Tail Rollback Probe

## Question

If E171 says E169's public-decisive top cells are visible-prior adverse, can we
roll those cells back toward E95 while preserving E169's broad body?

## Baseline E169

{md_table(pd.DataFrame([baseline.to_dict()]), cols, n=1)}

## Scan Summary

- variants scored: `{len(scan)}`.
- stress-gate variants: `{int(scan['stress_gate'].sum())}`.
- materialized files: `{int(shortlist['materialized_file'].notna().sum()) if not shortlist.empty and 'materialized_file' in shortlist else 0}`.

## Top Rows

{md_table(top, cols, n=30)}

## Stress-Gate Shortlist

{md_table(shortlist, cols, n=20)}

## Interpretation

- A useful rollback must reduce visible-prior p95/worse-than-E101 tail while
  keeping broad body breadth (`>=820` moved cells, `>=24` cells-to-flip, and
  focus expected edge `<= -8e-5`).
- If no stress-gate row exists, E171's critical-tail warning is diagnostic
  only: the visible-adverse cells cannot be removed cheaply without spending
  E169's broad-body edge.
- If a stress-gate row exists, it is a lower-risk E169 contrast, not proof that
  E169 itself is wrong. Public feedback should compare the original body claim
  against the tail-repaired body claim.
"""
    REPORT_OUT.write_text(report)


if __name__ == "__main__":
    run()
