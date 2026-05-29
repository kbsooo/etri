#!/usr/bin/env python3
"""E123 E101 transition-motif S3 sensor audit.

SAUNA question:
E101 missed E95 by roughly one high-impact S3 boundary cell. E118 showed that
the direct S3 flank label still supports the critical rank-23 cell, and E122
showed simple subject/raw priors explain only the aggregate branch. This audit
asks whether a different, public-independent signal exists: the full Q/S
transition motif around a hidden row.

The important negative result is also useful. If cross-target transition motif
features validate locally but still keep rank 23 in the support branch, then
the remaining E95/E101 boundary is not a visible neighbor-state problem.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402


E95_PUBLIC = 0.5762913298
E101_PUBLIC = 0.5763003660
E101_DELTA = E101_PUBLIC - E95_PUBLIC
N_ALL_CELLS = 250 * 7

CELL_IN = OUT / "e118_e101_flank_label_support_cells.csv"
SUMMARY_OUT = OUT / "e123_e101_transition_motif_s3_sensor_summary.csv"
CRITICAL_OUT = OUT / "e123_e101_transition_motif_s3_sensor_critical_summary.csv"
VALIDATION_OUT = OUT / "e123_e101_transition_motif_s3_sensor_validation_summary.csv"
REPORT_OUT = OUT / "e123_e101_transition_motif_s3_sensor_report.md"

Q_TARGETS = ["Q1", "Q2", "Q3"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
S_NO3_TARGETS = ["S1", "S2", "S4"]
NO3_TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S4"]
EPS = 1.0e-6


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def clip_prob(x: np.ndarray | pd.Series | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def state_code(values: Iterable[float]) -> float:
    code = 0
    seen = False
    for i, val in enumerate(values):
        if np.isfinite(val):
            seen = True
            code += int(round(float(val))) << i
    return float(code) if seen else np.nan


def safe_logloss(y_true: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y_true.astype(int), clip_prob(p), labels=[0, 1]))


def safe_auc(y_true: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y_true.astype(int))) < 2:
        return float("nan")
    return float(roc_auc_score(y_true.astype(int), clip_prob(p)))


def beta_smooth(prior: float, labels: list[float], weights: list[float], pseudo: float = 2.0) -> float:
    clean = [(float(y), float(w)) for y, w in zip(labels, weights) if np.isfinite(y) and np.isfinite(w) and w > 0]
    if not clean:
        return float(np.clip(prior, EPS, 1.0 - EPS))
    denom = pseudo + sum(w for _, w in clean)
    numer = pseudo * float(prior) + sum(y * w for y, w in clean)
    return float(np.clip(numer / denom, EPS, 1.0 - EPS))


def subject_prior_table(train: pd.DataFrame, known_idx: np.ndarray) -> tuple[dict[str, float], float, dict[str, int]]:
    known = train.loc[known_idx]
    global_prior = float(known["S3"].mean())
    subject_prior = {str(sid): float(g["S3"].mean()) for sid, g in known.groupby("subject_id", sort=False)}
    subject_count = {str(sid): int(len(g)) for sid, g in known.groupby("subject_id", sort=False)}
    return subject_prior, global_prior, subject_count


def split_nearest(known: pd.DataFrame, row_date: pd.Timestamp) -> tuple[pd.Series | None, pd.Series | None]:
    if known.empty:
        return None, None
    before = known[known["lifelog_date"] < row_date]
    after = known[known["lifelog_date"] > row_date]
    prev = before.iloc[-1] if len(before) else None
    next_ = after.iloc[0] if len(after) else None
    return prev, next_


def add_target_pair_features(rec: dict[str, float], prev: pd.Series | None, next_: pd.Series | None) -> None:
    for target in TARGETS:
        py = float(prev[target]) if prev is not None else np.nan
        ny = float(next_[target]) if next_ is not None else np.nan
        rec[f"prev_{target}"] = py
        rec[f"next_{target}"] = ny
        rec[f"mean_{target}"] = np.nanmean([py, ny]) if np.isfinite(py) or np.isfinite(ny) else np.nan
        rec[f"delta_{target}"] = ny - py if np.isfinite(py) and np.isfinite(ny) else np.nan
        rec[f"agree_{target}"] = float(py == ny) if np.isfinite(py) and np.isfinite(ny) else np.nan


def add_group_features(rec: dict[str, float], prev: pd.Series | None, next_: pd.Series | None) -> None:
    groups = {
        "q": Q_TARGETS,
        "s": S_TARGETS,
        "s_no3": S_NO3_TARGETS,
        "all": TARGETS,
        "all_no3": NO3_TARGETS,
    }
    for name, cols in groups.items():
        pvals = [float(prev[c]) for c in cols] if prev is not None else []
        nvals = [float(next_[c]) for c in cols] if next_ is not None else []
        psum = float(np.sum(pvals)) if pvals else np.nan
        nsum = float(np.sum(nvals)) if nvals else np.nan
        rec[f"prev_{name}_sum"] = psum
        rec[f"next_{name}_sum"] = nsum
        rec[f"mean_{name}_sum"] = np.nanmean([psum, nsum]) if np.isfinite(psum) or np.isfinite(nsum) else np.nan
        rec[f"delta_{name}_sum"] = nsum - psum if np.isfinite(psum) and np.isfinite(nsum) else np.nan
        rec[f"prev_{name}_state"] = state_code(pvals)
        rec[f"next_{name}_state"] = state_code(nvals)
        rec[f"same_{name}_state"] = float(rec[f"prev_{name}_state"] == rec[f"next_{name}_state"]) if (
            np.isfinite(rec[f"prev_{name}_state"]) and np.isfinite(rec[f"next_{name}_state"])
        ) else np.nan


def build_features(
    frame: pd.DataFrame,
    train: pd.DataFrame,
    known_idx: np.ndarray,
    is_train_frame: bool,
    index_col: str,
) -> pd.DataFrame:
    known = train.loc[known_idx].sort_values(["subject_id", "lifelog_date"]).copy()
    by_subject = {str(sid): g.copy() for sid, g in known.groupby("subject_id", sort=False)}
    subject_prior, global_prior, subject_count = subject_prior_table(train, known_idx)

    records: list[dict[str, float]] = []
    for _, row in frame.iterrows():
        sid = str(row["subject_id"])
        row_date = pd.Timestamp(row["lifelog_date"])
        known_subject = by_subject.get(sid, pd.DataFrame())
        if is_train_frame and not known_subject.empty:
            known_subject = known_subject[known_subject.index != int(row[index_col])]
        prev, next_ = split_nearest(known_subject, row_date)
        prev_date = pd.Timestamp(prev["lifelog_date"]) if prev is not None else pd.NaT
        next_date = pd.Timestamp(next_["lifelog_date"]) if next_ is not None else pd.NaT
        prev_gap = float((row_date - prev_date).days) if prev is not None else np.nan
        next_gap = float((next_date - row_date).days) if next_ is not None else np.nan
        subj_prior = float(subject_prior.get(sid, global_prior))
        rec: dict[str, float] = {
            "has_prev": float(prev is not None),
            "has_next": float(next_ is not None),
            "both_flanks": float(prev is not None and next_ is not None),
            "prev_gap_days": prev_gap,
            "next_gap_days": next_gap,
            "min_gap_days": float(np.nanmin([prev_gap, next_gap])) if np.isfinite(prev_gap) or np.isfinite(next_gap) else np.nan,
            "gap_balance": float(prev_gap - next_gap) if np.isfinite(prev_gap) and np.isfinite(next_gap) else np.nan,
            "inv_prev_gap": 1.0 / max(prev_gap, 1.0) if np.isfinite(prev_gap) else 0.0,
            "inv_next_gap": 1.0 / max(next_gap, 1.0) if np.isfinite(next_gap) else 0.0,
            "dow": float(row_date.dayofweek),
            "dow_sin": float(np.sin(2.0 * np.pi * row_date.dayofweek / 7.0)),
            "dow_cos": float(np.cos(2.0 * np.pi * row_date.dayofweek / 7.0)),
            "month": float(row_date.month),
            "day": float(row_date.day),
            "subject_s3_prior": subj_prior,
            "global_s3_prior": float(global_prior),
            "subject_known_count": float(subject_count.get(sid, 0)),
        }
        add_target_pair_features(rec, prev, next_)
        add_group_features(rec, prev, next_)
        rec["s3_flank_beta"] = beta_smooth(
            subj_prior,
            [rec["prev_S3"], rec["next_S3"]],
            [rec["inv_prev_gap"], rec["inv_next_gap"]],
            pseudo=2.0,
        )
        records.append(rec)
    return pd.DataFrame(records, index=frame.index)


def model_columns(x: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    base_drop = {"subject_s3_prior", "global_s3_prior", "subject_known_count", "s3_flank_beta"}
    all_cols = [c for c in x.columns if c not in base_drop]
    no_s3_cols = []
    banned_exact = {
        "prev_S3",
        "next_S3",
        "mean_S3",
        "delta_S3",
        "agree_S3",
        "prev_s_sum",
        "next_s_sum",
        "mean_s_sum",
        "delta_s_sum",
        "prev_s_state",
        "next_s_state",
        "same_s_state",
        "prev_all_sum",
        "next_all_sum",
        "mean_all_sum",
        "delta_all_sum",
        "prev_all_state",
        "next_all_state",
        "same_all_state",
    }
    for col in all_cols:
        if col in banned_exact:
            continue
        no_s3_cols.append(col)
    full_cols = all_cols
    plus_subject_cols = all_cols + ["subject_s3_prior", "global_s3_prior", "subject_known_count", "s3_flank_beta"]
    return no_s3_cols, full_cols, plus_subject_cols


def fit_logistic(x: pd.DataFrame, y: np.ndarray) -> object:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.35, max_iter=2000, solver="lbfgs", random_state=260991),
    ).fit(x, y.astype(int))


def split_indices(train: pd.DataFrame) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    splits: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    tail_val: list[int] = []
    interleaved_val: list[int] = []
    for _, g in train.groupby("subject_id", sort=False):
        idx = g.index.to_numpy(dtype=int)
        n_tail = max(2, int(np.ceil(len(idx) * 0.2)))
        tail_val.extend(idx[-n_tail:].tolist())
        interleaved_val.extend(idx[np.arange(len(idx)) % 5 == 2].tolist())
    all_idx = train.index.to_numpy(dtype=int)
    tail_val_a = np.asarray(sorted(set(tail_val)), dtype=int)
    inter_val_a = np.asarray(sorted(set(interleaved_val)), dtype=int)
    splits["temporal_tail20_by_subject"] = (np.setdiff1d(all_idx, tail_val_a), tail_val_a)
    splits["interleaved_pos_mod5"] = (np.setdiff1d(all_idx, inter_val_a), inter_val_a)
    return splits


def evaluate_validation(train: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    records: list[dict[str, float | str | int]] = []
    last_models: dict[str, object] = {}
    for split_name, (fit_idx, val_idx) in split_indices(train).items():
        fit_frame = train.loc[fit_idx].copy()
        fit_frame["_row_idx"] = fit_frame.index
        val_frame = train.loc[val_idx].copy()
        val_frame["_row_idx"] = val_frame.index
        x_fit = build_features(fit_frame, train, fit_idx, True, "_row_idx")
        x_val = build_features(val_frame, train, fit_idx, True, "_row_idx")
        y_fit = fit_frame["S3"].to_numpy(dtype=int)
        y_val = val_frame["S3"].to_numpy(dtype=int)
        no_s3_cols, full_cols, plus_subject_cols = model_columns(x_fit)
        preds = {
            "subject_prior": x_val["subject_s3_prior"].to_numpy(dtype=np.float64),
            "s3_flank_beta": x_val["s3_flank_beta"].to_numpy(dtype=np.float64),
        }
        for name, cols in [
            ("motif_no_s3", no_s3_cols),
            ("motif_full", full_cols),
            ("motif_plus_subject", plus_subject_cols),
        ]:
            model = fit_logistic(x_fit[cols], y_fit)
            preds[name] = model.predict_proba(x_val[cols])[:, 1]
            if split_name == "temporal_tail20_by_subject":
                last_models[name] = model
                last_models[f"{name}_cols"] = cols
        baseline_ll = safe_logloss(y_val, preds["subject_prior"])
        for name, pred in preds.items():
            records.append(
                {
                    "split": split_name,
                    "sensor": name,
                    "n_fit": int(len(fit_idx)),
                    "n_val": int(len(val_idx)),
                    "logloss": safe_logloss(y_val, pred),
                    "delta_vs_subject_prior": safe_logloss(y_val, pred) - baseline_ll,
                    "auc": safe_auc(y_val, pred),
                    "mean_pred": float(np.mean(pred)),
                    "y_rate": float(np.mean(y_val)),
                }
            )
    return pd.DataFrame(records), last_models


def fit_full_train_models(train: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object], dict[str, list[str]]]:
    all_idx = train.index.to_numpy(dtype=int)
    train_frame = train.copy()
    train_frame["_row_idx"] = train_frame.index
    x_train = build_features(train_frame, train, all_idx, True, "_row_idx")
    y_train = train_frame["S3"].to_numpy(dtype=int)
    no_s3_cols, full_cols, plus_subject_cols = model_columns(x_train)
    columns = {
        "motif_no_s3": no_s3_cols,
        "motif_full": full_cols,
        "motif_plus_subject": plus_subject_cols,
    }
    models = {name: fit_logistic(x_train[cols], y_train) for name, cols in columns.items()}
    return x_train, models, columns


def score_active_cells(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    cells = pd.read_csv(CELL_IN, parse_dates=["sleep_date", "lifelog_date"])
    cells = cells[cells["target"].eq("S3")].copy()
    cells = cells.sort_values("flip_benefit", ascending=False).reset_index(drop=True)
    cells["rank"] = np.arange(1, len(cells) + 1)

    _, models, columns = fit_full_train_models(train)
    sample_rows = sample.loc[cells["sub_idx"].to_numpy(dtype=int)].copy()
    sample_rows["_row_idx"] = np.arange(len(sample_rows))
    x_test = build_features(sample_rows, train, train.index.to_numpy(dtype=int), False, "_row_idx")

    cells["p_y1_motif_no_s3"] = models["motif_no_s3"].predict_proba(x_test[columns["motif_no_s3"]])[:, 1]
    cells["p_y1_motif_full"] = models["motif_full"].predict_proba(x_test[columns["motif_full"]])[:, 1]
    cells["p_y1_motif_plus_subject"] = models["motif_plus_subject"].predict_proba(x_test[columns["motif_plus_subject"]])[:, 1]

    for sensor in ["motif_no_s3", "motif_full", "motif_plus_subject"]:
        p = cells[f"p_y1_{sensor}"].to_numpy(dtype=np.float64)
        support_label = cells["support_label"].to_numpy(dtype=int)
        support_prob = np.where(support_label == 1, p, 1.0 - p)
        cells[f"support_probability_{sensor}"] = support_prob
        cells[f"expected_delta_{sensor}"] = (
            p * cells["delta_y1"].to_numpy(dtype=np.float64)
            + (1.0 - p) * cells["delta_y0"].to_numpy(dtype=np.float64)
        )
    return cells


def summarize_cells(cells: pd.DataFrame, validation: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, float | str]] = []
    sensors = [
        ("subject", "p_y1_subject", "support_probability_subject", "expected_delta_subject"),
        ("s3_flank_beta", "p_y1_both_distance_beta", "support_probability_both_distance_beta", "expected_delta_both_distance_beta"),
        ("motif_no_s3", "p_y1_motif_no_s3", "support_probability_motif_no_s3", "expected_delta_motif_no_s3"),
        ("motif_full", "p_y1_motif_full", "support_probability_motif_full", "expected_delta_motif_full"),
        (
            "motif_plus_subject",
            "p_y1_motif_plus_subject",
            "support_probability_motif_plus_subject",
            "expected_delta_motif_plus_subject",
        ),
    ]
    temporal = validation[validation["split"].eq("temporal_tail20_by_subject")]
    val_delta = dict(zip(temporal["sensor"], temporal["delta_vs_subject_prior"]))
    for name, p_col, support_col, expected_col in sensors:
        exp_sum = float(cells[expected_col].sum())
        exp_public_delta = exp_sum / N_ALL_CELLS
        records.append(
            {
                "sensor": name,
                "expected_active_delta_sum": exp_sum,
                "expected_public_delta_vs_e95": exp_public_delta,
                "actual_e101_public_delta_vs_e95": E101_DELTA,
                "abs_error_to_actual_e101_delta": abs(exp_public_delta - E101_DELTA),
                "mean_support_probability": float(cells[support_col].mean()),
                "top10_support_probability": float(cells.head(10)[support_col].mean()),
                "rank22_support_probability": float(cells.loc[cells["rank"].eq(22), support_col].iloc[0]),
                "rank23_support_probability": float(cells.loc[cells["rank"].eq(23), support_col].iloc[0]),
                "temporal_logloss_delta_vs_subject": float(val_delta.get(name, np.nan)),
            }
        )
    return pd.DataFrame(records).sort_values("abs_error_to_actual_e101_delta")


def write_report(summary: pd.DataFrame, critical: pd.DataFrame, validation: pd.DataFrame) -> None:
    best_actual = summary.iloc[0]
    rank23 = critical[critical["rank"].eq(23)].iloc[0]
    temporal = validation[validation["split"].eq("temporal_tail20_by_subject")].copy()
    interleaved = validation[validation["split"].eq("interleaved_pos_mod5")].copy()
    text = f"""# E123 transition-motif S3 sensor audit

## Question

E101 lost to E95 by `+{E101_DELTA:.10f}` public logloss. E122 says the loss is
roughly one high-impact S3 boundary cell, but the existing direct flank and
subject-prior sensors keep the rank-23 cell in the E101-support branch. This
experiment asks whether the *full Q/S neighbor-state motif* contains an
independent, train-only signal that can separate that cell.

No submission is created here. The output is a gate decision.

## Local stress result

Temporal tail-by-subject validation:

{md_table(temporal[['sensor', 'logloss', 'delta_vs_subject_prior', 'auc', 'mean_pred', 'y_rate']], '.6f')}

Interleaved within-subject validation:

{md_table(interleaved[['sensor', 'logloss', 'delta_vs_subject_prior', 'auc', 'mean_pred', 'y_rate']], '.6f')}

## E101 boundary sensor fit

Sorted by absolute error to the observed E101 public delta:

{md_table(summary, '.9f')}

Best aggregate explanatory sensor: `{best_actual['sensor']}` with expected
public delta `{best_actual['expected_public_delta_vs_e95']:.9f}`.

## Critical S3 cells

{md_table(critical, '.6f')}

## Interpretation

- The no-S3 transition motif is the cleanest independence test: it excludes the
  direct previous/next S3 labels and asks whether Q1/Q2/Q3/S1/S2/S4 neighbor
  state predicts S3.
- If this sensor lowered rank 23 support while surviving temporal validation,
  it would justify a new E101/E95 gate branch.
- Observed rank-23 support under motif_no_s3 is
  `{rank23['support_probability_motif_no_s3']:.6f}`; under motif_plus_subject it
  is `{rank23['support_probability_motif_plus_subject']:.6f}`.
- Therefore this experiment {'opens' if rank23['support_probability_motif_no_s3'] < 0.50 else 'does not open'} a new same-line gate for E101.

## Decision

Do not build a submission from this sensor unless a later public-independent
test contradicts the rank-23 reading. The current bottleneck remains a narrow
S3 hard-tail boundary whose aggregate branch is explainable but whose decisive
cell is not resolved by visible transition motifs.
"""
    REPORT_OUT.write_text(text)


def main() -> None:
    train, sample = hbr.read_data()
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)

    validation, _ = evaluate_validation(train)
    cells = score_active_cells(train, sample)
    summary = summarize_cells(cells, validation)

    critical_cols = [
        "rank",
        "sub_idx",
        "hidden_block_id",
        "sleep_date",
        "support_label",
        "prev_y",
        "next_y",
        "p_y1_subject",
        "p_y1_both_distance_beta",
        "p_y1_motif_no_s3",
        "p_y1_motif_full",
        "p_y1_motif_plus_subject",
        "support_probability_subject",
        "support_probability_both_distance_beta",
        "support_probability_motif_no_s3",
        "support_probability_motif_full",
        "support_probability_motif_plus_subject",
        "support_delta",
        "adverse_delta",
        "flip_benefit",
    ]
    critical = cells[cells["rank"].between(18, 27)][critical_cols].copy()

    validation.to_csv(VALIDATION_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    critical.to_csv(CRITICAL_OUT, index=False)
    write_report(summary, critical, validation)

    print("Wrote:")
    for path in [VALIDATION_OUT, SUMMARY_OUT, CRITICAL_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
