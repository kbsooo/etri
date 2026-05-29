from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q2", "S3"]
TOTAL_TEST_CELLS = 500 * 7
E95_EDGE_VS_MIXMIN = 0.0000153107
N_SIMS = 200_000

CELLS_IN = OUT / "e105_e101_public_label_breakeven_cells.csv"
RAW_DAILY_IN = OUT / "e113_sauna_raw_context_daily_features.csv"
E113_RESULTS_IN = OUT / "e113_sauna_raw_context_visibility_results.csv"

CELLS_OUT = OUT / "e114_e101_raw_context_support_cells.csv"
TARGET_OUT = OUT / "e114_e101_raw_context_support_by_target.csv"
SUMMARY_OUT = OUT / "e114_e101_raw_context_support_summary.csv"
REPORT_OUT = OUT / "e114_e101_raw_context_support_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 1e-6, 1.0 - 1e-6)


def smooth_rate(y: np.ndarray) -> float:
    return float((y.sum() + 0.5) / (len(y) + 1.0))


def train_subject_prior_features(train: pd.DataFrame, target: str) -> np.ndarray:
    y = train[target].to_numpy(dtype=float)
    global_rate = smooth_rate(y)
    out = np.full(len(train), global_rate, dtype=float)
    for _, grp in train.groupby("subject_id", sort=False):
        idx = grp.index.to_numpy()
        vals = train.loc[idx, target].to_numpy(dtype=float)
        if len(idx) <= 1:
            out[idx] = global_rate
            continue
        # Leave the current label out so the prior feature cannot memorize y.
        out[idx] = (vals.sum() - vals + 0.5) / (len(vals) - 1 + 1.0)
    return clip_prob(out)


def test_subject_prior_features(train: pd.DataFrame, test: pd.DataFrame, target: str) -> np.ndarray:
    y = train[target].to_numpy(dtype=float)
    global_rate = smooth_rate(y)
    rates = {
        subject: smooth_rate(grp[target].to_numpy(dtype=float))
        for subject, grp in train.groupby("subject_id", sort=False)
    }
    out = test["subject_id"].map(rates).fillna(global_rate).to_numpy(dtype=float)
    return clip_prob(out)


def fit_raw_plus_prior(
    train_x: pd.DataFrame,
    test_x: pd.DataFrame,
    y: np.ndarray,
) -> np.ndarray:
    if len(np.unique(y)) < 2:
        return np.full(len(test_x), smooth_rate(y), dtype=float)
    pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.1, max_iter=2000, solver="lbfgs"),
    )
    pipe.fit(train_x, y)
    return clip_prob(pipe.predict_proba(test_x)[:, 1])


def expected_delta(cells: pd.DataFrame, prob_col: str) -> np.ndarray:
    p = cells[prob_col].to_numpy(dtype=float)
    d1 = cells["delta_e101_minus_e95_y1"].to_numpy(dtype=float)
    d0 = cells["delta_e101_minus_e95_y0"].to_numpy(dtype=float)
    return p * d1 + (1.0 - p) * d0


def support_probability(cells: pd.DataFrame, prob_col: str) -> np.ndarray:
    p = cells[prob_col].to_numpy(dtype=float)
    support = cells["support_label"].to_numpy(dtype=int)
    return np.where(support == 1, p, 1.0 - p)


def simulate(cells: pd.DataFrame, prob_col: str, rng: np.random.Generator) -> dict[str, float]:
    p = cells[prob_col].to_numpy(dtype=float)
    d1 = cells["delta_e101_minus_e95_y1"].to_numpy(dtype=float)
    d0 = cells["delta_e101_minus_e95_y0"].to_numpy(dtype=float)
    labels = rng.random((N_SIMS, len(cells))) < p
    delta = np.where(labels, d1, d0).sum(axis=1) / TOTAL_TEST_CELLS
    return {
        "mean_delta_vs_e95": float(delta.mean()),
        "p_e101_beats_e95": float(np.mean(delta < 0.0)),
        "p_e101_beats_by_5e_6": float(np.mean(delta < -5.0e-6)),
        "p_e101_matches_e95_edge": float(np.mean(delta < -E95_EDGE_VS_MIXMIN)),
        "p_e101_worse_by_2e_5": float(np.mean(delta > 2.0e-5)),
        "p05_delta": float(np.quantile(delta, 0.05)),
        "p50_delta": float(np.quantile(delta, 0.50)),
        "p95_delta": float(np.quantile(delta, 0.95)),
    }


def md_table(frame: pd.DataFrame, float_fmt: str = ".6f") -> str:
    if frame.empty:
        return "(empty)"
    cols = list(frame.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(format(val, float_fmt))
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    raw_daily = pd.read_csv(RAW_DAILY_IN)
    e113 = pd.read_csv(E113_RESULTS_IN)
    cells = pd.read_csv(CELLS_IN)
    cells = cells[cells["active"].astype(bool)].copy()

    for frame in [train, test, raw_daily, cells]:
        if "lifelog_date" in frame.columns:
            frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"])
        if "sleep_date" in frame.columns:
            frame["sleep_date"] = pd.to_datetime(frame["sleep_date"])

    raw_cols = [c for c in raw_daily.columns if c not in {"subject_id", "lifelog_date"}]
    train_feat = train.merge(raw_daily, on=["subject_id", "lifelog_date"], how="left")
    test_feat = test.merge(raw_daily, on=["subject_id", "lifelog_date"], how="left")
    train_feat[raw_cols] = train_feat[raw_cols].fillna(0.0)
    test_feat[raw_cols] = test_feat[raw_cols].fillna(0.0)

    pred_columns: dict[str, np.ndarray] = {}
    subject_columns: dict[str, np.ndarray] = {}
    global_columns: dict[str, np.ndarray] = {}
    for target in TARGETS:
        y = train[target].to_numpy(dtype=int)
        train_prior = train_subject_prior_features(train, target)
        test_prior = test_subject_prior_features(train, test, target)
        train_x = train_feat[raw_cols].copy()
        test_x = test_feat[raw_cols].copy()
        train_x[f"{target}__subject_prior_feature"] = train_prior
        test_x[f"{target}__subject_prior_feature"] = test_prior
        raw_plus_prior = fit_raw_plus_prior(train_x, test_x, y)
        pred_columns[target] = raw_plus_prior
        subject_columns[target] = test_prior
        global_columns[target] = np.full(len(test), smooth_rate(y), dtype=float)

    for target in TARGETS:
        target_mask = cells["target"].eq(target)
        sub_idx = cells.loc[target_mask, "sub_idx"].to_numpy(dtype=int)
        cells.loc[target_mask, "raw_plus_prior_y1"] = pred_columns[target][sub_idx]
        cells.loc[target_mask, "full_subject_prior_y1"] = subject_columns[target][sub_idx]
        cells.loc[target_mask, "full_global_prior_y1"] = global_columns[target][sub_idx]

    temporal_delta = (
        e113[e113["split"].eq("temporal_last25_by_subject")]
        .set_index("target")["raw_plus_prior_delta_vs_subject_prior"]
        .to_dict()
    )
    cells["target_temporal_raw_delta"] = cells["target"].map(temporal_delta)
    cells["temporal_valid_raw_target"] = cells["target_temporal_raw_delta"] < 0.0
    cells["validation_gated_raw_y1"] = np.where(
        cells["temporal_valid_raw_target"],
        cells["raw_plus_prior_y1"],
        cells["full_subject_prior_y1"],
    )

    prior_cols = [
        "global_prior_y1",
        "subject_prior_y1",
        "full_global_prior_y1",
        "full_subject_prior_y1",
        "raw_plus_prior_y1",
        "validation_gated_raw_y1",
    ]
    for col in prior_cols:
        cells[f"{col}_support_probability"] = support_probability(cells, col)
        cells[f"{col}_expected_delta"] = expected_delta(cells, col)
        cells[f"{col}_expected_delta_per_all_cells"] = (
            cells[f"{col}_expected_delta"] / TOTAL_TEST_CELLS
        )

    subject_support = cells["subject_prior_y1_support_probability"]
    for col in prior_cols:
        cells[f"{col}_support_minus_subject_support"] = (
            cells[f"{col}_support_probability"] - subject_support
        )

    by_target_rows = []
    for target, grp in cells.groupby("target", sort=False):
        rec: dict[str, object] = {
            "target": target,
            "active_cells": int(len(grp)),
            "temporal_raw_delta_vs_subject_prior": float(
                grp["target_temporal_raw_delta"].iloc[0]
            ),
            "temporal_valid_raw_target": bool(grp["temporal_valid_raw_target"].iloc[0]),
            "flip_benefit_share": float(grp["flip_benefit"].sum() / cells["flip_benefit"].sum()),
        }
        for col in [
            "subject_prior_y1",
            "raw_plus_prior_y1",
            "validation_gated_raw_y1",
        ]:
            rec[f"{col}_support_probability_mean"] = float(
                grp[f"{col}_support_probability"].mean()
            )
            rec[f"{col}_expected_delta_per_all_cells_sum"] = float(
                grp[f"{col}_expected_delta_per_all_cells"].sum()
            )
        by_target_rows.append(rec)
    by_target = pd.DataFrame(by_target_rows)

    rng = np.random.default_rng(114)
    summary_rows = []
    for col in [
        "global_prior_y1",
        "subject_prior_y1",
        "full_subject_prior_y1",
        "raw_plus_prior_y1",
        "validation_gated_raw_y1",
    ]:
        rec = {"probability_source": col}
        rec.update(simulate(cells, col, rng))
        rec["mean_support_probability"] = float(cells[f"{col}_support_probability"].mean())
        rec["expected_delta_sum"] = float(cells[f"{col}_expected_delta_per_all_cells"].sum())
        rec["weighted_support_minus_subject"] = float(
            np.average(
                cells[f"{col}_support_minus_subject_support"],
                weights=cells["flip_benefit"],
            )
        )
        summary_rows.append(rec)
    summary = pd.DataFrame(summary_rows)

    cells.to_csv(CELLS_OUT, index=False)
    by_target.to_csv(TARGET_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)

    key_cols = [
        "probability_source",
        "expected_delta_sum",
        "mean_delta_vs_e95",
        "p_e101_beats_e95",
        "p_e101_matches_e95_edge",
        "mean_support_probability",
        "weighted_support_minus_subject",
        "p95_delta",
    ]
    target_cols = [
        "target",
        "active_cells",
        "temporal_raw_delta_vs_subject_prior",
        "temporal_valid_raw_target",
        "flip_benefit_share",
        "subject_prior_y1_support_probability_mean",
        "raw_plus_prior_y1_support_probability_mean",
        "validation_gated_raw_y1_support_probability_mean",
        "subject_prior_y1_expected_delta_per_all_cells_sum",
        "raw_plus_prior_y1_expected_delta_per_all_cells_sum",
        "validation_gated_raw_y1_expected_delta_per_all_cells_sum",
    ]

    raw_summary = summary[summary["probability_source"].eq("raw_plus_prior_y1")].iloc[0]
    gated_summary = summary[summary["probability_source"].eq("validation_gated_raw_y1")].iloc[0]
    subject_summary = summary[summary["probability_source"].eq("subject_prior_y1")].iloc[0]

    if raw_summary["expected_delta_sum"] < subject_summary["expected_delta_sum"]:
        raw_direction = "supports E101 more than subject prior"
    else:
        raw_direction = "does not support E101 more than subject prior"
    if gated_summary["expected_delta_sum"] < subject_summary["expected_delta_sum"]:
        gated_direction = "improves after validation-gating"
    else:
        gated_direction = "still fails after validation-gating"

    report = f"""# E114 E101 Raw-Context Support Audit

## Question

E113 rejected broad raw-context prediction. The smaller question is whether the
same raw context can still act as an energy for the `50` E101 active cells:
does it assign higher probability to the hard labels that would make E101 beat
E95?

## Summary

{md_table(summary[key_cols], '.9f')}

## By Target

{md_table(by_target[target_cols], '.9f')}

## Interpretation

- Raw+prior {raw_direction}.
- Validation-gated raw, which trusts raw only on temporal-valid targets, {gated_direction}.
- Temporal validation trusts S3 but rejects Q2: Q2 raw temporal delta is `{float(by_target[by_target['target'].eq('Q2')]['temporal_raw_delta_vs_subject_prior'].iloc[0]):+.6f}`, S3 raw temporal delta is `{float(by_target[by_target['target'].eq('S3')]['temporal_raw_delta_vs_subject_prior'].iloc[0]):+.6f}`.

This is not a submission model. If raw support improves E101, it is only a weak
interpretation energy because E113 already rejected broad raw-context
calibration. If it does not improve E101, raw context is demoted further: it
cannot rescue Q temporal state and cannot pre-validate E101's active-cell label
world.

## Outputs

- `{CELLS_OUT.name}`
- `{TARGET_OUT.name}`
- `{SUMMARY_OUT.name}`
"""
    REPORT_OUT.write_text(report)
    print(f"wrote {CELLS_OUT}")
    print(f"wrote {TARGET_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
