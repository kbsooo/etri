#!/usr/bin/env python3
"""E241: train/OOF validation for E240 residual-energy Q3 rules.

E240 showed that simple E208 residual-energy rules pass the same public-free
E237-like stress as the learned E237 selector. That is not enough: those rules
were derived from test-side motif inspection.

This experiment asks whether the same residual-energy scores identify Q3 rows
where the E224-like movement is harmful on train OOF labels. If they do not,
the E240 rules are stress-gate artifacts. If they do, residual PC10 becomes a
real target for a future fold-safe JEPA cell-tail head.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e232_cross_target_support_invariance as e232  # noqa: E402
import e239_e237_cell_motif_atlas as e239  # noqa: E402


RNG = 20260530 + 241
EPS = 1.0e-12

SCORE_OUT = OUT / "e241_residual_pc10_oof_benefit_validation_scores.csv"
STRESS_OUT = OUT / "e241_residual_pc10_oof_benefit_validation_stress.csv"
STRESS_SUMMARY_OUT = OUT / "e241_residual_pc10_oof_benefit_validation_stress_summary.csv"
TEST_CONTEXT_OUT = OUT / "e241_residual_pc10_oof_benefit_validation_test_context.csv"
REPORT_OUT = OUT / "e241_residual_pc10_oof_benefit_validation_report.md"


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in frame.columns if cols is None or c in cols]]
    return e138.md_table(view.head(n), floatfmt)


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yy = np.asarray(y, dtype=int)
    if len(np.unique(yy)) < 2:
        return float("nan")
    return float(roc_auc_score(yy, score))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float:
    yy = np.asarray(y, dtype=int)
    if len(np.unique(yy)) < 2:
        return float("nan")
    return float(average_precision_score(yy, score))


def rank_corr(a: pd.Series, b: pd.Series) -> float:
    aa = pd.to_numeric(a, errors="coerce").rank(method="average")
    bb = pd.to_numeric(b, errors="coerce").rank(method="average")
    return float(aa.corr(bb))


def split_random_stratified(frame: pd.DataFrame, label: np.ndarray, n_splits: int = 5) -> list[tuple[str, np.ndarray, np.ndarray]]:
    out: list[tuple[str, np.ndarray, np.ndarray]] = []
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RNG)
    idx = np.arange(len(frame))
    for i, (tr, va) in enumerate(skf.split(idx, label)):
        out.append((f"random_stratified_{i}", tr, va))
    return out


def split_row_contiguous(frame: pd.DataFrame, n_splits: int = 5) -> list[tuple[str, np.ndarray, np.ndarray]]:
    idx = np.arange(len(frame))
    chunks = np.array_split(idx, n_splits)
    out = []
    for i, va in enumerate(chunks):
        tr = np.setdiff1d(idx, va)
        out.append((f"row_contiguous_{i}", tr, va))
    return out


def split_subject_loo(frame: pd.DataFrame) -> list[tuple[str, np.ndarray, np.ndarray]]:
    out = []
    idx = np.arange(len(frame))
    for subject in sorted(frame["subject_id"].astype(str).unique()):
        va = np.where(frame["subject_id"].astype(str).to_numpy() == subject)[0]
        tr = np.setdiff1d(idx, va)
        out.append((f"subject_loo_{subject}", tr, va))
    return out


def standardize_from_train(train: pd.DataFrame, pred: pd.DataFrame, col: str) -> tuple[pd.Series, pd.Series]:
    mu = float(pd.to_numeric(train[col], errors="coerce").mean())
    sigma = float(pd.to_numeric(train[col], errors="coerce").std(ddof=0))
    if sigma <= EPS:
        return pd.Series(np.zeros(len(train)), index=train.index), pd.Series(np.zeros(len(pred)), index=pred.index)
    return (train[col].astype(float) - mu) / sigma, (pred[col].astype(float) - mu) / sigma


def build_scores(train_q3: pd.DataFrame, test_q3: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train = train_q3.copy()
    test = test_q3.copy()
    base_cols = [
        "abs_logit_step",
        "full_margin",
        "e208_resid_self_abs_mean",
        "e208_nn_target_dist",
        "e208_resid_self_pc10",
        "e208_resid_self_norm",
        "e215_resid_abs_mean",
    ]
    z_train: dict[str, pd.Series] = {}
    z_test: dict[str, pd.Series] = {}
    for col in base_cols:
        zt, zv = standardize_from_train(train, test, col)
        z_train[col] = zt
        z_test[col] = zv

    for frame, z in [(train, z_train), (test, z_test)]:
        frame["score_amp"] = frame["abs_logit_step"].astype(float)
        frame["score_resid_abs"] = frame["e208_resid_self_abs_mean"].astype(float)
        frame["score_nn_dist"] = frame["e208_nn_target_dist"].astype(float)
        frame["score_pc10"] = frame["e208_resid_self_pc10"].astype(float)
        frame["score_resid_norm"] = frame["e208_resid_self_norm"].astype(float)
        frame["score_low_margin"] = -frame["full_margin"].astype(float)
        frame["score_resid_combo"] = (
            z["e208_resid_self_abs_mean"]
            + z["e208_nn_target_dist"]
            + z["e208_resid_self_pc10"]
            + 0.5 * z["e208_resid_self_norm"]
        )
        frame["score_amp_resid_combo"] = z["abs_logit_step"] + frame["score_resid_combo"]
        frame["score_e239_combo"] = frame["score_amp_resid_combo"] - 0.5 * z["full_margin"]
        frame["score_e215_e208_combo"] = (
            z["abs_logit_step"]
            + 0.8 * frame["score_resid_combo"]
            + 0.5 * z["e215_resid_abs_mean"]
            - 0.4 * z["full_margin"]
        )
        frame["score_neg_pc10_control"] = -frame["score_pc10"]
    score_cols = [
        "score_amp",
        "score_resid_abs",
        "score_nn_dist",
        "score_pc10",
        "score_resid_norm",
        "score_low_margin",
        "score_resid_combo",
        "score_amp_resid_combo",
        "score_e239_combo",
        "score_e215_e208_combo",
        "score_neg_pc10_control",
    ]
    return train, test, score_cols


def full_score_summary(train: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    benefit = train["benefit"].astype(float)
    harmful = (benefit < 0.0).astype(int).to_numpy()
    tail10 = (benefit <= float(benefit.quantile(0.10))).astype(int).to_numpy()
    tail20 = (benefit <= float(benefit.quantile(0.20))).astype(int).to_numpy()
    rows: list[dict[str, Any]] = []
    n = len(train)
    for score_col in score_cols:
        score = train[score_col].astype(float).to_numpy()
        for frac in [0.05, 0.10, 0.20]:
            k = max(1, int(round(n * frac)))
            idx = np.argsort(-score, kind="mergesort")[:k]
            selected_benefit = benefit.iloc[idx]
            rows.append(
                {
                    "score": score_col,
                    "top_frac": frac,
                    "selected_n": k,
                    "auc_harmful": safe_auc(harmful, score),
                    "ap_harmful": safe_ap(harmful, score),
                    "auc_tail10": safe_auc(tail10, score),
                    "ap_tail10": safe_ap(tail10, score),
                    "auc_tail20": safe_auc(tail20, score),
                    "benefit_spearman_neg": rank_corr(train[score_col], -benefit),
                    "selected_mean_benefit": float(selected_benefit.mean()),
                    "population_mean_benefit": float(benefit.mean()),
                    "drop_delta_vs_full_per_row": float(selected_benefit.sum() / n),
                    "harmful_rate_selected": float((selected_benefit < 0.0).mean()),
                    "harmful_rate_population": float((benefit < 0.0).mean()),
                    "tail10_rate_selected": float((selected_benefit <= benefit.quantile(0.10)).mean()),
                    "tail20_rate_selected": float((selected_benefit <= benefit.quantile(0.20)).mean()),
                }
            )
    return pd.DataFrame(rows)


def stress_eval(train: pd.DataFrame, score_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    harmful = (train["benefit"].astype(float) < 0.0).astype(int).to_numpy()
    splits = (
        split_random_stratified(train, harmful)
        + split_row_contiguous(train)
        + split_subject_loo(train)
    )
    rows: list[dict[str, Any]] = []
    for split_name, tr, va in splits:
        tr_df = train.iloc[tr]
        va_df = train.iloc[va]
        valid_benefit = va_df["benefit"].astype(float)
        for score_col in score_cols:
            train_score = tr_df[score_col].astype(float)
            valid_score = va_df[score_col].astype(float)
            for frac in [0.05, 0.10, 0.20]:
                k = max(1, int(round(len(va_df) * frac)))
                top_idx = valid_score.sort_values(ascending=False, kind="mergesort").head(k).index
                threshold = float(train_score.quantile(1.0 - frac))
                threshold_idx = valid_score[valid_score >= threshold].index
                for mode, selected_index in [
                    ("valid_top_frac", top_idx),
                    ("train_quantile_threshold", threshold_idx),
                ]:
                    selected_benefit = valid_benefit.loc[selected_index]
                    selected_n = int(len(selected_benefit))
                    if selected_n == 0:
                        rows.append(
                            {
                                "split": split_name,
                                "split_family": split_name.rsplit("_", 1)[0],
                                "score": score_col,
                                "top_frac": frac,
                                "mode": mode,
                                "valid_n": int(len(va_df)),
                                "selected_n": 0,
                                "selected_mean_benefit": np.nan,
                                "valid_mean_benefit": float(valid_benefit.mean()),
                                "drop_delta_vs_full_per_row": 0.0,
                                "harmful_rate_selected": np.nan,
                                "harmful_rate_valid": float((valid_benefit < 0.0).mean()),
                                "tail20_rate_selected": np.nan,
                            }
                        )
                        continue
                    rows.append(
                        {
                            "split": split_name,
                            "split_family": split_name.rsplit("_", 1)[0],
                            "score": score_col,
                            "top_frac": frac,
                            "mode": mode,
                            "valid_n": int(len(va_df)),
                            "selected_n": selected_n,
                            "selected_mean_benefit": float(selected_benefit.mean()),
                            "valid_mean_benefit": float(valid_benefit.mean()),
                            "drop_delta_vs_full_per_row": float(selected_benefit.sum() / max(len(va_df), 1)),
                            "harmful_rate_selected": float((selected_benefit < 0.0).mean()),
                            "harmful_rate_valid": float((valid_benefit < 0.0).mean()),
                            "tail20_rate_selected": float(
                                (selected_benefit <= valid_benefit.quantile(0.20)).mean()
                            ),
                        }
                    )
    stress = pd.DataFrame(rows)
    summary = (
        stress.groupby(["score", "top_frac", "mode"], dropna=False)
        .agg(
            folds=("split", "count"),
            selected_n_mean=("selected_n", "mean"),
            drop_delta_mean=("drop_delta_vs_full_per_row", "mean"),
            drop_delta_std=("drop_delta_vs_full_per_row", "std"),
            win_rate=("drop_delta_vs_full_per_row", lambda x: float((x < 0.0).mean())),
            selected_mean_benefit_mean=("selected_mean_benefit", "mean"),
            harmful_rate_selected_mean=("harmful_rate_selected", "mean"),
            harmful_rate_valid_mean=("harmful_rate_valid", "mean"),
            tail20_rate_selected_mean=("tail20_rate_selected", "mean"),
        )
        .reset_index()
        .sort_values(["top_frac", "mode", "drop_delta_mean"])
    )
    return stress, summary


def test_context(test: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    n = len(test)
    e237_set = set(test.loc[test["e237_drop"].astype(bool), "row_idx"].astype(int))
    swing_set = set(test.loc[test["e230_swing25"].astype(bool), "row_idx"].astype(int))
    risk_set = set(test.loc[test["e230_risk21"].astype(bool), "row_idx"].astype(int))
    for score_col in score_cols:
        score = test[score_col].astype(float)
        for frac in [0.05, 0.10, 0.20]:
            k = max(1, int(round(n * frac)))
            idx = set(test.loc[score.sort_values(ascending=False, kind="mergesort").head(k).index, "row_idx"].astype(int))
            rows.append(
                {
                    "score": score_col,
                    "top_frac": frac,
                    "selected_n": len(idx),
                    "overlap_e237": len(idx & e237_set),
                    "overlap_e230_swing25": len(idx & swing_set),
                    "overlap_e230_risk21": len(idx & risk_set),
                    "jaccard_e237": float(len(idx & e237_set) / len(idx | e237_set)) if idx or e237_set else 1.0,
                    "near_edge2_rate": float(test.loc[test["row_idx"].isin(idx), "near_test_edge_2"].mean()),
                    "gap_adjacent2_rate": float(test.loc[test["row_idx"].isin(idx), "gap_adjacent_2"].mean()),
                    "mean_abs_logit_step": float(test.loc[test["row_idx"].isin(idx), "abs_logit_step"].mean()),
                    "mean_pc10": float(test.loc[test["row_idx"].isin(idx), "e208_resid_self_pc10"].mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["top_frac", "overlap_e237"], ascending=[True, False])


def write_report(scores: pd.DataFrame, stress_summary: pd.DataFrame, test_ctx: pd.DataFrame) -> None:
    score_cols = [
        "score",
        "top_frac",
        "auc_harmful",
        "auc_tail10",
        "auc_tail20",
        "benefit_spearman_neg",
        "drop_delta_vs_full_per_row",
        "harmful_rate_selected",
        "tail20_rate_selected",
    ]
    stress_cols = [
        "score",
        "top_frac",
        "mode",
        "folds",
        "selected_n_mean",
        "drop_delta_mean",
        "drop_delta_std",
        "win_rate",
        "harmful_rate_selected_mean",
        "harmful_rate_valid_mean",
        "tail20_rate_selected_mean",
    ]
    test_cols = [
        "score",
        "top_frac",
        "selected_n",
        "overlap_e237",
        "overlap_e230_swing25",
        "overlap_e230_risk21",
        "jaccard_e237",
        "near_edge2_rate",
        "gap_adjacent2_rate",
    ]
    top_scores = scores[scores["top_frac"].eq(0.10)].sort_values("drop_delta_vs_full_per_row")
    top_stress = stress_summary[
        stress_summary["top_frac"].eq(0.10) & stress_summary["mode"].eq("valid_top_frac")
    ].sort_values("drop_delta_mean")
    top_test = test_ctx[test_ctx["top_frac"].eq(0.10)].sort_values("overlap_e237", ascending=False)
    best_score = top_scores.iloc[0]
    lines = [
        "# E241 Residual PC10 OOF Benefit Validation",
        "",
        "## Question",
        "",
        "Do E240 residual-energy rules identify train OOF Q3 rows where the E224-like movement is harmful, or are they only test-side stress artifacts?",
        "",
        "## Full Train Top-10% Ranking",
        "",
        md_table(top_scores, score_cols, n=20),
        "",
        "## Split Stress Top-10%",
        "",
        md_table(top_stress, stress_cols, n=20),
        "",
        "## Test Top-10% Context",
        "",
        md_table(top_test, test_cols, n=20),
        "",
        "## Decision",
        "",
    ]
    if float(best_score["drop_delta_vs_full_per_row"]) < 0.0:
        lines.append(
            f"- Best full-train score `{best_score['score']}` has negative selected-benefit delta `{best_score['drop_delta_vs_full_per_row']:.9f}`. Residual-energy rules have some train-side support, but split stress must decide whether it is stable enough to materialize."
        )
    else:
        lines.append(
            f"- Best full-train score `{best_score['score']}` still has non-negative selected-benefit delta `{best_score['drop_delta_vs_full_per_row']:.9f}`. E240 residual rules should be treated as test-side stress artifacts, not submission rules."
        )
    lines.append("- No submission is created from E241.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    _, train_long, _, _ = e232.build_long_frames()
    train_q3 = train_long[train_long["task_name"].eq("q3_e224")].copy().sort_values("row_idx").reset_index(drop=True)
    test_q3 = e239.build_rows().copy().sort_values("row_idx").reset_index(drop=True)
    train_q3, test_q3, score_cols = build_scores(train_q3, test_q3)
    scores = full_score_summary(train_q3, score_cols)
    stress, stress_summary = stress_eval(train_q3, score_cols)
    test_ctx = test_context(test_q3, score_cols)
    scores.to_csv(SCORE_OUT, index=False)
    stress.to_csv(STRESS_OUT, index=False)
    stress_summary.to_csv(STRESS_SUMMARY_OUT, index=False)
    test_ctx.to_csv(TEST_CONTEXT_OUT, index=False)
    write_report(scores, stress_summary, test_ctx)
    top = scores[scores["top_frac"].eq(0.10)].sort_values("drop_delta_vs_full_per_row").head(10)
    print("[E241 full-train top10%]")
    print(
        top[
            [
                "score",
                "auc_harmful",
                "auc_tail20",
                "benefit_spearman_neg",
                "drop_delta_vs_full_per_row",
                "harmful_rate_selected",
                "tail20_rate_selected",
            ]
        ].round(9).to_string(index=False)
    )
    stress_top = stress_summary[
        stress_summary["top_frac"].eq(0.10) & stress_summary["mode"].eq("valid_top_frac")
    ].sort_values("drop_delta_mean").head(10)
    print("\n[E241 split stress top10%]")
    print(
        stress_top[
            [
                "score",
                "drop_delta_mean",
                "drop_delta_std",
                "win_rate",
                "harmful_rate_selected_mean",
                "tail20_rate_selected_mean",
            ]
        ].round(9).to_string(index=False)
    )
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
