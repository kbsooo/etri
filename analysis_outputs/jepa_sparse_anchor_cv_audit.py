from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402
from public_subset_sensitivity_audit import ce_matrix  # noqa: E402


ALL_ANCHORS = list(inv.ANCHORS)
SELECTED_SPARSE = OUT / "jepa_regularized_sparse_direct_solver_selected.csv"
SUMMARY_OUT = OUT / "jepa_sparse_anchor_cv_audit_summary.csv"
DETAIL_OUT = OUT / "jepa_sparse_anchor_cv_audit_detail.csv"
REPORT_OUT = OUT / "jepa_sparse_anchor_cv_audit_report.md"


CONTROL_FILES = {
    "control_a2c8": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "control_raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "control_directrob_29ffe34b": "submission_directrob_29ffe34b.csv",
    "control_directcons_de1d6b6d": "submission_directcons_de1d6b6d.csv",
}


def load_submission(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = inv.load_sub(file_name, sample)
    return inv.clip_prob(frame[inv.TARGETS].to_numpy(dtype=np.float64))


def score_under_fit(fit: inv.FitResult, pred: np.ndarray, stage2: np.ndarray) -> float:
    unique_rows = np.unique(fit.flat_rows)
    row_pos = {row: pos for pos, row in enumerate(unique_rows)}
    matrix_pred = np.zeros((len(unique_rows), len(inv.TARGETS)), dtype=np.float64)
    matrix_stage2 = np.zeros((len(unique_rows), len(inv.TARGETS)), dtype=np.float64)
    matrix_y = np.zeros((len(unique_rows), len(inv.TARGETS)), dtype=np.float64)
    for row_idx, target_idx, y in zip(fit.flat_rows, fit.flat_targets, fit.y, strict=False):
        pos = row_pos[int(row_idx)]
        j = int(target_idx)
        matrix_pred[pos, j] = pred[int(row_idx), j]
        matrix_stage2[pos, j] = stage2[int(row_idx), j]
        matrix_y[pos, j] = y
    pred_loss = ce_matrix(matrix_y, matrix_pred).mean()
    stage2_loss = ce_matrix(matrix_y, matrix_stage2).mean()
    return float(inv.STAGE2_PUBLIC + pred_loss - stage2_loss)


def heldout_pred_delta(fit: inv.FitResult, preds: dict[str, np.ndarray], anchor_key: str) -> float:
    base = preds["stage2"]
    pred = preds[anchor_key]
    intercept, coef = inv.diff_terms(pred, base)
    n_cells = len(fit.flat_rows)
    return float(intercept[fit.flat_rows, fit.flat_targets].mean() + (coef[fit.flat_rows, fit.flat_targets] / n_cells) @ fit.y)


def fit_quality(fit: inv.FitResult, robust_lookup: dict[tuple[int, str], float]) -> float:
    key = (int(fit.mask_index), str(fit.prior_name))
    robust_source = robust_lookup.get(key, 0.003)
    return float(
        fit.metrics["solution_score"]
        + 0.50 * fit.metrics["weighted_std_rmse"]
        + 0.015 * fit.metrics["mean_abs_shift_vs_prior"]
        + 0.35 * robust_source
    )


def build_fits(
    train_anchors: list[tuple[str, str, float, float]],
    heldout_anchors: list[tuple[str, str, float, float]],
    records: list[dict[str, object]],
    selected_masks: pd.DataFrame,
    priors: dict[str, np.ndarray],
    preds: dict[str, np.ndarray],
    robust_lookup: dict[tuple[int, str], float],
) -> pd.DataFrame:
    inv.ANCHORS = train_anchors
    rows: list[dict[str, object]] = []
    try:
        for mask_row in selected_masks.itertuples(index=False):
            rec = records[int(mask_row.mask_index)]
            row_mask = rec["mask"]
            assert isinstance(row_mask, np.ndarray)
            row_series = pd.Series(mask_row._asdict())
            for prior_name, prior in priors.items():
                fit = inv.solve_for_prior(row_series, row_mask, preds, prior_name, prior)
                heldout_errors = []
                for key, _file, public_lb, _weight in heldout_anchors:
                    obs_delta = public_lb - inv.STAGE2_PUBLIC
                    pred_delta = heldout_pred_delta(fit, preds, key)
                    heldout_errors.append(abs(pred_delta - obs_delta))
                rows.append(
                    {
                        "fit": fit,
                        "mask_index": int(fit.mask_index),
                        "mask_kind": str(fit.mask_kind),
                        "mask_name": str(fit.mask_name),
                        "rows": int(fit.rows),
                        "prior_name": str(fit.prior_name),
                        "train_solution_score": float(fit.metrics["solution_score"]),
                        "train_weighted_std_rmse": float(fit.metrics["weighted_std_rmse"]),
                        "train_mean_abs_shift_vs_prior": float(fit.metrics["mean_abs_shift_vs_prior"]),
                        "heldout_anchor_abs_error_mean": float(np.mean(heldout_errors)),
                        "heldout_anchor_abs_error_max": float(np.max(heldout_errors)),
                        "fit_quality": fit_quality(fit, robust_lookup),
                    }
                )
    finally:
        inv.ANCHORS = ALL_ANCHORS
    return pd.DataFrame(rows)


def select_fits(fits: pd.DataFrame, policy: str) -> pd.DataFrame:
    ranked = fits.sort_values(["fit_quality", "train_solution_score", "train_mean_abs_shift_vs_prior"]).copy()
    if policy == "train_best1":
        return ranked.head(1)
    if policy == "train_best5":
        return ranked.head(5)
    if policy == "structured_best3":
        return ranked[ranked["mask_kind"] != "random_rows"].head(3)
    if policy == "low_error_best5":
        return ranked.sort_values(["heldout_anchor_abs_error_mean", "fit_quality"]).head(5)
    raise ValueError(policy)


def collect_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    selected = pd.read_csv(SELECTED_SPARSE)
    keep_roles = ["sparse_first", "sparse_q3s4", "sparse_large_probe", "sparse_antiaxis"]
    selected = selected[selected["submit_role"].isin(keep_roles)].copy()
    selected = selected.sort_values(["actual_anchor_score_final", "mean_abs_move_vs_a2c8"]).drop_duplicates("file").head(24)
    rows = []
    arrays = {}
    for name, file_name in CONTROL_FILES.items():
        rows.append({"name": name, "file": file_name, "submit_role": "control"})
        arrays[name] = load_submission(file_name, sample)
    for row in selected.itertuples(index=False):
        name = str(row.name)
        file_name = str(row.file)
        rows.append(
            {
                "name": name,
                "file": file_name,
                "submit_role": str(row.submit_role),
                "actual_anchor_score_final": float(row.actual_anchor_score_final),
                "signal": str(row.signal),
                "target_mask": str(row.target_mask),
                "cell_gate": str(row.cell_gate),
                "row_gate": str(row.row_gate),
                "strength": float(row.strength),
                "cap": float(row.cap),
                "anti_lambda": float(row.anti_lambda),
                "mean_abs_move_vs_a2c8": float(row.mean_abs_move_vs_a2c8),
            }
        )
        arrays[name] = load_submission(file_name, sample)
    return pd.DataFrame(rows), arrays


def summarize(detail: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (candidate, policy, fold_kind), group in detail.groupby(["candidate_name", "policy", "fold_kind"], sort=False):
        deltas = group["delta_vs_a2c8"].to_numpy(dtype=float)
        rows.append(
            {
                "candidate_name": candidate,
                "policy": policy,
                "fold_kind": fold_kind,
                "n_folds": int(len(group)),
                "cv_delta_mean": float(np.mean(deltas)),
                "cv_delta_p10": float(np.quantile(deltas, 0.10)),
                "cv_delta_p50": float(np.quantile(deltas, 0.50)),
                "cv_delta_p90": float(np.quantile(deltas, 0.90)),
                "cv_delta_worst": float(np.max(deltas)),
                "cv_win_rate": float(np.mean(deltas < 0)),
                "selector_abs_error_mean": float(group["selector_abs_error_mean"].mean()),
                "selector_abs_error_p90": float(group["selector_abs_error_mean"].quantile(0.90)),
            }
        )
    summary = pd.DataFrame(rows)
    summary = summary.merge(candidates, left_on="candidate_name", right_on="name", how="left")
    summary["cv_stability_score"] = (
        summary["cv_delta_mean"]
        + 0.70 * np.maximum(summary["cv_delta_p90"], 0.0)
        + 0.50 * np.maximum(summary["cv_delta_worst"], 0.0)
        + 0.20 * summary["selector_abs_error_mean"]
        - 0.0005 * summary["cv_win_rate"]
    )
    return summary.sort_values(["fold_kind", "policy", "cv_stability_score"]).reset_index(drop=True)


def write_report(summary: pd.DataFrame, detail: pd.DataFrame) -> None:
    cols = [
        "candidate_name",
        "file",
        "submit_role",
        "fold_kind",
        "policy",
        "cv_delta_mean",
        "cv_delta_p90",
        "cv_delta_worst",
        "cv_win_rate",
        "selector_abs_error_mean",
        "actual_anchor_score_final",
        "mean_abs_move_vs_a2c8",
        "signal",
        "target_mask",
        "cv_stability_score",
    ]
    loo = summary[summary["fold_kind"] == "loo"].sort_values(["policy", "cv_stability_score"])
    l2o = summary[summary["fold_kind"] == "l2o"].sort_values(["policy", "cv_stability_score"])
    both = (
        summary.groupby(["candidate_name", "file", "submit_role"], as_index=False)
        .agg(
            cv_delta_mean=("cv_delta_mean", "mean"),
            cv_delta_p90=("cv_delta_p90", "mean"),
            cv_delta_worst=("cv_delta_worst", "max"),
            cv_win_rate=("cv_win_rate", "mean"),
            selector_abs_error_mean=("selector_abs_error_mean", "mean"),
            actual_anchor_score_final=("actual_anchor_score_final", "first"),
            mean_abs_move_vs_a2c8=("mean_abs_move_vs_a2c8", "first"),
            cv_stability_score=("cv_stability_score", "mean"),
        )
        .sort_values("cv_stability_score")
    )
    report = [
        "# JEPA Sparse Anchor-CV Audit",
        "",
        "This retrains direct-label hidden-label fits while leaving out public anchors, then scores sparse JEPA candidates under those fold-specific hidden-label fits.",
        "",
        "## Combined LOO/L2O Stability",
        "",
        "```",
        both.head(30).round(9).to_string(index=False),
        "```",
        "",
        "## LOO Best Rows",
        "",
        "```",
        loo[[c for c in cols if c in loo.columns]].head(40).round(9).to_string(index=False),
        "```",
        "",
        "## L2O Best Rows",
        "",
        "```",
        l2o[[c for c in cols if c in l2o.columns]].head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- Negative `cv_delta_*` means the candidate beats a2c8 under hidden-label fits trained without some public anchors.",
        "- `train_best*` policies are the honest selector view. `low_error_best5` is an oracle-like diagnostic that uses heldout error and should not drive submission alone.",
        "- A candidate that wins actual-anchor stress but fails LOO/L2O stability is likely another underidentified public-inverse artifact.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(inv.KEY).reset_index(drop=True)
    records, mask_meta = inv.mask_records(sample)
    selected_masks = inv.selected_mask_indices().merge(mask_meta, on=["mask_index", "mask_kind", "mask_name", "rows"], how="left")
    selected_masks = selected_masks.head(44).reset_index(drop=True)
    preds = inv.load_predictions(sample)
    priors = {
        name: inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64)
        for name, file_name in inv.PRIOR_FILES.items()
        if inv.locate(file_name) is not None
    }
    source_path = OUT / "public_lb_direct_label_robust_selector_sources.csv"
    source = pd.read_csv(source_path) if source_path.exists() else pd.DataFrame()
    robust_lookup = {
        (int(row.mask_index), str(row.prior_name)): float(row.robust_source_score)
        for row in source.itertuples(index=False)
        if hasattr(row, "robust_source_score")
    }
    candidates, arrays = collect_candidates(sample)
    base = arrays["control_a2c8"]
    stage2 = preds["stage2"]

    detail_rows: list[dict[str, object]] = []
    fold_specs: list[tuple[str, tuple[tuple[str, str, float, float], ...]]] = []
    fold_specs.extend(("loo", (anchor,)) for anchor in ALL_ANCHORS)
    fold_specs.extend(("l2o", pair) for pair in combinations(ALL_ANCHORS, 2))

    policies = ["train_best1", "train_best5", "structured_best3", "low_error_best5"]
    for fold_kind, heldout_tuple in fold_specs:
        heldout = list(heldout_tuple)
        heldout_keys = {anchor[0] for anchor in heldout}
        fold_name = "+".join(sorted(heldout_keys))
        train = [anchor for anchor in ALL_ANCHORS if anchor[0] not in heldout_keys]
        fits = build_fits(train, heldout, records, selected_masks, priors, preds, robust_lookup)
        for policy in policies:
            chosen = select_fits(fits, policy)
            if chosen.empty:
                continue
            selector_error = float(chosen["heldout_anchor_abs_error_mean"].mean())
            for candidate in candidates.itertuples(index=False):
                pred = arrays[str(candidate.name)]
                cand_scores = []
                base_scores = []
                for fit in chosen["fit"]:
                    cand_scores.append(score_under_fit(fit, pred, stage2))
                    base_scores.append(score_under_fit(fit, base, stage2))
                delta = float(np.mean(cand_scores) - np.mean(base_scores))
                detail_rows.append(
                    {
                        "fold_kind": fold_kind,
                        "fold_name": fold_name,
                        "policy": policy,
                        "candidate_name": str(candidate.name),
                        "file": str(candidate.file),
                        "n_selected_fits": int(len(chosen)),
                        "delta_vs_a2c8": delta,
                        "candidate_public_proxy": float(np.mean(cand_scores)),
                        "a2c8_public_proxy": float(np.mean(base_scores)),
                        "selector_abs_error_mean": selector_error,
                        "top_mask_kind": str(chosen.iloc[0]["mask_kind"]),
                        "top_mask_name": str(chosen.iloc[0]["mask_name"]),
                        "top_prior_name": str(chosen.iloc[0]["prior_name"]),
                        "top_fit_quality": float(chosen.iloc[0]["fit_quality"]),
                    }
                )

    detail = pd.DataFrame(detail_rows)
    detail.to_csv(DETAIL_OUT, index=False)
    summary = summarize(detail, candidates)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(summary, detail)

    print(REPORT_OUT)
    print("[combined]")
    combined = (
        summary.groupby(["candidate_name", "file", "submit_role"], as_index=False)
        .agg(
            cv_delta_mean=("cv_delta_mean", "mean"),
            cv_delta_p90=("cv_delta_p90", "mean"),
            cv_delta_worst=("cv_delta_worst", "max"),
            cv_win_rate=("cv_win_rate", "mean"),
            selector_abs_error_mean=("selector_abs_error_mean", "mean"),
            actual_anchor_score_final=("actual_anchor_score_final", "first"),
            mean_abs_move_vs_a2c8=("mean_abs_move_vs_a2c8", "first"),
            cv_stability_score=("cv_stability_score", "mean"),
        )
        .sort_values("cv_stability_score")
    )
    print(combined.head(24).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
