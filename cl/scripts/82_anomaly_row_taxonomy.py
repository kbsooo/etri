"""Q5 — Anomaly row taxonomy.

The IRT measurement model (advanced76) flagged ~20% of rows as high-residual.
But the residual signal lumps three very different things:
  (a) label noise / true transition day  — neighbors disagree among themselves
  (b) sensor failure / measurement gap   — coverage features anomalous
  (c) rare context event                 — non-coverage features anomalous

These need different treatment:
  (a) → downweight in loss / no smoothing
  (b) → shrink prediction toward anchor (anomaly gate)
  (c) → may be the *signal*; do not shrink

This script classifies every train row into one of those buckets using only
observable train info (no test leakage), then reports how much each bucket
contributes to subject_prior_a20 mirror logloss.

Outputs:
  experiments/q5_anomaly_taxonomy_report.md
  experiments/q5_anomaly_taxonomy_rows.csv      (row-level classification)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, logloss  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
COVERAGE_PARQUET = ROOT / "features" / "observation_coverage_features.parquet"
MIRROR_FOLDS = ROOT / "outputs" / "validation" / "folds_subject_mirror_v1.json"
REPORT_MD = ROOT / "experiments" / "q5_anomaly_taxonomy_report.md"
ROWS_CSV = ROOT / "experiments" / "q5_anomaly_taxonomy_rows.csv"


def load_data():
    tr = pd.read_csv(TRAIN_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    cov = pd.read_parquet(COVERAGE_PARQUET)
    if "date" in cov.columns and "lifelog_date" not in cov.columns:
        cov = cov.rename(columns={"date": "lifelog_date"})
    cov["lifelog_date"] = pd.to_datetime(cov["lifelog_date"]).dt.date.astype(str)
    return tr, cov


def per_row_anchor_logloss(df: pd.DataFrame, alpha: float = 20.0) -> pd.DataFrame:
    """Per-row contribution to subject_prior_a20 logloss, on the FULL train."""
    out = df.copy()
    for t in LABELS:
        g = float(df[t].mean())
        ps = df.groupby("subject_id")[t].sum()
        ns = df.groupby("subject_id")[t].count()
        smoothed = ((ps + alpha * g) / (ns + alpha)).to_dict()
        p = np.clip(np.array([smoothed.get(s, g) for s in df["subject_id"]]), 0.03, 0.97)
        y = df[t].astype(int).values
        out[f"ll_{t}"] = -(y * np.log(p) + (1 - y) * np.log(1 - p))
    out["ll_mean"] = out[[f"ll_{t}" for t in LABELS]].mean(axis=1)
    return out


def neighbor_disagreement(df: pd.DataFrame, window: int = 2) -> pd.DataFrame:
    """For each row, how often does the row's labels disagree with the *agreed*
    labels of nearby same-subject rows?
    score_a = fraction of targets where neighbors agree (within tolerance) but
              this row breaks that agreement.
    Higher = more likely a true behavioral transition or label noise."""
    df = df.copy()
    df["_d"] = pd.to_datetime(df["lifelog_date"])
    df = df.sort_values(["subject_id", "_d"]).reset_index(drop=True)
    scores = []
    for i in range(len(df)):
        row = df.iloc[i]
        same_subj = df[(df["subject_id"] == row["subject_id"]) & (df.index != i)]
        diff = (same_subj["_d"] - row["_d"]).dt.days.abs()
        neigh = same_subj[(diff > 0) & (diff <= window)]
        if len(neigh) < 2:
            scores.append(np.nan)
            continue
        broken = 0
        considered = 0
        for t in LABELS:
            vals = neigh[t].values
            if len(vals) == 0:
                continue
            considered += 1
            n_pos = int((vals == 1).sum())
            n_neg = int((vals == 0).sum())
            # neighbors agree if one class dominates
            if max(n_pos, n_neg) / len(vals) >= 0.8:
                consensus = 1 if n_pos > n_neg else 0
                if int(row[t]) != consensus:
                    broken += 1
        scores.append(broken / considered if considered else np.nan)
    df["neighbor_disagreement_rate"] = scores
    return df[["subject_id", "lifelog_date", "neighbor_disagreement_rate"]]


def coverage_anomaly_score(df: pd.DataFrame, cov: pd.DataFrame) -> pd.DataFrame:
    """Per row, z-score of selected coverage columns vs subject baseline. Max
    abs z across columns = coverage anomaly intensity."""
    cov_cols = [
        c for c in cov.columns
        if any(k in c for k in ["missing_hours", "night_hours", "active_hours", "day_hours", "item_n", "record_n"])
    ]
    if not cov_cols:
        return pd.DataFrame({"subject_id": df["subject_id"], "lifelog_date": df["lifelog_date"], "coverage_anomaly_score": 0.0})
    merged = df[["subject_id", "lifelog_date"]].merge(cov[["subject_id", "lifelog_date", *cov_cols]], on=["subject_id", "lifelog_date"], how="left")
    z_vals = []
    for s, g in merged.groupby("subject_id"):
        sub = g[cov_cols]
        mu = sub.mean()
        sigma = sub.std().replace(0, np.nan)
        z = (sub - mu) / sigma
        max_abs_z = z.abs().max(axis=1)
        z_vals.append(pd.Series(max_abs_z.values, index=g.index, name="coverage_anomaly_score"))
    score = pd.concat(z_vals).sort_index()
    merged["coverage_anomaly_score"] = score.values
    return merged[["subject_id", "lifelog_date", "coverage_anomaly_score"]]


def classify(row: pd.Series, q_neigh: float, q_cov: float, q_ll: float) -> str:
    high_ll = row["ll_mean"] >= q_ll
    if not high_ll:
        return "normal"
    high_neigh = (row["neighbor_disagreement_rate"] >= q_neigh) and not pd.isna(row["neighbor_disagreement_rate"])
    high_cov = (row["coverage_anomaly_score"] >= q_cov) and not pd.isna(row["coverage_anomaly_score"])
    if high_neigh and high_cov:
        return "a_or_b_mixed"
    if high_neigh:
        return "a_label_noise_or_transition"
    if high_cov:
        return "b_sensor_failure"
    return "c_unexplained"


def df_to_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    idx_name = df.index.name or ""
    head = "| " + " | ".join([idx_name, *map(str, cols)]) + " |"
    sep = "|" + "|".join(["---"] * (1 + len(cols))) + "|"
    lines = [head, sep]
    for ix, row in df.iterrows():
        cells = [str(ix)] + [f"{v:.4f}" if isinstance(v, (int, float, np.floating)) and not pd.isna(v) else str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    tr, cov = load_data()
    print(f"train n={len(tr)} coverage n={len(cov)}")

    ll = per_row_anchor_logloss(tr, alpha=20.0)
    nd = neighbor_disagreement(tr, window=2)
    cs = coverage_anomaly_score(tr, cov)

    merged = ll.merge(nd, on=["subject_id", "lifelog_date"]).merge(cs, on=["subject_id", "lifelog_date"], how="left")
    # thresholds: top-quartile of high-residual rows by each axis
    q_ll = merged["ll_mean"].quantile(0.75)
    q_neigh = merged["neighbor_disagreement_rate"].quantile(0.75) if merged["neighbor_disagreement_rate"].notna().any() else 1.0
    q_cov = merged["coverage_anomaly_score"].quantile(0.75) if merged["coverage_anomaly_score"].notna().any() else 1.0
    print(f"thresholds: ll_mean@p75={q_ll:.3f}  neighbor_disagreement@p75={q_neigh:.3f}  coverage@p75={q_cov:.3f}")

    merged["bucket"] = merged.apply(lambda r: classify(r, q_neigh, q_cov, q_ll), axis=1)
    bucket_counts = merged["bucket"].value_counts().to_frame("n")
    bucket_counts["pct"] = (bucket_counts["n"] / len(merged)).round(3)

    # contribution to total logloss per bucket
    contrib = merged.groupby("bucket")["ll_mean"].agg(["mean", "sum", "count"]).round(4)
    contrib["total_share"] = (contrib["sum"] / contrib["sum"].sum()).round(3)

    # per-target high-residual breakdown
    per_target_share = {}
    for t in LABELS:
        s_total = merged[f"ll_{t}"].sum()
        s_high = merged[merged["bucket"] != "normal"][f"ll_{t}"].sum()
        per_target_share[t] = round(s_high / s_total, 3) if s_total > 0 else 0
    per_t_df = pd.Series(per_target_share, name="anomaly_rows_share_of_target_logloss").to_frame()

    ROWS_CSV.parent.mkdir(parents=True, exist_ok=True)
    keep = ["subject_id", "lifelog_date", "ll_mean", "neighbor_disagreement_rate", "coverage_anomaly_score", "bucket"]
    merged[keep].to_csv(ROWS_CSV, index=False)
    print(f"wrote {ROWS_CSV}")

    lines = []
    lines.append("# Q5 — Anomaly row taxonomy\n")
    lines.append(
        "Each train row is classified into one of four buckets based on three\n"
        "axes (anchor logloss, neighbor disagreement, sensor coverage z-score).\n"
        "Goal: distinguish label noise/transition vs sensor failure vs unexplained\n"
        "anomalies so they can be treated differently.\n"
    )
    lines.append(f"\nThresholds (top-quartile by each axis):\n")
    lines.append(f"- `ll_mean` ≥ {q_ll:.3f}\n")
    lines.append(f"- `neighbor_disagreement_rate` ≥ {q_neigh:.3f}\n")
    lines.append(f"- `coverage_anomaly_score` ≥ {q_cov:.3f}\n")

    lines.append("\n## 1. Bucket sizes\n")
    lines.append(df_to_md(bucket_counts))

    lines.append("\n\n## 2. Bucket contribution to anchor logloss\n")
    lines.append(df_to_md(contrib))

    lines.append("\n\n## 3. Share of each target's logloss coming from non-normal rows\n")
    lines.append(df_to_md(per_t_df))

    lines.append("\n\n## 4. Interpretation\n")
    norm_mean = contrib.loc["normal", "mean"] if "normal" in contrib.index else float("nan")
    a_mean = contrib.loc["a_label_noise_or_transition", "mean"] if "a_label_noise_or_transition" in contrib.index else float("nan")
    b_mean = contrib.loc["b_sensor_failure", "mean"] if "b_sensor_failure" in contrib.index else float("nan")
    c_mean = contrib.loc["c_unexplained", "mean"] if "c_unexplained" in contrib.index else float("nan")
    mixed_mean = contrib.loc["a_or_b_mixed", "mean"] if "a_or_b_mixed" in contrib.index else float("nan")
    lines.append(
        f"- normal rows mean anchor logloss: {norm_mean:.4f}\n"
        f"- (a) label noise / transition mean: {a_mean:.4f}\n"
        f"- (b) sensor failure mean: {b_mean:.4f}\n"
        f"- (c) unexplained anomaly mean: {c_mean:.4f}\n"
        f"- mixed (both a & b) mean: {mixed_mean:.4f}\n"
    )
    lines.append(
        "\n### Decision implications\n"
        "- If bucket (a) dominates the high-residual total, anomaly shrinkage will\n"
        "  not help — those rows are *informationally* anomalous and any anchor\n"
        "  prediction will be wrong. Best treatment: accept the loss; do not waste\n"
        "  features on them.\n"
        "- If bucket (b) dominates, coverage-based shrinkage toward anchor will\n"
        "  reduce average loss (we already trust anchor; sensor evidence is bad).\n"
        "- If bucket (c) is large, there is signal we are not capturing — these\n"
        "  rows are anomalous *and* coverage is normal *and* neighbors don't help.\n"
        "  This is where new feature families could matter.\n"
    )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")
    print("\nbucket summary:")
    print(bucket_counts)
    print("\ncontrib summary:")
    print(contrib)


if __name__ == "__main__":
    main()
