from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import linprog


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    TARGETS,
    KEYS,
    known_public_table,
    load_sub,
    locate,
)


FIT_OUT = OUT / "public_lb_inverse_feasibility_known_fit.csv"
TARGET_RANGE_OUT = OUT / "public_lb_inverse_feasibility_target_ranges.csv"
SUBJECT_RANGE_OUT = OUT / "public_lb_inverse_feasibility_subject_ranges.csv"
CANDIDATE_RANGE_OUT = OUT / "public_lb_inverse_feasibility_candidate_ranges.csv"
PRIOR_BAND_RANGE_OUT = OUT / "public_lb_inverse_feasibility_candidate_ranges_priorband.csv"
REPORT_OUT = OUT / "public_lb_inverse_feasibility_report.md"


CANDIDATES = [
    ("pair_sensor_1bb", "submission_label_flow_focused_1bbfb735.csv"),
    ("pair_sensor_1bb_s0p65", "submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv"),
    ("pair_sensor_6b", "submission_label_flow_focused_6b9335b1.csv"),
    ("mixmin_0c916", "submission_mixmin_0c916bb4.csv"),
    ("direns_c4af", "submission_direns_c4af1fd8.csv"),
    ("targetabl_q3stage", "submission_targetabl_b19056bb.csv"),
    ("targetabl_q3s234", "submission_targetabl_1049b8e7.csv"),
    ("inverse7blend_1040", "submission_inverse7blend_1040423d.csv"),
    ("raw05_known", "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def losses(prob: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip_prob(prob)
    return -np.log(p).reshape(-1), -np.log(1.0 - p).reshape(-1)


def load_prob(file_name: str | Path, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)


def known_predictions(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    known = known_public_table().copy()
    known = known[known["file"].map(lambda x: locate(str(x)) is not None)].reset_index(drop=True)
    pos_rows: list[np.ndarray] = []
    neg_rows: list[np.ndarray] = []
    for file_name in known["file"]:
        pos, neg = losses(load_prob(str(file_name), sample))
        pos_rows.append(pos)
        neg_rows.append(neg)
    return known, np.vstack(pos_rows), np.vstack(neg_rows)


def solve_lp(
    c: np.ndarray,
    a_ub: np.ndarray | None,
    b_ub: np.ndarray | None,
    bounds: list[tuple[float | None, float | None]],
    a_eq: np.ndarray | None = None,
    b_eq: np.ndarray | None = None,
) -> tuple[bool, float, np.ndarray]:
    res = linprog(
        c,
        A_ub=a_ub,
        b_ub=b_ub,
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    if not res.success:
        return False, float("nan"), np.full(len(c), np.nan)
    return True, float(res.fun), np.asarray(res.x, dtype=np.float64)


class AllTestSoftLabelLP:
    def __init__(self, known: pd.DataFrame, pos_loss: np.ndarray, neg_loss: np.ndarray):
        self.known = known
        self.pos_loss = pos_loss
        self.neg_loss = neg_loss
        self.y = known["public_lb"].to_numpy(dtype=np.float64)
        self.k, self.m = pos_loss.shape
        self.const = neg_loss.mean(axis=1)
        self.b = (pos_loss - neg_loss) / float(self.m)
        self.fit_sum_slack: float | None = None
        self.fit_x: np.ndarray | None = None
        self.fit_residual: np.ndarray | None = None

    def fit(self) -> None:
        c = np.r_[np.zeros(self.m), np.ones(self.k)]
        lhs = self.y - self.const
        a_ub = np.vstack(
            [
                np.c_[self.b, -np.eye(self.k)],
                np.c_[-self.b, -np.eye(self.k)],
            ]
        )
        b_ub = np.r_[lhs, -lhs]
        bounds = [(0.0, 1.0)] * self.m + [(0.0, None)] * self.k
        ok, value, x = solve_lp(c, a_ub, b_ub, bounds)
        if not ok:
            raise RuntimeError("all-test soft-label LP failed")
        q = x[: self.m]
        pred = self.const + self.b @ q
        self.fit_sum_slack = value
        self.fit_x = x
        self.fit_residual = pred - self.y

    def constraints(self, slack_tol: float) -> tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]:
        if self.fit_sum_slack is None:
            self.fit()
        lhs = self.y - self.const
        base_a = np.vstack(
            [
                np.c_[self.b, -np.eye(self.k)],
                np.c_[-self.b, -np.eye(self.k)],
            ]
        )
        base_b = np.r_[lhs, -lhs]
        sum_slack = np.r_[np.zeros(self.m), np.ones(self.k)][None, :]
        a_ub = np.vstack([base_a, sum_slack])
        b_ub = np.r_[base_b, float(self.fit_sum_slack or 0.0) + float(slack_tol)]
        bounds = [(0.0, 1.0)] * self.m + [(0.0, None)] * self.k
        return a_ub, b_ub, bounds

    def optimize_linear(self, coeff_q: np.ndarray, slack_tol: float, maximize: bool = False) -> tuple[bool, float]:
        a_ub, b_ub, bounds = self.constraints(slack_tol)
        c = np.r_[coeff_q, np.zeros(self.k)]
        if maximize:
            c = -c
        ok, value, _ = solve_lp(c, a_ub, b_ub, bounds)
        if not ok:
            return False, float("nan")
        return True, float(-value if maximize else value)

    def candidate_delta_coeff(self, candidate_prob: np.ndarray, base_prob: np.ndarray) -> tuple[float, np.ndarray]:
        cand_pos, cand_neg = losses(candidate_prob)
        base_pos, base_neg = losses(base_prob)
        const = float(np.mean(cand_neg - base_neg))
        coeff = (cand_pos - cand_neg - base_pos + base_neg) / float(self.m)
        return const, coeff


class CellMixtureLP:
    def __init__(self, known: pd.DataFrame, pos_loss: np.ndarray, neg_loss: np.ndarray):
        self.known = known
        self.pos_loss = pos_loss
        self.neg_loss = neg_loss
        self.y = known["public_lb"].to_numpy(dtype=np.float64)
        self.k, self.m = pos_loss.shape
        self.fit_sum_slack: float | None = None
        self.fit_x: np.ndarray | None = None
        self.fit_residual: np.ndarray | None = None

    def fit(self) -> None:
        n = 2 * self.m + self.k
        c = np.r_[np.zeros(2 * self.m), np.ones(self.k)]
        loss_block = np.c_[self.pos_loss, self.neg_loss]
        a_ub = np.vstack(
            [
                np.c_[loss_block, -np.eye(self.k)],
                np.c_[-loss_block, -np.eye(self.k)],
            ]
        )
        b_ub = np.r_[self.y, -self.y]
        a_eq = np.r_[np.ones(2 * self.m), np.zeros(self.k)][None, :]
        b_eq = np.array([1.0])
        bounds = [(0.0, None)] * n
        ok, value, x = solve_lp(c, a_ub, b_ub, bounds, a_eq, b_eq)
        if not ok:
            raise RuntimeError("cell-mixture LP failed")
        weights = x[: 2 * self.m]
        pred = loss_block @ weights
        self.fit_sum_slack = value
        self.fit_x = x
        self.fit_residual = pred - self.y

    def constraints(
        self,
        slack_tol: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]:
        if self.fit_sum_slack is None:
            self.fit()
        loss_block = np.c_[self.pos_loss, self.neg_loss]
        base_a = np.vstack(
            [
                np.c_[loss_block, -np.eye(self.k)],
                np.c_[-loss_block, -np.eye(self.k)],
            ]
        )
        base_b = np.r_[self.y, -self.y]
        sum_slack = np.r_[np.zeros(2 * self.m), np.ones(self.k)][None, :]
        a_ub = np.vstack([base_a, sum_slack])
        b_ub = np.r_[base_b, float(self.fit_sum_slack or 0.0) + float(slack_tol)]
        a_eq = np.r_[np.ones(2 * self.m), np.zeros(self.k)][None, :]
        b_eq = np.array([1.0])
        bounds = [(0.0, None)] * (2 * self.m + self.k)
        return a_ub, b_ub, a_eq, b_eq, bounds

    def optimize_linear(self, coeff_weights: np.ndarray, slack_tol: float, maximize: bool = False) -> tuple[bool, float]:
        a_ub, b_ub, a_eq, b_eq, bounds = self.constraints(slack_tol)
        c = np.r_[coeff_weights, np.zeros(self.k)]
        if maximize:
            c = -c
        ok, value, _ = solve_lp(c, a_ub, b_ub, bounds, a_eq, b_eq)
        if not ok:
            return False, float("nan")
        return True, float(-value if maximize else value)

    def candidate_delta_coeff(self, candidate_prob: np.ndarray, base_prob: np.ndarray) -> np.ndarray:
        cand_pos, cand_neg = losses(candidate_prob)
        base_pos, base_neg = losses(base_prob)
        return np.r_[cand_pos - base_pos, cand_neg - base_neg]


def cell_target_index(n_rows: int) -> np.ndarray:
    return np.tile(np.arange(len(TARGETS)), n_rows)


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


def range_pair(
    model: AllTestSoftLabelLP | CellMixtureLP,
    coeff: np.ndarray,
    slack_tol: float,
    const: float = 0.0,
) -> tuple[float, float]:
    ok_min, lo = model.optimize_linear(coeff, slack_tol, maximize=False)
    ok_max, hi = model.optimize_linear(coeff, slack_tol, maximize=True)
    return (float(const + lo) if ok_min else float("nan"), float(const + hi) if ok_max else float("nan"))


def alltest_prior_band_constraints(
    model: AllTestSoftLabelLP,
    train_prior: dict[str, float],
    band: float,
) -> tuple[np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]:
    lhs = model.y - model.const
    base_a = np.vstack(
        [
            np.c_[model.b, -np.eye(model.k)],
            np.c_[-model.b, -np.eye(model.k)],
        ]
    )
    base_b = np.r_[lhs, -lhs]
    n_rows = model.m // len(TARGETS)
    target_ids = cell_target_index(n_rows)
    prior_rows: list[np.ndarray] = []
    prior_rhs: list[float] = []
    for ti, target in enumerate(TARGETS):
        coeff = (target_ids == ti).astype(np.float64) / float(n_rows)
        lo = max(0.0, float(train_prior[target]) - float(band))
        hi = min(1.0, float(train_prior[target]) + float(band))
        prior_rows.append(np.r_[coeff, np.zeros(model.k)])
        prior_rhs.append(hi)
        prior_rows.append(np.r_[-coeff, np.zeros(model.k)])
        prior_rhs.append(-lo)
    a_ub = np.vstack([base_a, np.vstack(prior_rows)])
    b_ub = np.r_[base_b, np.asarray(prior_rhs, dtype=np.float64)]
    bounds = [(0.0, 1.0)] * model.m + [(0.0, None)] * model.k
    return a_ub, b_ub, bounds


def fit_alltest_prior_band(
    model: AllTestSoftLabelLP,
    train_prior: dict[str, float],
    band: float,
) -> tuple[float, float, np.ndarray, np.ndarray, list[tuple[float | None, float | None]]]:
    a_ub, b_ub, bounds = alltest_prior_band_constraints(model, train_prior, band)
    c = np.r_[np.zeros(model.m), np.ones(model.k)]
    ok, value, x = solve_lp(c, a_ub, b_ub, bounds)
    if not ok:
        return float("nan"), float("nan"), a_ub, b_ub, bounds
    pred = model.const + model.b @ x[: model.m]
    return float(value), float(np.max(np.abs(pred - model.y))), a_ub, b_ub, bounds


def range_alltest_prior_band(
    model: AllTestSoftLabelLP,
    coeff_q: np.ndarray,
    train_prior: dict[str, float],
    band: float,
    slack_tol: float,
    const: float = 0.0,
) -> tuple[float, float, float, float]:
    fit_sum, fit_max_abs, a_ub, b_ub, bounds = fit_alltest_prior_band(model, train_prior, band)
    if not np.isfinite(fit_sum):
        return float("nan"), float("nan"), fit_sum, fit_max_abs
    sum_slack = np.r_[np.zeros(model.m), np.ones(model.k)][None, :]
    a_ub2 = np.vstack([a_ub, sum_slack])
    b_ub2 = np.r_[b_ub, fit_sum + slack_tol]
    c = np.r_[coeff_q, np.zeros(model.k)]
    ok_min, lo, _ = solve_lp(c, a_ub2, b_ub2, bounds)
    ok_max, hi_raw, _ = solve_lp(-c, a_ub2, b_ub2, bounds)
    lo_out = const + lo if ok_min else float("nan")
    hi_out = const - hi_raw if ok_max else float("nan")
    return float(lo_out), float(hi_out), fit_sum, fit_max_abs


def main() -> None:
    sample = load_sub(A2C8)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    train_prior = train[TARGETS].mean().to_dict()
    known, pos_loss, neg_loss = known_predictions(sample)
    n_rows = len(sample)
    m = n_rows * len(TARGETS)
    base_prob = load_prob(A2C8, sample)

    alltest = AllTestSoftLabelLP(known, pos_loss, neg_loss)
    alltest.fit()
    cellmix = CellMixtureLP(known, pos_loss, neg_loss)
    cellmix.fit()
    alltest_slack_tol = 1e-8
    cellmix_slack_tol = 1e-8

    alltest_pred = alltest.const + alltest.b @ alltest.fit_x[:m]
    cell_weights = cellmix.fit_x[: 2 * m]
    cellmix_pred = np.c_[pos_loss, neg_loss] @ cell_weights
    fit_rows = []
    for i, rec in known.iterrows():
        fit_rows.append(
            {
                "file": rec["file"],
                "public_lb": float(rec["public_lb"]),
                "alltest_fit": float(alltest_pred[i]),
                "alltest_residual": float(alltest_pred[i] - rec["public_lb"]),
                "cellmix_fit": float(cellmix_pred[i]),
                "cellmix_residual": float(cellmix_pred[i] - rec["public_lb"]),
            }
        )
    fit_df = pd.DataFrame(fit_rows)
    fit_df.to_csv(FIT_OUT, index=False)

    target_ids = cell_target_index(n_rows)
    target_rows = []
    for ti, target in enumerate(TARGETS):
        q_coeff = (target_ids == ti).astype(np.float64) / float(n_rows)
        lo, hi = range_pair(alltest, q_coeff, alltest_slack_tol)
        pos_coeff = np.r_[(target_ids == ti).astype(np.float64), np.zeros(m)]
        mass_coeff = np.r_[(target_ids == ti).astype(np.float64), (target_ids == ti).astype(np.float64)]
        pos_lo, pos_hi = range_pair(cellmix, pos_coeff, cellmix_slack_tol)
        mass_lo, mass_hi = range_pair(cellmix, mass_coeff, cellmix_slack_tol)
        target_rows.append(
            {
                "target": target,
                "alltest_prior_min": lo,
                "alltest_prior_max": hi,
                "alltest_prior_width": hi - lo,
                "cellmix_positive_mass_min": pos_lo,
                "cellmix_positive_mass_max": pos_hi,
                "cellmix_target_mass_min": mass_lo,
                "cellmix_target_mass_max": mass_hi,
            }
        )
    target_df = pd.DataFrame(target_rows)
    target_df.to_csv(TARGET_RANGE_OUT, index=False)

    subject_rows = []
    row_subject = sample["subject_id"].to_numpy()
    cell_subject = np.repeat(row_subject, len(TARGETS))
    for sid in sorted(sample["subject_id"].unique()):
        mask = (cell_subject == sid).astype(np.float64)
        mass_coeff = np.r_[mask, mask]
        lo, hi = range_pair(cellmix, mass_coeff, cellmix_slack_tol)
        subject_rows.append(
            {
                "subject_id": sid,
                "actual_test_row_frac": float(np.mean(row_subject == sid)),
                "cellmix_subject_mass_min": lo,
                "cellmix_subject_mass_max": hi,
                "cellmix_subject_mass_width": hi - lo,
            }
        )
    subject_df = pd.DataFrame(subject_rows)
    subject_df.to_csv(SUBJECT_RANGE_OUT, index=False)

    cand_rows = []
    for role, file_name in CANDIDATES:
        if locate(file_name) is None:
            continue
        cand_prob = load_prob(file_name, sample)
        const, coeff = alltest.candidate_delta_coeff(cand_prob, base_prob)
        all_lo, all_hi = range_pair(alltest, coeff, alltest_slack_tol, const)
        cell_coeff = cellmix.candidate_delta_coeff(cand_prob, base_prob)
        cell_lo, cell_hi = range_pair(cellmix, cell_coeff, cellmix_slack_tol)
        cand_rows.append(
            {
                "role": role,
                "file": file_name,
                "alltest_delta_min": all_lo,
                "alltest_delta_max": all_hi,
                "alltest_crosses_zero": bool(all_lo <= 0.0 <= all_hi),
                "cellmix_delta_min": cell_lo,
                "cellmix_delta_max": cell_hi,
                "cellmix_crosses_zero": bool(cell_lo <= 0.0 <= cell_hi),
                "mean_abs_prob_move_vs_a2c8": float(np.mean(np.abs(cand_prob - base_prob))),
                "mean_abs_logit_move_vs_a2c8": float(
                    np.mean(np.abs(np.log(clip_prob(cand_prob) / (1 - clip_prob(cand_prob))) - np.log(clip_prob(base_prob) / (1 - clip_prob(base_prob)))))
                ),
            }
        )
    cand_df = pd.DataFrame(cand_rows).sort_values("alltest_delta_min").reset_index(drop=True)
    cand_df.to_csv(CANDIDATE_RANGE_OUT, index=False)

    prior_band_rows = []
    for role, file_name in CANDIDATES:
        if locate(file_name) is None:
            continue
        cand_prob = load_prob(file_name, sample)
        const, coeff = alltest.candidate_delta_coeff(cand_prob, base_prob)
        for band in [0.05, 0.10, 0.20]:
            lo, hi, fit_sum, fit_max_abs = range_alltest_prior_band(
                alltest,
                coeff,
                train_prior,
                band,
                slack_tol=1e-8,
                const=const,
            )
            prior_band_rows.append(
                {
                    "role": role,
                    "file": file_name,
                    "prior_band": band,
                    "fit_sum_slack": fit_sum,
                    "fit_max_abs_residual": fit_max_abs,
                    "delta_min": lo,
                    "delta_max": hi,
                    "crosses_zero": bool(lo <= 0.0 <= hi) if np.isfinite(lo) and np.isfinite(hi) else False,
                }
            )
    prior_band_df = pd.DataFrame(prior_band_rows).sort_values(["prior_band", "delta_min"]).reset_index(drop=True)
    prior_band_df.to_csv(PRIOR_BAND_RANGE_OUT, index=False)

    report_lines = [
        "# Public LB Inverse Feasibility",
        "",
        "Question: do the known public LB observations identify target/row/public-prior structure strongly enough to rank candidate deltas, or are many hidden worlds still feasible?",
        "",
        "## Fit",
        "",
        f"- known public observations used: `{len(known)}`.",
        f"- cells: `{m}` (`{n_rows}` rows x `{len(TARGETS)}` targets).",
        f"- all-test soft-label minimum total slack: `{float(alltest.fit_sum_slack):.12g}`; max abs residual `{float(np.max(np.abs(alltest.fit_residual))):.12g}`.",
        f"- arbitrary cell-mixture minimum total slack: `{float(cellmix.fit_sum_slack):.12g}`; max abs residual `{float(np.max(np.abs(cellmix.fit_residual))):.12g}`.",
        "",
        "## Target Ranges",
        "",
        markdown_table(target_df),
        "",
        "## Candidate Delta Ranges vs A2C8",
        "",
        markdown_table(cand_df),
        "",
        "## Candidate Delta Ranges With Train-Prior Bands",
        "",
        markdown_table(prior_band_df),
        "",
        "## Subject Mass Ranges Under Cell-Mixture Model",
        "",
        markdown_table(subject_df),
        "",
        "## Decision",
        "",
    ]
    all_cross = int(cand_df["alltest_crosses_zero"].sum()) if not cand_df.empty else 0
    cell_cross = int(cand_df["cellmix_crosses_zero"].sum()) if not cand_df.empty else 0
    band_cross = (
        prior_band_df.groupby("prior_band")["crosses_zero"].sum().to_dict()
        if not prior_band_df.empty
        else {}
    )
    if all_cross:
        report_lines.extend(
            [
                f"- `{all_cross}` candidate delta intervals cross zero under the stricter all-test soft-label inverse model.",
                "- Known public LB anchors are therefore not enough to determine those candidate signs without additional structural assumptions.",
            ]
        )
    else:
        report_lines.append("- Under all-test soft labels, candidate signs are one-sided for the checked candidates.")
    report_lines.extend(
        [
            f"- `{cell_cross}` candidate delta intervals cross zero under the looser cell-mixture model.",
            f"- Train-prior band cross-zero counts: `{band_cross}`.",
            "- If public subset/row/target weights are allowed to vary freely, the LB observations are highly underidentified.",
            "- This supports using public LB as a sensor only after declaring a selector worldview, not as a standalone optimizer.",
        ]
    )
    REPORT_OUT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(REPORT_OUT)
    print(
        {
            "known": len(known),
            "alltest_sum_slack": float(alltest.fit_sum_slack),
            "alltest_max_abs_resid": float(np.max(np.abs(alltest.fit_residual))),
            "cellmix_sum_slack": float(cellmix.fit_sum_slack),
            "cellmix_max_abs_resid": float(np.max(np.abs(cellmix.fit_residual))),
            "alltest_cross_zero": all_cross,
            "cellmix_cross_zero": cell_cross,
            "prior_band_cross_zero": band_cross,
        }
    )
    print("[candidate ranges]")
    print(cand_df.to_string(index=False))


if __name__ == "__main__":
    main()
