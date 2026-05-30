#!/usr/bin/env python3
"""E182: refreshed current-anchor binary-world stress.

E181 found that inherited binary hidden-label worlds, when re-ranked by current
public anchors, are a counterprior against E176 and favor E154/E144. The obvious
objection is that those worlds were inherited from an older frontier-box pool.

This audit regenerates the binary-world stress from the current known public
anchors and explicitly asks for candidate delta ranges under the same residual
budget. It is a falsification test, not a submission generator.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
import time
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, TARGETS, known_public_table, load_sub, locate  # noqa: E402
from public_lb_inverse_feasibility import known_predictions, load_prob  # noqa: E402
from public_lb_structural_prior_stress import build_constraints, markdown_table  # noqa: E402
from public_lb_binary_inverse_stress import candidate_delta_coeff, residuals_from_x  # noqa: E402


FIT_OUT = OUT / "e182_current_anchor_binary_world_refresh_fit.csv"
RANGE_OUT = OUT / "e182_current_anchor_binary_world_refresh_ranges.csv"
PRESSURE_OUT = OUT / "e182_current_anchor_binary_world_refresh_pressure.csv"
WORLD_OUT = OUT / "e182_current_anchor_binary_world_refresh_worlds.csv"
LABEL_NPZ = OUT / "e182_current_anchor_binary_world_refresh_labels.npz"
REPORT_OUT = OUT / "e182_current_anchor_binary_world_refresh_report.md"


BASE_FILE = "submission_e95_hardtail_541e3973.csv"
FRONTIER_RAW05_GAP = 0.5775263072 - 0.5774393210
FIT_TIME_LIMIT = 6.0
RANGE_TIME_LIMIT = 6.0
PRESSURE_TIME_LIMIT = 5.0
PRESSURE_ALPHA = 0.010
RESIDUAL_TOL = 1.0e-8

SCENARIOS = [
    {
        "scenario": "global_t010",
        "global_band": 0.10,
        "subject_target_band": None,
        "interpretation": "current anchors with global target prior only",
    },
    {
        "scenario": "global_t010_subject_t020",
        "global_band": 0.10,
        "subject_target_band": 0.20,
        "interpretation": "current anchors with weak subject-target prior",
    },
    {
        "scenario": "global_t010_subject_t010",
        "global_band": 0.10,
        "subject_target_band": 0.10,
        "interpretation": "current anchors with tight subject-target prior",
    },
]

LIVE_CANDIDATES = [
    ("e176", "visible_body_q2_underopen", "submission_e176_abl_q2_to0p75_91e49725.csv"),
    ("e174", "max_edge_broad_reopen", "submission_e174_ro_fc_top75_to1p0_95638e73.csv"),
    ("e172", "visible_tail_repair", "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"),
    ("e154", "repaired_all_four_branch", "submission_e154_s3repair_9f2e2e73.csv"),
    ("e144", "active_boundary_branch", "submission_e144_activeboundary_d7b4b331.csv"),
]
PRESSURE_CANDIDATES = {"e176", "e154", "e144"}


def as_bounds(bounds: list[tuple[float | None, float | None]]) -> Bounds:
    lb = np.array([0.0 if lo is None else lo for lo, _ in bounds], dtype=np.float64)
    ub = np.array([np.inf if hi is None else hi for _, hi in bounds], dtype=np.float64)
    return Bounds(lb, ub)


def label_hash(labels: np.ndarray) -> str:
    bits = np.asarray(np.rint(labels), dtype=np.uint8)
    return hashlib.sha1(bits.tobytes()).hexdigest()[:12]


def safe_float(value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out


def safe_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def has_incumbent(res: object) -> bool:
    x = getattr(res, "x", None)
    return x is not None and bool(np.all(np.isfinite(x)))


def frontier_box_bounds(bounds: list[tuple[float | None, float | None]], m: int, k: int) -> list[tuple[float | None, float | None]]:
    out = list(bounds)
    for j in range(k):
        out[m + j] = (0.0, FRONTIER_RAW05_GAP)
    return out


def solve_binary(
    c: np.ndarray,
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    bounds: list[tuple[float | None, float | None]],
    m: int,
    time_limit: float,
) -> tuple[object, float]:
    lower = np.full(len(b_ub), -np.inf, dtype=np.float64)
    integrality = np.r_[np.ones(m, dtype=np.int8), np.zeros(len(c) - m, dtype=np.int8)]
    start = time.time()
    res = milp(
        c,
        integrality=integrality,
        bounds=as_bounds(bounds),
        constraints=LinearConstraint(a_ub, lower, b_ub),
        options={"time_limit": time_limit, "mip_rel_gap": 1.0e-8},
    )
    return res, time.time() - start


def slack_sum(x: np.ndarray, m: int) -> float:
    return float(np.sum(x[m:]))


def scenario_constraints(
    spec: dict[str, Any],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    y_public: np.ndarray,
    const: np.ndarray,
    b: np.ndarray,
    k: int,
    m: int,
) -> tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]:
    model_view = type("BinaryModelView", (), {"y": y_public, "const": const, "b": b, "k": k, "m": m})()
    a_ub, b_ub, bounds = build_constraints(
        model_view,
        train,
        sample,
        spec["global_band"],
        spec["subject_target_band"],
    )
    return a_ub, b_ub, frontier_box_bounds(bounds, m, k)


def solve_fit(
    spec: dict[str, Any],
    train: pd.DataFrame,
    sample: pd.DataFrame,
    y_public: np.ndarray,
    const: np.ndarray,
    b: np.ndarray,
    k: int,
    m: int,
) -> tuple[dict[str, Any], np.ndarray | None, tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]]:
    a_ub, b_ub, bounds = scenario_constraints(spec, train, sample, y_public, const, b, k, m)
    c = np.r_[np.zeros(m), np.ones(k)]
    res, elapsed = solve_binary(c, a_ub, b_ub, bounds, m, FIT_TIME_LIMIT)
    row: dict[str, Any] = {
        "scenario": spec["scenario"],
        "global_band": spec["global_band"],
        "subject_target_band": spec["subject_target_band"],
        "interpretation": spec["interpretation"],
        "solver_success": bool(getattr(res, "success", False)),
        "status": safe_int(getattr(res, "status", -999)),
        "message": str(getattr(res, "message", "")),
        "mip_gap": safe_float(getattr(res, "mip_gap", np.nan)),
        "mip_dual_bound": safe_float(getattr(res, "mip_dual_bound", np.nan)),
        "mip_node_count": safe_int(getattr(res, "mip_node_count", -1)),
        "elapsed_sec": elapsed,
        "time_limit": FIT_TIME_LIMIT,
        "has_incumbent": has_incumbent(res),
        "slack_upper_bound": FRONTIER_RAW05_GAP,
    }
    if not has_incumbent(res):
        return row, None, (a_ub, b_ub, bounds)
    x = np.asarray(res.x, dtype=np.float64)
    labels = np.rint(x[:m]).astype(np.uint8)
    resid = residuals_from_x(const, b, y_public, x, m)
    row.update(
        {
            "world_id": label_hash(labels),
            "fit_objective_value": safe_float(getattr(res, "fun", np.nan)),
            "slack_sum": slack_sum(x, m),
            "sum_abs_residual": float(np.abs(resid).sum()),
            "max_abs_residual": float(np.abs(resid).max()),
            "mean_abs_residual": float(np.abs(resid).mean()),
            "max_residual_over_frontier_raw05_gap": float(np.abs(resid).max() / FRONTIER_RAW05_GAP),
            "positive_cell_count": int(labels.sum()),
            "frontier_scale_fit": bool(np.abs(resid).max() <= FRONTIER_RAW05_GAP + 1.0e-10),
        }
    )
    return row, x, (a_ub, b_ub, bounds)


def add_slack_budget(
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    m: int,
    k: int,
    budget: float,
) -> tuple[np.ndarray, np.ndarray]:
    row = np.r_[np.zeros(m), np.ones(k)][None, :]
    return np.vstack([a_ub, row]), np.r_[b_ub, budget + RESIDUAL_TOL]


def candidate_coefficients(sample: pd.DataFrame) -> dict[str, dict[str, Any]]:
    base_prob = load_prob(BASE_FILE, sample)
    out: dict[str, dict[str, Any]] = {}
    for name, role, file_name in LIVE_CANDIDATES:
        if locate(file_name) is None:
            continue
        prob = load_prob(file_name, sample)
        const, coeff = candidate_delta_coeff(prob, base_prob)
        out[name] = {"role": role, "file": file_name, "const": const, "coeff": coeff}
    return out


def solve_candidate_ranges(
    spec: dict[str, Any],
    fit_row: dict[str, Any],
    fit_x: np.ndarray,
    constraints: tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]],
    coeffs: dict[str, dict[str, Any]],
    const_anchor: np.ndarray,
    b_anchor: np.ndarray,
    y_public: np.ndarray,
    m: int,
    k: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[np.ndarray]]:
    a_ub, b_ub, bounds = constraints
    range_a, range_b = add_slack_budget(a_ub, b_ub, m, k, float(fit_row["slack_sum"]))
    range_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    labels_out: list[np.ndarray] = []
    for candidate, meta in coeffs.items():
        for direction, sign in [("min", 1.0), ("max", -1.0)]:
            c = np.r_[sign * meta["coeff"], np.zeros(k)]
            res, elapsed = solve_binary(c, range_a, range_b, bounds, m, RANGE_TIME_LIMIT)
            row: dict[str, Any] = {
                "scenario": spec["scenario"],
                "candidate": candidate,
                "role": meta["role"],
                "file": meta["file"],
                "direction": direction,
                "solver_success": bool(getattr(res, "success", False)),
                "status": safe_int(getattr(res, "status", -999)),
                "message": str(getattr(res, "message", "")),
                "mip_gap": safe_float(getattr(res, "mip_gap", np.nan)),
                "mip_dual_bound": safe_float(getattr(res, "mip_dual_bound", np.nan)),
                "mip_node_count": safe_int(getattr(res, "mip_node_count", -1)),
                "elapsed_sec": elapsed,
                "time_limit": RANGE_TIME_LIMIT,
                "has_incumbent": has_incumbent(res),
                "fit_slack_budget": float(fit_row["slack_sum"]),
            }
            if has_incumbent(res):
                x = np.asarray(res.x, dtype=np.float64)
                labels = np.rint(x[:m]).astype(np.uint8)
                resid = residuals_from_x(const_anchor, b_anchor, y_public, x, m)
                delta = float(meta["const"] + meta["coeff"] @ labels)
                row.update(
                    {
                        "world_id": label_hash(labels),
                        "delta_vs_e95": delta,
                        "slack_sum": slack_sum(x, m),
                        "sum_abs_residual": float(np.abs(resid).sum()),
                        "max_abs_residual": float(np.abs(resid).max()),
                        "mean_abs_residual": float(np.abs(resid).mean()),
                        "frontier_scale_fit": bool(np.abs(resid).max() <= FRONTIER_RAW05_GAP + 1.0e-10),
                        "positive_cell_count": int(labels.sum()),
                        "better_than_e95": bool(delta < 0.0),
                    }
                )
                world_rows.append(
                    {
                        "scenario": spec["scenario"],
                        "objective": f"{candidate}_{direction}",
                        "candidate": candidate,
                        "direction": direction,
                        "world_id": row["world_id"],
                        "delta_vs_e95": delta,
                        "sum_abs_residual": row["sum_abs_residual"],
                        "max_abs_residual": row["max_abs_residual"],
                        "slack_sum": row["slack_sum"],
                        "positive_cell_count": row["positive_cell_count"],
                    }
                )
                labels_out.append(labels)
            range_rows.append(row)
    return range_rows, world_rows, labels_out


def solve_pressure_worlds(
    spec: dict[str, Any],
    constraints: tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]],
    coeffs: dict[str, dict[str, Any]],
    const_anchor: np.ndarray,
    b_anchor: np.ndarray,
    y_public: np.ndarray,
    m: int,
    k: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[np.ndarray]]:
    """Solve softer objective-pressure worlds when exact range MILPs are sparse."""
    a_ub, b_ub, bounds = constraints
    slack_obj = np.r_[np.zeros(m), np.ones(k)]
    pressure_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    labels_out: list[np.ndarray] = []
    for candidate, meta in coeffs.items():
        if candidate not in PRESSURE_CANDIDATES:
            continue
        for direction, sign in [("min", 1.0), ("max", -1.0)]:
            c = slack_obj + PRESSURE_ALPHA * np.r_[sign * meta["coeff"], np.zeros(k)]
            res, elapsed = solve_binary(c, a_ub, b_ub, bounds, m, PRESSURE_TIME_LIMIT)
            row: dict[str, Any] = {
                "scenario": spec["scenario"],
                "candidate": candidate,
                "role": meta["role"],
                "file": meta["file"],
                "direction": direction,
                "solver_success": bool(getattr(res, "success", False)),
                "status": safe_int(getattr(res, "status", -999)),
                "message": str(getattr(res, "message", "")),
                "mip_gap": safe_float(getattr(res, "mip_gap", np.nan)),
                "mip_dual_bound": safe_float(getattr(res, "mip_dual_bound", np.nan)),
                "mip_node_count": safe_int(getattr(res, "mip_node_count", -1)),
                "elapsed_sec": elapsed,
                "time_limit": PRESSURE_TIME_LIMIT,
                "has_incumbent": has_incumbent(res),
                "pressure_alpha": PRESSURE_ALPHA,
            }
            if has_incumbent(res):
                x = np.asarray(res.x, dtype=np.float64)
                labels = np.rint(x[:m]).astype(np.uint8)
                resid = residuals_from_x(const_anchor, b_anchor, y_public, x, m)
                delta = float(meta["const"] + meta["coeff"] @ labels)
                row.update(
                    {
                        "world_id": label_hash(labels),
                        "delta_vs_e95": delta,
                        "slack_sum": slack_sum(x, m),
                        "sum_abs_residual": float(np.abs(resid).sum()),
                        "max_abs_residual": float(np.abs(resid).max()),
                        "mean_abs_residual": float(np.abs(resid).mean()),
                        "frontier_scale_fit": bool(np.abs(resid).max() <= FRONTIER_RAW05_GAP + 1.0e-10),
                        "positive_cell_count": int(labels.sum()),
                        "better_than_e95": bool(delta < 0.0),
                    }
                )
                world_rows.append(
                    {
                        "scenario": spec["scenario"],
                        "objective": f"pressure_{candidate}_{direction}",
                        "candidate": candidate,
                        "direction": direction,
                        "world_id": row["world_id"],
                        "delta_vs_e95": delta,
                        "sum_abs_residual": row["sum_abs_residual"],
                        "max_abs_residual": row["max_abs_residual"],
                        "slack_sum": row["slack_sum"],
                        "positive_cell_count": row["positive_cell_count"],
                    }
                )
                labels_out.append(labels)
            pressure_rows.append(row)
    return pressure_rows, world_rows, labels_out


def summarize_ranges(range_df: pd.DataFrame) -> pd.DataFrame:
    if range_df.empty or "delta_vs_e95" not in range_df.columns:
        return pd.DataFrame()
    ok = range_df[range_df["has_incumbent"]].copy()
    pivot = (
        ok.pivot_table(
            index=["scenario", "candidate", "role", "file"],
            columns="direction",
            values="delta_vs_e95",
            aggfunc="first",
        )
        .reset_index()
        .rename(columns={"min": "min_delta_vs_e95", "max": "max_delta_vs_e95"})
    )
    for col in ["min_delta_vs_e95", "max_delta_vs_e95"]:
        if col not in pivot.columns:
            pivot[col] = np.nan
    pivot["range_width"] = pivot["max_delta_vs_e95"] - pivot["min_delta_vs_e95"]
    pivot["crosses_zero"] = (pivot["min_delta_vs_e95"] <= 0.0) & (pivot["max_delta_vs_e95"] >= 0.0)
    pivot["one_sided_negative"] = pivot["max_delta_vs_e95"] < 0.0
    pivot["one_sided_positive"] = pivot["min_delta_vs_e95"] > 0.0
    pivot = pivot.sort_values(["scenario", "min_delta_vs_e95", "candidate"]).reset_index(drop=True)
    return pivot


def summarize_pressure(pressure_df: pd.DataFrame) -> pd.DataFrame:
    if pressure_df.empty or "delta_vs_e95" not in pressure_df.columns:
        return pd.DataFrame()
    ok = pressure_df[pressure_df["has_incumbent"]].copy()
    pivot = (
        ok.pivot_table(
            index=["scenario", "candidate", "role", "file"],
            columns="direction",
            values="delta_vs_e95",
            aggfunc="first",
        )
        .reset_index()
        .rename(columns={"min": "pressure_min_delta_vs_e95", "max": "pressure_max_delta_vs_e95"})
    )
    for col in ["pressure_min_delta_vs_e95", "pressure_max_delta_vs_e95"]:
        if col not in pivot.columns:
            pivot[col] = np.nan
    pivot["pressure_range_width"] = pivot["pressure_max_delta_vs_e95"] - pivot["pressure_min_delta_vs_e95"]
    pivot["pressure_crosses_zero"] = (pivot["pressure_min_delta_vs_e95"] <= 0.0) & (
        pivot["pressure_max_delta_vs_e95"] >= 0.0
    )
    pivot["pressure_one_sided_negative"] = pivot["pressure_max_delta_vs_e95"] < 0.0
    pivot["pressure_one_sided_positive"] = pivot["pressure_min_delta_vs_e95"] > 0.0
    pivot = pivot.sort_values(["scenario", "pressure_min_delta_vs_e95", "candidate"]).reset_index(drop=True)
    return pivot


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 80) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return markdown_table(view.head(n))


def main() -> None:
    sample = load_sub(A2C8)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    known = known_public_table().copy().reset_index(drop=True)
    known, pos_loss, neg_loss = known_predictions(sample)
    y_public = known["public_lb"].to_numpy(dtype=np.float64)
    k, m = pos_loss.shape
    const = neg_loss.mean(axis=1)
    b = (pos_loss - neg_loss) / float(m)
    coeffs = candidate_coefficients(sample)

    fit_rows: list[dict[str, Any]] = []
    range_rows: list[dict[str, Any]] = []
    pressure_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    label_rows: list[np.ndarray] = []

    for spec in SCENARIOS:
        fit_row, fit_x, constraints = solve_fit(spec, train, sample, y_public, const, b, k, m)
        fit_rows.append(fit_row)
        if fit_x is None:
            continue
        fit_labels = np.rint(fit_x[:m]).astype(np.uint8)
        world_rows.append(
            {
                "scenario": spec["scenario"],
                "objective": "fit",
                "candidate": "fit",
                "direction": "fit",
                "world_id": fit_row["world_id"],
                "delta_vs_e95": np.nan,
                "sum_abs_residual": fit_row["sum_abs_residual"],
                "max_abs_residual": fit_row["max_abs_residual"],
                "slack_sum": fit_row["slack_sum"],
                "positive_cell_count": fit_row["positive_cell_count"],
            }
        )
        label_rows.append(fit_labels)
        rr, ww, ll = solve_candidate_ranges(spec, fit_row, fit_x, constraints, coeffs, const, b, y_public, m, k)
        range_rows.extend(rr)
        world_rows.extend(ww)
        label_rows.extend(ll)
        pr, pw, pl = solve_pressure_worlds(spec, constraints, coeffs, const, b, y_public, m, k)
        pressure_rows.extend(pr)
        world_rows.extend(pw)
        label_rows.extend(pl)

    fit_df = pd.DataFrame(fit_rows)
    range_df = pd.DataFrame(range_rows)
    pressure_df = pd.DataFrame(pressure_rows)
    world_df = pd.DataFrame(world_rows)
    summary_df = summarize_ranges(range_df)
    pressure_summary = summarize_pressure(pressure_df)

    fit_df.to_csv(FIT_OUT, index=False)
    range_df.to_csv(RANGE_OUT, index=False)
    pressure_df.to_csv(PRESSURE_OUT, index=False)
    world_df.to_csv(WORLD_OUT, index=False)
    if label_rows:
        labels = np.vstack(label_rows).astype(np.uint8)
    else:
        labels = np.empty((0, m), dtype=np.uint8)
    np.savez_compressed(LABEL_NPZ, labels=labels, targets=np.array(TARGETS, dtype=object))

    live_cols = [
        "scenario",
        "candidate",
        "min_delta_vs_e95",
        "max_delta_vs_e95",
        "range_width",
        "crosses_zero",
        "one_sided_negative",
        "one_sided_positive",
    ]
    pressure_cols = [
        "scenario",
        "candidate",
        "pressure_min_delta_vs_e95",
        "pressure_max_delta_vs_e95",
        "pressure_range_width",
        "pressure_crosses_zero",
        "pressure_one_sided_negative",
        "pressure_one_sided_positive",
    ]
    fit_cols = [
        "scenario",
        "has_incumbent",
        "slack_sum",
        "sum_abs_residual",
        "max_abs_residual",
        "positive_cell_count",
        "frontier_scale_fit",
        "elapsed_sec",
    ]
    exact_incumbent_rate = float(range_df["has_incumbent"].mean()) if not range_df.empty else float("nan")
    if pressure_summary.empty:
        e176_cross = e154_cross = e144_cross = float("nan")
    else:
        e176_cross = float(pressure_summary[pressure_summary["candidate"].eq("e176")]["pressure_crosses_zero"].mean())
        e154_cross = float(pressure_summary[pressure_summary["candidate"].eq("e154")]["pressure_crosses_zero"].mean())
        e144_cross = float(pressure_summary[pressure_summary["candidate"].eq("e144")]["pressure_crosses_zero"].mean())

    report = f"""# E182 Current-Anchor Binary-World Refresh

## Question

E181 says inherited binary worlds are a counterprior against E176 and favor
E154/E144. Is that still true if the binary-world stress is regenerated from
the current public anchors and the E176/E154/E144 objectives are asked
explicitly?

No submission is created.

## Result In One Sentence

Refreshed current-anchor worlds do not certify E176, E154, or E144 one-sided:
under objective-pressure worlds E176/E154/E144 cross zero in
`{e176_cross:.3f}` / `{e154_cross:.3f}` / `{e144_cross:.3f}` of scenarios. The
strict residual-budget range solver only found incumbents in
`{exact_incumbent_rate:.3f}` of rows, which is itself a warning that this inverse
problem is still hard at frontier scale. E181's counterprior remains useful, but
it is not enough to promote E154/E144 as certified replacements.

## Scenario Fits

{md(fit_df, fit_cols, n=20)}

## Candidate Ranges Versus E95

{md(summary_df, live_cols, n=60)}

## Objective-Pressure Worlds Versus E95

{md(pressure_summary, pressure_cols, n=40)}

## Raw Range Solver Rows

{md(range_df.sort_values(['scenario', 'candidate', 'direction']), ['scenario', 'candidate', 'direction', 'has_incumbent', 'delta_vs_e95', 'sum_abs_residual', 'max_abs_residual', 'slack_sum', 'status', 'elapsed_sec'], n=80)}

## Raw Pressure Solver Rows

{md(pressure_df.sort_values(['scenario', 'candidate', 'direction']), ['scenario', 'candidate', 'direction', 'has_incumbent', 'delta_vs_e95', 'sum_abs_residual', 'max_abs_residual', 'slack_sum', 'status', 'elapsed_sec'], n=80)}

## Interpretation

- E181's inherited-world ranking was a useful counterprior, but E182 shows it is
  not strong enough to promote E154/E144 as certified replacements. Under a
  refreshed current-anchor stress, objective pressure can produce both favorable
  and adverse worlds for E176, E154, and E144.
- The plateau law survives: current public anchors and structural priors still
  underidentify frontier-scale candidate signs. The hidden label space can
  support E176-like and E154/E144-like worlds depending on objective pressure.
- E176 should still be described as a conditional visible-body/Q2-underopen
  sensor, not a certified improvement. E154/E144 become the main alternate
  worldview to test, but E182 says they need either public feedback or an
  additional non-public selector before promotion.

## Decision

No new submission. The next public candidate remains a worldview choice rather
than an expected-score certificate. If spending one slot to test the broad
visible-body law, use E176 and decode with E177/E179/E180/E181/E182. If the
question is binary-world repaired-branch validity, E154 or E144 should first get
a fresh decoder and public-feedback interpretation comparable to E177.
"""
    REPORT_OUT.write_text(report)

    for path in [FIT_OUT, RANGE_OUT, PRESSURE_OUT, WORLD_OUT, LABEL_NPZ, REPORT_OUT]:
        print(path)


if __name__ == "__main__":
    main()
