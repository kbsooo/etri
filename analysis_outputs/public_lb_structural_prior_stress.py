from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, TARGETS, locate, load_sub  # noqa: E402
from public_lb_inverse_feasibility import (  # noqa: E402
    AllTestSoftLabelLP,
    CANDIDATES,
    cell_target_index,
    known_predictions,
    load_prob,
    range_pair,
    solve_lp,
)


RANGE_OUT = OUT / "public_lb_structural_prior_stress_ranges.csv"
SCENARIO_OUT = OUT / "public_lb_structural_prior_stress_scenarios.csv"
REPORT_OUT = OUT / "public_lb_structural_prior_stress_report.md"


SCENARIOS = [
    {
        "scenario": "alltest_no_prior",
        "global_band": None,
        "subject_target_band": None,
        "interpretation": "E26 control: all test cells, no structural prior.",
    },
    {
        "scenario": "global_t005",
        "global_band": 0.05,
        "subject_target_band": None,
        "interpretation": "All-test public world with train target prevalence +/-0.05.",
    },
    {
        "scenario": "global_t005_subject_t020",
        "global_band": 0.05,
        "subject_target_band": 0.20,
        "interpretation": "Weak subject identity prior layered on global prevalence.",
    },
    {
        "scenario": "global_t005_subject_t015",
        "global_band": 0.05,
        "subject_target_band": 0.15,
        "interpretation": "Moderate subject identity prior; still allows temporal drift.",
    },
    {
        "scenario": "global_t010_subject_t020",
        "global_band": 0.10,
        "subject_target_band": 0.20,
        "interpretation": "Looser global prior with weak subject identity prior.",
    },
    {
        "scenario": "global_t010_subject_t015",
        "global_band": 0.10,
        "subject_target_band": 0.15,
        "interpretation": "Balanced global/subject prior stress.",
    },
    {
        "scenario": "global_t010_subject_t010",
        "global_band": 0.10,
        "subject_target_band": 0.10,
        "interpretation": "Tight subject identity prior; strong assumption stress.",
    },
]


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def add_global_prior_rows(
    rows: list[np.ndarray],
    rhs: list[float],
    model: AllTestSoftLabelLP,
    train_prior: dict[str, float],
    band: float | None,
) -> None:
    if band is None:
        return
    n_rows = model.m // len(TARGETS)
    target_ids = cell_target_index(n_rows)
    for ti, target in enumerate(TARGETS):
        coeff = (target_ids == ti).astype(np.float64) / float(n_rows)
        lo = max(0.0, float(train_prior[target]) - float(band))
        hi = min(1.0, float(train_prior[target]) + float(band))
        rows.append(np.r_[coeff, np.zeros(model.k)])
        rhs.append(hi)
        rows.append(np.r_[-coeff, np.zeros(model.k)])
        rhs.append(-lo)


def add_subject_target_prior_rows(
    rows: list[np.ndarray],
    rhs: list[float],
    model: AllTestSoftLabelLP,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    band: float | None,
) -> None:
    if band is None:
        return
    n_rows = len(sample)
    subject_train_prior = train.groupby("subject_id")[TARGETS].mean()
    row_subject = sample["subject_id"].to_numpy()
    target_ids = cell_target_index(n_rows)
    cell_subject = np.repeat(row_subject, len(TARGETS))
    for subject_id in sorted(sample["subject_id"].unique()):
        if subject_id not in subject_train_prior.index:
            continue
        subject_cell_count = int((row_subject == subject_id).sum())
        if subject_cell_count == 0:
            continue
        for ti, target in enumerate(TARGETS):
            mask = ((cell_subject == subject_id) & (target_ids == ti)).astype(np.float64)
            coeff = mask / float(subject_cell_count)
            center = float(subject_train_prior.loc[subject_id, target])
            lo = max(0.0, center - float(band))
            hi = min(1.0, center + float(band))
            rows.append(np.r_[coeff, np.zeros(model.k)])
            rhs.append(hi)
            rows.append(np.r_[-coeff, np.zeros(model.k)])
            rhs.append(-lo)


def build_constraints(
    model: AllTestSoftLabelLP,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    global_band: float | None,
    subject_target_band: float | None,
) -> tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]:
    lhs = model.y - model.const
    base_a = np.vstack(
        [
            np.c_[model.b, -np.eye(model.k)],
            np.c_[-model.b, -np.eye(model.k)],
        ]
    )
    base_b = np.r_[lhs, -lhs]
    rows = [base_a]
    rhs = list(base_b)
    train_prior = train[TARGETS].mean().to_dict()
    extra_rows: list[np.ndarray] = []
    extra_rhs: list[float] = []
    add_global_prior_rows(extra_rows, extra_rhs, model, train_prior, global_band)
    add_subject_target_prior_rows(extra_rows, extra_rhs, model, train, sample, subject_target_band)
    if extra_rows:
        rows.append(np.vstack(extra_rows))
        rhs.extend(extra_rhs)
    bounds = [(0.0, 1.0)] * model.m + [(0.0, None)] * model.k
    return np.vstack(rows), np.asarray(rhs, dtype=np.float64), bounds


def fit_scenario(
    model: AllTestSoftLabelLP,
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    bounds: list[tuple[float | None, float | None]],
) -> tuple[bool, float, float, np.ndarray]:
    c = np.r_[np.zeros(model.m), np.ones(model.k)]
    ok, value, x = solve_lp(c, a_ub, b_ub, bounds)
    if not ok:
        return False, float("nan"), float("nan"), np.full(model.m + model.k, np.nan)
    pred = model.const + model.b @ x[: model.m]
    return True, float(value), float(np.max(np.abs(pred - model.y))), x


def candidate_range_under_scenario(
    model: AllTestSoftLabelLP,
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    bounds: list[tuple[float | None, float | None]],
    fit_sum_slack: float,
    coeff_q: np.ndarray,
    const: float,
    slack_tol: float = 1e-8,
) -> tuple[float, float]:
    sum_slack = np.r_[np.zeros(model.m), np.ones(model.k)][None, :]
    a_ub2 = np.vstack([a_ub, sum_slack])
    b_ub2 = np.r_[b_ub, fit_sum_slack + slack_tol]
    c = np.r_[coeff_q, np.zeros(model.k)]
    ok_min, lo, _ = solve_lp(c, a_ub2, b_ub2, bounds)
    ok_max, hi_raw, _ = solve_lp(-c, a_ub2, b_ub2, bounds)
    if not ok_min or not ok_max:
        return float("nan"), float("nan")
    return float(const + lo), float(const - hi_raw)


def scenario_prior_ranges(
    model: AllTestSoftLabelLP,
    fit_sum_slack: float,
    a_ub: np.ndarray,
    b_ub: np.ndarray,
    bounds: list[tuple[float | None, float | None]],
    sample: pd.DataFrame,
) -> dict[str, float]:
    n_rows = len(sample)
    target_ids = cell_target_index(n_rows)
    rows: dict[str, float] = {}
    sum_slack = np.r_[np.zeros(model.m), np.ones(model.k)][None, :]
    a_ub2 = np.vstack([a_ub, sum_slack])
    b_ub2 = np.r_[b_ub, fit_sum_slack + 1e-8]
    for ti, target in enumerate(TARGETS):
        coeff = (target_ids == ti).astype(np.float64) / float(n_rows)
        lo_ok, lo, _ = solve_lp(np.r_[coeff, np.zeros(model.k)], a_ub2, b_ub2, bounds)
        hi_ok, hi_raw, _ = solve_lp(np.r_[-coeff, np.zeros(model.k)], a_ub2, b_ub2, bounds)
        rows[f"{target}_prior_min"] = float(lo) if lo_ok else float("nan")
        rows[f"{target}_prior_max"] = float(-hi_raw) if hi_ok else float("nan")
    return rows


def main() -> None:
    sample = load_sub(A2C8)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    known, pos_loss, neg_loss = known_predictions(sample)
    base_prob = load_prob(A2C8, sample)
    model = AllTestSoftLabelLP(known, pos_loss, neg_loss)
    model.fit()

    scenario_rows = []
    range_rows = []
    for spec in SCENARIOS:
        a_ub, b_ub, bounds = build_constraints(
            model,
            train,
            sample,
            spec["global_band"],
            spec["subject_target_band"],
        )
        ok, fit_sum, fit_max_abs, fit_x = fit_scenario(model, a_ub, b_ub, bounds)
        scenario_row = {
            "scenario": spec["scenario"],
            "global_band": spec["global_band"],
            "subject_target_band": spec["subject_target_band"],
            "fit_ok": ok,
            "fit_sum_slack": fit_sum,
            "fit_max_abs_residual": fit_max_abs,
            "interpretation": spec["interpretation"],
        }
        if ok:
            scenario_row.update(scenario_prior_ranges(model, fit_sum, a_ub, b_ub, bounds, sample))
        scenario_rows.append(scenario_row)
        if not ok:
            continue

        for role, file_name in CANDIDATES:
            if locate(file_name) is None:
                continue
            cand_prob = load_prob(file_name, sample)
            const, coeff = model.candidate_delta_coeff(cand_prob, base_prob)
            lo, hi = candidate_range_under_scenario(model, a_ub, b_ub, bounds, fit_sum, coeff, const)
            range_rows.append(
                {
                    "scenario": spec["scenario"],
                    "role": role,
                    "file": file_name,
                    "delta_min": lo,
                    "delta_max": hi,
                    "range_width": hi - lo,
                    "crosses_zero": bool(lo <= 0.0 <= hi) if np.isfinite(lo) and np.isfinite(hi) else False,
                    "one_sided_negative": bool(hi < 0.0) if np.isfinite(hi) else False,
                    "one_sided_positive": bool(lo > 0.0) if np.isfinite(lo) else False,
                    "fit_sum_slack": fit_sum,
                    "fit_max_abs_residual": fit_max_abs,
                }
            )

    scenario_df = pd.DataFrame(scenario_rows)
    range_df = pd.DataFrame(range_rows)
    scenario_df.to_csv(SCENARIO_OUT, index=False)
    range_df.to_csv(RANGE_OUT, index=False)

    stability = (
        range_df.groupby(["role", "file"], as_index=False)
        .agg(
            scenarios=("scenario", "nunique"),
            cross_zero_count=("crosses_zero", "sum"),
            one_sided_negative_count=("one_sided_negative", "sum"),
            one_sided_positive_count=("one_sided_positive", "sum"),
            best_delta_min=("delta_min", "min"),
            worst_delta_max=("delta_max", "max"),
            median_width=("range_width", "median"),
        )
        .sort_values(["cross_zero_count", "worst_delta_max", "best_delta_min"])
        .reset_index(drop=True)
        if not range_df.empty
        else pd.DataFrame()
    )

    narrow = range_df[
        range_df["scenario"].isin(
            [
                "global_t005_subject_t020",
                "global_t005_subject_t015",
                "global_t010_subject_t015",
                "global_t010_subject_t010",
            ]
        )
    ].copy()
    scenario_summary = (
        range_df.groupby("scenario", as_index=False)
        .agg(
            candidates=("role", "count"),
            cross_zero=("crosses_zero", "sum"),
            one_sided_negative=("one_sided_negative", "sum"),
            one_sided_positive=("one_sided_positive", "sum"),
            median_width=("range_width", "median"),
        )
        .merge(scenario_df[["scenario", "fit_sum_slack", "fit_max_abs_residual"]], on="scenario", how="left")
        if not range_df.empty
        else pd.DataFrame()
    )

    report_lines = [
        "# Public LB Structural Prior Stress",
        "",
        "Question: if E26 is underidentified, do weak structural priors from train target prevalence and subject-target priors collapse candidate signs enough to rank submissions?",
        "",
        "## Scenario Feasibility",
        "",
        markdown_table(
            scenario_df[
                [
                    "scenario",
                    "global_band",
                    "subject_target_band",
                    "fit_ok",
                    "fit_sum_slack",
                    "fit_max_abs_residual",
                    "interpretation",
                ]
            ]
        ),
        "",
        "## Candidate Sign Stability",
        "",
        markdown_table(stability),
        "",
        "## Scenario Summary",
        "",
        markdown_table(scenario_summary),
        "",
        "## Structured Scenarios Detail",
        "",
        markdown_table(
            narrow[
                [
                    "scenario",
                    "role",
                    "delta_min",
                    "delta_max",
                    "range_width",
                    "crosses_zero",
                    "one_sided_negative",
                    "one_sided_positive",
                ]
            ].sort_values(["scenario", "delta_min"])
            if not narrow.empty
            else pd.DataFrame()
        ),
        "",
        "## Decision",
        "",
    ]
    if not range_df.empty:
        unobserved = range_df[range_df["role"] != "raw05_known"]
        strict_structured = unobserved[
            unobserved["scenario"].isin(
                [
                    "global_t005_subject_t020",
                    "global_t005_subject_t015",
                    "global_t010_subject_t015",
                    "global_t010_subject_t010",
                ]
            )
        ]
        cross_count = int(strict_structured["crosses_zero"].sum())
        neg_count = int(strict_structured["one_sided_negative"].sum())
        pos_count = int(strict_structured["one_sided_positive"].sum())
        report_lines.extend(
            [
                f"- Structured unobserved candidate-scenario cells crossing zero: `{cross_count}`.",
                f"- Structured one-sided improvement cells: `{neg_count}`.",
                f"- Structured one-sided degradation cells: `{pos_count}`.",
            ]
        )
        if neg_count == 0:
            report_lines.append(
                "- No current unobserved candidate becomes a one-sided improvement even after adding weak/moderate subject-target priors."
            )
        else:
            report_lines.append("- At least one candidate becomes one-sided negative under a declared structural prior; inspect it as a hypothesis-specific sensor only.")
        if float(scenario_df["fit_sum_slack"].max()) > 1e-6:
            report_lines.append("- Some structural priors cannot fit the known LB anchors exactly; treat their signs as stress diagnostics, not evidence of the real public world.")
        else:
            report_lines.append("- All tested structural priors fit known LB anchors exactly, so remaining sign ambiguity is not caused by infeasible prior assumptions.")
    REPORT_OUT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(REPORT_OUT)
    print(
        {
            "scenarios": len(scenario_df),
            "range_rows": len(range_df),
            "max_fit_sum_slack": float(scenario_df["fit_sum_slack"].max()) if not scenario_df.empty else None,
            "unobserved_cross_zero_cells": int(range_df[(range_df["role"] != "raw05_known")]["crosses_zero"].sum())
            if not range_df.empty
            else 0,
            "unobserved_one_sided_negative_cells": int(
                range_df[(range_df["role"] != "raw05_known")]["one_sided_negative"].sum()
            )
            if not range_df.empty
            else 0,
        }
    )
    if not stability.empty:
        print(stability.to_string(index=False))


if __name__ == "__main__":
    main()
