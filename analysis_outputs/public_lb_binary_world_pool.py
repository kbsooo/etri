from __future__ import annotations

from pathlib import Path
import hashlib
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
from public_lb_binary_inverse_stress import candidate_delta_coeff, residuals_from_x  # noqa: E402


WORLD_OUT = OUT / "public_lb_binary_world_pool_worlds.csv"
TARGET_OUT = OUT / "public_lb_binary_world_pool_target_priors.csv"
DELTA_OUT = OUT / "public_lb_binary_world_pool_candidate_deltas.csv"
SUMMARY_OUT = OUT / "public_lb_binary_world_pool_summary.csv"
NPZ_OUT = OUT / "public_lb_binary_world_pool_labels.npz"
REPORT_OUT = OUT / "public_lb_binary_world_pool_report.md"


TIME_LIMIT = 7.0
FRONTIER_RAW05_GAP = 0.5775263072 - 0.5774393210
GLOBAL_BAND = 0.10
SUBJECT_TARGET_BAND = 0.10
OBJECTIVE_ALPHA = 0.02
RANDOM_ALPHA = 0.015
RANDOM_SEED = 20260528

POOL_ROLES = [
    "pair_sensor_1bb",
    "pair_sensor_1bb_s0p65",
    "pair_sensor_6b",
    "mixmin_0c916",
    "inverse7blend_1040",
]


def as_bounds(bounds: list[tuple[float | None, float | None]]) -> Bounds:
    lb = np.array([0.0 if lo is None else lo for lo, _ in bounds], dtype=np.float64)
    ub = np.array([np.inf if hi is None else hi for _, hi in bounds], dtype=np.float64)
    return Bounds(lb, ub)


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


def has_incumbent(res: object) -> bool:
    x = getattr(res, "x", None)
    return x is not None and bool(np.all(np.isfinite(x)))


def solve_world(
    c: np.ndarray,
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    bounds: list[tuple[float | None, float | None]],
    m: int,
) -> tuple[object, float]:
    lower = np.full(len(b_ub), -np.inf, dtype=np.float64)
    integrality = np.r_[np.ones(m, dtype=np.int8), np.zeros(len(c) - m, dtype=np.int8)]
    start = time.time()
    res = milp(
        c,
        integrality=integrality,
        bounds=as_bounds(bounds),
        constraints=LinearConstraint(a_ub, lower, b_ub),
        options={"time_limit": TIME_LIMIT, "mip_rel_gap": 1e-8},
    )
    return res, time.time() - start


def label_hash(labels: np.ndarray) -> str:
    bits = np.asarray(np.rint(labels), dtype=np.uint8)
    return hashlib.sha1(bits.tobytes()).hexdigest()[:12]


def main() -> None:
    sample = load_sub(A2C8)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    known, pos_loss, neg_loss = known_predictions(sample)
    y_public = known["public_lb"].to_numpy(dtype=np.float64)
    k, m = pos_loss.shape
    const = neg_loss.mean(axis=1)
    b = (pos_loss - neg_loss) / float(m)
    base_prob = load_prob(A2C8, sample)

    model_view = type("BinaryModelView", (), {"y": y_public, "const": const, "b": b, "k": k, "m": m})()
    a_ub, b_ub, bounds = build_constraints(model_view, train, sample, GLOBAL_BAND, SUBJECT_TARGET_BAND)
    slack_obj = np.r_[np.zeros(m), np.ones(k)]

    candidate_coeffs: dict[str, tuple[str, float, np.ndarray]] = {}
    for role, file_name in CANDIDATES:
        if role not in POOL_ROLES or locate(file_name) is None:
            continue
        cand_prob = load_prob(file_name, sample)
        delta_const, delta_coeff = candidate_delta_coeff(cand_prob, base_prob)
        candidate_coeffs[role] = (file_name, delta_const, delta_coeff)

    objectives: list[tuple[str, str, np.ndarray]] = [("fit", "slack", slack_obj.copy())]
    for role, (_, _, coeff) in candidate_coeffs.items():
        objectives.append((f"{role}_min", role, slack_obj + OBJECTIVE_ALPHA * np.r_[coeff, np.zeros(k)]))
        objectives.append((f"{role}_max", role, slack_obj - OBJECTIVE_ALPHA * np.r_[coeff, np.zeros(k)]))

    rng = np.random.default_rng(RANDOM_SEED)
    target_ids = np.tile(np.arange(len(TARGETS)), len(sample))
    row_subject = sample["subject_id"].to_numpy()
    cell_subject = np.repeat(row_subject, len(TARGETS))
    for i in range(4):
        coeff = rng.normal(0.0, 0.3, size=m)
        for ti in range(len(TARGETS)):
            coeff[target_ids == ti] += rng.normal(0.0, 1.0)
        for sid in sorted(sample["subject_id"].unique()):
            coeff[cell_subject == sid] += rng.normal(0.0, 0.5)
        coeff = coeff / (np.std(coeff) + 1e-12) / float(m)
        objectives.append((f"random_world_{i}", "random", slack_obj + RANDOM_ALPHA * np.r_[coeff, np.zeros(k)]))

    world_rows = []
    target_rows = []
    delta_rows = []
    label_rows = []
    seen_hashes: set[str] = set()

    for objective_name, source_role, c in objectives:
        res, elapsed = solve_world(c, a_ub, b_ub, bounds, m)
        row = {
            "objective": objective_name,
            "source_role": source_role,
            "solver_success": bool(getattr(res, "success", False)),
            "status": safe_int(getattr(res, "status", -999)),
            "message": str(getattr(res, "message", "")),
            "mip_gap": safe_float(getattr(res, "mip_gap", np.nan)),
            "mip_dual_bound": safe_float(getattr(res, "mip_dual_bound", np.nan)),
            "mip_node_count": safe_int(getattr(res, "mip_node_count", -1)),
            "elapsed_sec": elapsed,
            "time_limit": TIME_LIMIT,
            "has_incumbent": has_incumbent(res),
        }
        if not has_incumbent(res):
            world_rows.append(row)
            continue
        labels = np.rint(res.x[:m]).astype(np.uint8)
        h = label_hash(labels)
        resid = residuals_from_x(const, b, y_public, res.x, m)
        row.update(
            {
                "world_id": h,
                "duplicate_world": h in seen_hashes,
                "fit_objective_value": safe_float(getattr(res, "fun", np.nan)),
                "sum_abs_residual": float(np.sum(np.abs(resid))),
                "max_abs_residual": float(np.max(np.abs(resid))),
                "mean_abs_residual": float(np.mean(np.abs(resid))),
                "max_residual_over_frontier_raw05_gap": float(np.max(np.abs(resid)) / FRONTIER_RAW05_GAP),
                "positive_cell_count": int(labels.sum()),
                "frontier_scale_fit": bool(np.max(np.abs(resid)) <= FRONTIER_RAW05_GAP),
            }
        )
        seen_hashes.add(h)
        label_rows.append(labels)

        for ti, target in enumerate(TARGETS):
            mask = target_ids == ti
            target_rows.append(
                {
                    "world_id": h,
                    "objective": objective_name,
                    "target": target,
                    "binary_prior": float(labels[mask].mean()),
                    "train_prior": float(train[target].mean()),
                }
            )
        for role, (file_name, delta_const, delta_coeff) in candidate_coeffs.items():
            delta = float(delta_const + delta_coeff @ labels)
            delta_rows.append(
                {
                    "world_id": h,
                    "objective": objective_name,
                    "source_role": source_role,
                    "role": role,
                    "file": file_name,
                    "candidate_delta_vs_a2c8": delta,
                    "candidate_better_than_a2c8": bool(delta < 0.0),
                    "frontier_scale_fit": bool(row["frontier_scale_fit"]),
                    "max_abs_residual": float(row["max_abs_residual"]),
                    "sum_abs_residual": float(row["sum_abs_residual"]),
                }
            )
        world_rows.append(row)

    world_df = pd.DataFrame(world_rows)
    target_df = pd.DataFrame(target_rows)
    delta_df = pd.DataFrame(delta_rows)
    world_df.to_csv(WORLD_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    delta_df.to_csv(DELTA_OUT, index=False)
    if label_rows:
        np.savez_compressed(NPZ_OUT, labels=np.vstack(label_rows), targets=np.asarray(TARGETS, dtype=object))

    if not delta_df.empty:
        summary_df = (
            delta_df.groupby("role", as_index=False)
            .agg(
                worlds=("world_id", "nunique"),
                better_rate=("candidate_better_than_a2c8", "mean"),
                min_delta=("candidate_delta_vs_a2c8", "min"),
                median_delta=("candidate_delta_vs_a2c8", "median"),
                max_delta=("candidate_delta_vs_a2c8", "max"),
                frontier_worlds=("frontier_scale_fit", "sum"),
            )
            .sort_values(["better_rate", "median_delta"], ascending=[False, True])
            .reset_index(drop=True)
        )
        frontier_df = delta_df[delta_df["frontier_scale_fit"]].copy()
        if not frontier_df.empty:
            frontier_summary = (
                frontier_df.groupby("role", as_index=False)
                .agg(
                    frontier_worlds=("world_id", "nunique"),
                    frontier_better_rate=("candidate_better_than_a2c8", "mean"),
                    frontier_min_delta=("candidate_delta_vs_a2c8", "min"),
                    frontier_median_delta=("candidate_delta_vs_a2c8", "median"),
                    frontier_max_delta=("candidate_delta_vs_a2c8", "max"),
                )
                .sort_values(["frontier_better_rate", "frontier_median_delta"], ascending=[False, True])
                .reset_index(drop=True)
            )
        else:
            frontier_summary = pd.DataFrame()
    else:
        summary_df = pd.DataFrame()
        frontier_summary = pd.DataFrame()
    summary_df.to_csv(SUMMARY_OUT, index=False)

    accepted_worlds = world_df[world_df.get("frontier_scale_fit", False) == True] if "frontier_scale_fit" in world_df else pd.DataFrame()
    lines = [
        "# Public LB Binary World Pool",
        "",
        "Question: if binary hidden-label worlds can fit known public anchors, do multiple binary incumbents agree on candidate signs?",
        "",
        "## World Fit Summary",
        "",
        markdown_table(
            world_df[
                [
                    "objective",
                    "source_role",
                    "world_id",
                    "duplicate_world",
                    "max_abs_residual",
                    "max_residual_over_frontier_raw05_gap",
                    "sum_abs_residual",
                    "positive_cell_count",
                    "frontier_scale_fit",
                    "elapsed_sec",
                    "message",
                ]
            ]
            if not world_df.empty and "world_id" in world_df
            else world_df
        ),
        "",
        "## Candidate Delta Summary",
        "",
        markdown_table(summary_df),
        "",
        "## Frontier-Scale Worlds Only",
        "",
        markdown_table(frontier_summary),
        "",
        "## Decision",
        "",
        f"- objectives attempted: `{len(objectives)}`.",
        f"- incumbent worlds: `{int(world_df['has_incumbent'].sum()) if 'has_incumbent' in world_df else 0}`.",
        f"- unique worlds: `{len(seen_hashes)}`.",
        f"- frontier-scale worlds: `{len(accepted_worlds)}`.",
    ]
    if not frontier_summary.empty:
        stable = frontier_summary[
            (frontier_summary["frontier_better_rate"] == 1.0) | (frontier_summary["frontier_better_rate"] == 0.0)
        ].copy()
        improving = frontier_summary[frontier_summary["frontier_better_rate"] == 1.0].copy()
        lines.append(f"- frontier-stable roles: `{len(stable)}`; stable-improving roles: `{len(improving)}`.")
        if improving.empty:
            lines.append("- No candidate is consistently better than a2c8 across frontier-scale binary worlds.")
        else:
            lines.append("- Some candidates are consistently better inside this binary-world pool; treat as a hypothesis-specific signal requiring selector stress.")
    else:
        lines.append("- No frontier-scale binary world pool was obtained; this cannot rank submissions.")
    lines.append("- This pool is a diagnostic sample, not proof of the exact public set; all worlds are solver incumbents under time limits.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(REPORT_OUT)
    print(
        {
            "objectives": len(objectives),
            "incumbents": int(world_df["has_incumbent"].sum()) if "has_incumbent" in world_df else 0,
            "unique_worlds": len(seen_hashes),
            "frontier_worlds": len(accepted_worlds),
        }
    )
    if not summary_df.empty:
        print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
