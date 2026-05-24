"""Q4 — Per-subject logloss attribution.

If 2-3 subjects dominate the mirror logloss, target-uniform efforts are
misallocated. This script decomposes the mirror_v1 anchor logloss into:

  - per (subject, target) cells
  - per subject totals
  - per subject "explainability" (anchor vs marginal — how much subject prior
    actually buys over global prior on that subject)
  - subject volatility (within-subject label variance, the rough cap on
    achievable per-subject logloss)

Output:
  experiments/q4_per_subject_loss_report.md
  experiments/q4_per_subject_cells.csv

No models trained. No submission generated.
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
MIRROR = ROOT / "outputs" / "validation" / "folds_subject_mirror_v1.json"
REPORT_MD = ROOT / "experiments" / "q4_per_subject_loss_report.md"
CELLS_CSV = ROOT / "experiments" / "q4_per_subject_cells.csv"


def load_train() -> pd.DataFrame:
    df = pd.read_csv(TRAIN_CSV)
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"]).dt.date.astype(str)
    return df


def score_fold(df: pd.DataFrame, fold: dict, alpha: float = 20.0) -> pd.DataFrame:
    idx = {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    train, valid = df.iloc[tr_i].copy(), df.iloc[va_i].copy()
    rows = []
    for t in LABELS:
        g = float(train[t].mean())
        ps = train.groupby("subject_id")[t].sum()
        ns = train.groupby("subject_id")[t].count()
        smoothed = ((ps + alpha * g) / (ns + alpha)).to_dict()
        p_subj = np.clip(np.array([smoothed.get(s, g) for s in valid["subject_id"]]), 0.03, 0.97)
        p_marg = np.full(len(valid), np.clip(g, 0.03, 0.97))
        y = valid[t].astype(int).values
        ll_subj = -(y * np.log(p_subj) + (1 - y) * np.log(1 - p_subj))
        ll_marg = -(y * np.log(p_marg) + (1 - y) * np.log(1 - p_marg))
        for i, (s, llS, llM) in enumerate(zip(valid["subject_id"].values, ll_subj, ll_marg)):
            rows.append({
                "fold": fold.get("name"),
                "subject_id": s,
                "target": t,
                "y": int(y[i]),
                "p_subj": float(p_subj[i]),
                "ll_subj": float(llS),
                "ll_marg": float(llM),
                "ll_lift_vs_marg": float(llM - llS),
            })
    return pd.DataFrame(rows)


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
    df = load_train()
    mirror = json.loads(MIRROR.read_text())
    all_rows = []
    for fold in mirror["folds"]:
        all_rows.append(score_fold(df, fold, alpha=20.0))
    cells = pd.concat(all_rows, ignore_index=True)
    cells.to_csv(CELLS_CSV, index=False)
    print(f"wrote {CELLS_CSV} (n={len(cells)})")

    # per-subject summary (avg across mirror seeds)
    per_subj_target = cells.groupby(["subject_id", "target"]).agg(
        n=("y", "count"),
        ll_subj=("ll_subj", "mean"),
        ll_marg=("ll_marg", "mean"),
        ll_lift=("ll_lift_vs_marg", "mean"),
        pos_rate=("y", "mean"),
    ).round(4).reset_index()

    per_subj = cells.groupby("subject_id").agg(
        n=("y", "count"),
        mean_ll_subj=("ll_subj", "mean"),
        sum_ll_subj=("ll_subj", "sum"),
        mean_ll_marg=("ll_marg", "mean"),
        mean_ll_lift=("ll_lift_vs_marg", "mean"),
    ).round(4)
    per_subj["loss_share"] = (per_subj["sum_ll_subj"] / per_subj["sum_ll_subj"].sum()).round(3)
    per_subj["explainability"] = (per_subj["mean_ll_lift"] / per_subj["mean_ll_marg"]).round(3)
    per_subj = per_subj.sort_values("sum_ll_subj", ascending=False)

    # how concentrated is the loss?
    cumshare = per_subj["loss_share"].cumsum()
    subj_at_50 = cumshare[cumshare >= 0.5].index[0] if (cumshare >= 0.5).any() else None
    subj_at_75 = cumshare[cumshare >= 0.75].index[0] if (cumshare >= 0.75).any() else None

    # per-subject best/worst target
    per_subj_target_pivot = per_subj_target.pivot(index="subject_id", columns="target", values="ll_subj").round(4)

    lines = []
    lines.append("# Q4 — Per-subject logloss attribution\n")
    lines.append(
        "Mirror_v1 fold family (the LB-mimicking fold). subject_prior_a20 anchor.\n"
        "Averaged across 3 mirror seeds.\n"
    )

    lines.append("\n## 1. Per-subject totals (sorted by total loss contribution)\n")
    lines.append(
        f"Cumulative top subjects covering ≥50% of total loss: top **{cumshare[cumshare>=0.5].index[0] if (cumshare>=0.5).any() else 'N/A'}** ranked subject.\n"
    )
    lines.append(df_to_md(per_subj))

    lines.append("\n\n## 2. Per-(subject, target) anchor logloss\n")
    lines.append(df_to_md(per_subj_target_pivot))

    lines.append("\n\n## 3. Per-subject mean lift vs marginal (subject prior usefulness)\n")
    lift_pivot = per_subj_target.pivot(index="subject_id", columns="target", values="ll_lift").round(4)
    lines.append("Positive = subject prior beats marginal. Negative = subject prior overfit / wrong.\n\n")
    lines.append(df_to_md(lift_pivot))

    # interpretation
    top3_share = float(per_subj["loss_share"].iloc[:3].sum())
    bot3_share = float(per_subj["loss_share"].iloc[-3:].sum())
    worst_subj = per_subj.index[0]
    worst_target_per_subj = per_subj_target_pivot.idxmax(axis=1).to_dict()
    overall_lift = float(per_subj["mean_ll_lift"].mean())

    lines.append("\n\n## 4. Interpretation\n")
    lines.append(
        f"- top-3 subjects account for {top3_share*100:.1f}% of total mirror loss\n"
        f"- bottom-3 subjects account for {bot3_share*100:.1f}%\n"
        f"- worst single subject: **{worst_subj}** ({per_subj.loc[worst_subj,'loss_share']*100:.1f}% of total)\n"
        f"- mean subject_prior lift over marginal: {overall_lift:+.4f}\n"
        f"  (positive = the smoothing toward per-subject mean is buying something on average)\n"
        f"- per-subject hardest target: {json.dumps(worst_target_per_subj, ensure_ascii=False)}\n"
    )
    lines.append(
        "\n### Decision implications\n"
        "- If top-3 subjects > 50% of loss → subject-specialized treatment is high-ROI.\n"
        "- If any subject has *negative* mean lift (subject prior worse than marginal) → that subject's "
        "label distribution is unusual; subject prior is over-confident in the wrong direction. Consider "
        "α decay for those subjects only.\n"
        "- If per-subject hardest targets cluster (e.g., all subjects worst on Q2) → the difficulty is in the "
        "target, not the subject. If they vary by subject → there are subject-specific *target weaknesses*.\n"
    )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")
    print("\nper-subject summary:")
    print(per_subj)


if __name__ == "__main__":
    main()
