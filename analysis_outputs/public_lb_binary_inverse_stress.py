from __future__ import annotations

from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, TARGETS, locate, load_sub  # noqa: E402
from public_lb_inverse_feasibility import CANDIDATES, known_predictions, load_prob  # noqa: E402
from public_lb_structural_prior_stress import build_constraints, markdown_table  # noqa: E402


FIT_OUT = OUT / "public_lb_binary_inverse_stress_fit.csv"
RANGE_OUT = OUT / "public_lb_binary_inverse_stress_ranges.csv"
REPORT_OUT = OUT / "public_lb_binary_inverse_stress_report.md"


FIT_TIME_LIMIT = 18.0
RANGE_TIME_LIMIT = 4.0
FRONTIER_RAW05_GAP = 0.5775263072 - 0.5774393210

SCENARIOS = [
    {
        "scenario": "binary_no_prior",
        "global_band": None,
        "subject_target_band": None,
        "range_scan": True,
    },
    {
        "scenario": "binary_global_t005",
        "global_band": 0.05,
        "subject_target_band": None,
        "range_scan": False,
    },
    {
        "scenario": "binary_global_t010_subject_t010",
        "global_band": 0.10,
        "subject_target_band": 0.10,
        "range_scan": True,
    },
]

RANGE_ROLES = {
    "pair_sensor_1bb",
    "pair_sensor_1bb_s0p65",
    "pair_sensor_6b",
    "mixmin_0c916",
    "inverse7blend_1040",
    "raw05_known",
}


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def losses(prob: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip_prob(prob)
    return -np.log(p).reshape(-1), -np.log(1.0 - p).reshape(-1)


def candidate_delta_coeff(candidate_prob: np.ndarray, base_prob: np.ndarray) -> tuple[float, np.ndarray]:
    cand_pos, cand_neg = losses(candidate_prob)
    base_pos, base_neg = losses(base_prob)
    const = float(np.mean(cand_neg - base_neg))
    coeff = (cand_pos - cand_neg - base_pos + base_neg) / float(candidate_prob.size)
    return const, coeff


def as_bounds(bounds: list[tuple[float | None, float | None]]) -> Bounds:
    lb = np.array([0.0 if lo is None else lo for lo, _ in bounds], dtype=np.float64)
    ub = np.array([np.inf if hi is None else hi for _, hi in bounds], dtype=np.float64)
    return Bounds(lb, ub)


def solve_binary_milp(
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
        options={"time_limit": time_limit, "mip_rel_gap": 1e-8},
    )
    return res, time.time() - start


def residuals_from_x(const: np.ndarray, b: np.ndarray, y_public: np.ndarray, x: np.ndarray, m: int) -> np.ndarray:
    return const + b @ x[:m] - y_public


def has_incumbent(res: object) -> bool:
    x = getattr(res, "x", None)
    return x is not None and bool(np.all(np.isfinite(x)))


def safe_float(value: object) -> float:
    if value is None:
        return float("nan")
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def safe_int(value: object) -> int:
    if value is None:
        return -1
    try:
        return int(value)
    except (TypeError, ValueError):
        return -1


def main() -> None:
    sample = load_sub(A2C8)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    known, pos_loss, neg_loss = known_predictions(sample)
    y_public = known["public_lb"].to_numpy(dtype=np.float64)
    k, m = pos_loss.shape
    const = neg_loss.mean(axis=1)
    b = (pos_loss - neg_loss) / float(m)
    base_prob = load_prob(A2C8, sample)

    fit_rows = []
    range_rows = []
    fit_cache: dict[str, tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]], float]] = {}

    for spec in SCENARIOS:
        a_ub, b_ub, bounds = build_constraints(
            type("BinaryModelView", (), {"y": y_public, "const": const, "b": b, "k": k, "m": m})(),
            train,
            sample,
            spec["global_band"],
            spec["subject_target_band"],
        )
        c = np.r_[np.zeros(m), np.ones(k)]
        res, elapsed = solve_binary_milp(c, a_ub, b_ub, bounds, m, FIT_TIME_LIMIT)
        row = {
            "scenario": spec["scenario"],
            "global_band": spec["global_band"],
            "subject_target_band": spec["subject_target_band"],
            "solver_success": bool(getattr(res, "success", False)),
            "status": safe_int(getattr(res, "status", -999)),
            "message": str(getattr(res, "message", "")),
            "mip_gap": safe_float(getattr(res, "mip_gap", np.nan)),
            "mip_dual_bound": safe_float(getattr(res, "mip_dual_bound", np.nan)),
            "mip_node_count": safe_int(getattr(res, "mip_node_count", -1)),
            "elapsed_sec": elapsed,
            "fit_time_limit": FIT_TIME_LIMIT,
            "has_incumbent": has_incumbent(res),
        }
        if has_incumbent(res):
            resid = residuals_from_x(const, b, y_public, res.x, m)
            row.update(
                {
                    "fit_sum_slack_objective": float(getattr(res, "fun", np.nan)),
                    "sum_abs_residual": float(np.sum(np.abs(resid))),
                    "max_abs_residual": float(np.max(np.abs(resid))),
                    "mean_abs_residual": float(np.mean(np.abs(resid))),
                    "positive_cell_count": int(round(float(np.sum(res.x[:m])))),
                    "max_residual_over_frontier_raw05_gap": float(np.max(np.abs(resid)) / FRONTIER_RAW05_GAP),
                }
            )
            fit_cache[spec["scenario"]] = (a_ub, b_ub, bounds, float(np.sum(np.abs(resid))))
        fit_rows.append(row)

        if not spec["range_scan"] or not has_incumbent(res):
            continue
        residual_budget = float(np.sum(np.abs(residuals_from_x(const, b, y_public, res.x, m))) + 1e-8)
        sum_slack_row = np.r_[np.zeros(m), np.ones(k)][None, :]
        range_a_ub = np.vstack([a_ub, sum_slack_row])
        range_b_ub = np.r_[b_ub, residual_budget]
        for role, file_name in CANDIDATES:
            if role not in RANGE_ROLES or locate(file_name) is None:
                continue
            cand_prob = load_prob(file_name, sample)
            delta_const, delta_coeff = candidate_delta_coeff(cand_prob, base_prob)
            for direction, sign in [("min", 1.0), ("max", -1.0)]:
                obj = np.r_[sign * delta_coeff, np.zeros(k)]
                rres, relapsed = solve_binary_milp(obj, range_a_ub, range_b_ub, bounds, m, RANGE_TIME_LIMIT)
                out = {
                    "scenario": spec["scenario"],
                    "role": role,
                    "file": file_name,
                    "direction": direction,
                    "solver_success": bool(getattr(rres, "success", False)),
                    "status": safe_int(getattr(rres, "status", -999)),
                    "message": str(getattr(rres, "message", "")),
                    "mip_gap": safe_float(getattr(rres, "mip_gap", np.nan)),
                    "mip_node_count": safe_int(getattr(rres, "mip_node_count", -1)),
                    "elapsed_sec": relapsed,
                    "range_time_limit": RANGE_TIME_LIMIT,
                    "residual_budget": residual_budget,
                    "has_incumbent": has_incumbent(rres),
                }
                if has_incumbent(rres):
                    rr = residuals_from_x(const, b, y_public, rres.x, m)
                    delta = float(delta_const + delta_coeff @ rres.x[:m])
                    out.update(
                        {
                            "candidate_delta_vs_a2c8": delta,
                            "sum_abs_residual": float(np.sum(np.abs(rr))),
                            "max_abs_residual": float(np.max(np.abs(rr))),
                            "budget_ok": bool(np.sum(np.abs(rr)) <= residual_budget + 1e-7),
                            "positive_cell_count": int(round(float(np.sum(rres.x[:m])))),
                        }
                    )
                range_rows.append(out)

    fit_df = pd.DataFrame(fit_rows)
    range_df = pd.DataFrame(range_rows)
    fit_df.to_csv(FIT_OUT, index=False)
    range_df.to_csv(RANGE_OUT, index=False)

    if not range_df.empty and "candidate_delta_vs_a2c8" in range_df.columns:
        pivot = (
            range_df[range_df["has_incumbent"]]
            .pivot_table(
                index=["scenario", "role", "file"],
                columns="direction",
                values="candidate_delta_vs_a2c8",
                aggfunc="first",
            )
            .reset_index()
        )
        if "min" not in pivot.columns:
            pivot["min"] = np.nan
        if "max" not in pivot.columns:
            pivot["max"] = np.nan
        pivot["incumbent_crosses_zero"] = (pivot["min"] <= 0.0) & (pivot["max"] >= 0.0)
        pivot["incumbent_one_sided_negative"] = pivot["max"] < 0.0
        pivot["incumbent_one_sided_positive"] = pivot["min"] > 0.0
        pivot = pivot.sort_values(["scenario", "min"]).reset_index(drop=True)
    else:
        pivot = pd.DataFrame()

    fit_view_cols = [
        "scenario",
        "solver_success",
        "fit_sum_slack_objective",
        "max_abs_residual",
        "max_residual_over_frontier_raw05_gap",
        "mip_gap",
        "elapsed_sec",
        "message",
    ]
    fit_view_cols = [c for c in fit_view_cols if c in fit_df.columns]
    lines = [
        "# Public LB Binary Inverse Stress",
        "",
        "Question: does enforcing binary hidden labels for the all-test public world make known LB anchors precise enough to rank current candidates?",
        "",
        "## Fit Quality",
        "",
        markdown_table(fit_df[fit_view_cols]),
        "",
        "## Candidate Incumbent Ranges",
        "",
        markdown_table(pivot),
        "",
        "## Decision",
        "",
    ]
    if not fit_df.empty and "max_abs_residual" in fit_df.columns:
        best_max_resid = float(fit_df["max_abs_residual"].min())
        lines.append(f"- Best incumbent max absolute LB residual: `{best_max_resid:.9f}`.")
        lines.append(f"- A2C8-vs-raw05 public gap: `{FRONTIER_RAW05_GAP:.9f}`.")
        if best_max_resid > FRONTIER_RAW05_GAP:
            lines.append(
                "- The binary all-test inverse assumption is not precise enough at the frontier scale; its anchor residual is larger than the best-known public edge."
            )
        else:
            lines.append("- At least one binary all-test incumbent fits anchors within the raw05/a2c8 public gap.")
    if not pivot.empty:
        unobserved = pivot[pivot["role"] != "raw05_known"]
        lines.append(f"- Unobserved incumbent range rows: `{len(unobserved)}`.")
        lines.append(f"- Incumbent cross-zero rows: `{int(unobserved['incumbent_crosses_zero'].sum())}`.")
        lines.append(f"- Incumbent one-sided improvement rows: `{int(unobserved['incumbent_one_sided_negative'].sum())}`.")
        if int(unobserved["incumbent_one_sided_negative"].sum()) == 0:
            lines.append("- No representative unobserved candidate gets a binary-inverse one-sided improvement signal.")
    lines.append("- Treat this as a stress test, not exact public-set reconstruction: optimizers may hit time limits, and all-test public membership may itself be the wrong hidden-world assumption.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(REPORT_OUT)
    print(
        {
            "fit_rows": len(fit_df),
            "range_rows": len(range_df),
            "best_max_abs_residual": float(fit_df["max_abs_residual"].min()) if "max_abs_residual" in fit_df else None,
            "frontier_raw05_gap": FRONTIER_RAW05_GAP,
            "unobserved_cross_zero": int(
                pivot[pivot["role"] != "raw05_known"]["incumbent_crosses_zero"].sum()
            )
            if not pivot.empty
            else 0,
        }
    )


if __name__ == "__main__":
    main()
