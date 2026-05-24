"""Score a small model zoo on three fold families (chrono_tail / hole / mirror)
built by scripts/78_build_hybrid_validation_folds.py.

Diagnostic only. No submission generated.

Models scored:
  global_mean              — per-target train mean
  subject_prior_a20        — per-subject smoothed mean, alpha=20 toward global
  neighbor_label_avg_k3    — average labels of the 3 nearest same-subject train
                              rows by |date diff|. Designed to be strong on hole
                              folds and weak on tail folds — the regime canary.
  tiny_logistic_topk20     — F-test top-20 features + L2 logistic per target,
                              using features/model_features_v0.parquet

Outputs:
  experiments/hybrid_validation_v1_results.csv   (long format)
  experiments/hybrid_validation_v1_report.md     (summary tables + interpretation)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, clip_prob, logloss  # noqa: E402

VAL_DIR = ROOT / "outputs" / "validation"
TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
FEAT_PARQUET = ROOT / "features" / "model_features_v0.parquet"
RESULTS_CSV = ROOT / "experiments" / "hybrid_validation_v1_results.csv"
REPORT_MD = ROOT / "experiments" / "hybrid_validation_v1_report.md"

FOLD_FILES = {
    "chrono_tail": VAL_DIR / "folds_chrono_tail_v2.json",
    "hole_v1": VAL_DIR / "folds_interleaved_hole_v1.json",
    "mirror_v1": VAL_DIR / "folds_subject_mirror_v1.json",
}


def load_train_with_features() -> pd.DataFrame:
    tr = pd.read_csv(TRAIN_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    feats = pd.read_parquet(FEAT_PARQUET)
    feats["lifelog_date"] = feats["lifelog_date"].astype(str)
    df = tr.merge(feats, on=["subject_id", "lifelog_date"], how="left")
    assert len(df) == len(tr), "feature join lost rows"
    return df


def key_index(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    return {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}


def split_by_fold(df: pd.DataFrame, fold: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = key_index(df)
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    return df.iloc[tr_i].copy(), df.iloc[va_i].copy()


# ============== models ==============

def predict_global_mean(train: pd.DataFrame, valid: pd.DataFrame) -> dict[str, np.ndarray]:
    preds = {}
    for t in LABELS:
        p = float(train[t].mean())
        preds[t] = np.full(len(valid), p, dtype=float)
    return preds


def predict_subject_prior(train: pd.DataFrame, valid: pd.DataFrame, alpha: float = 20.0) -> dict[str, np.ndarray]:
    preds = {}
    for t in LABELS:
        g = float(train[t].mean())
        subj_pos = train.groupby("subject_id")[t].sum()
        subj_cnt = train.groupby("subject_id")[t].count()
        smoothed = (subj_pos + alpha * g) / (subj_cnt + alpha)
        smoothed = smoothed.to_dict()
        preds[t] = np.array([smoothed.get(s, g) for s in valid["subject_id"]], dtype=float)
    return preds


def predict_neighbor_label_avg(train: pd.DataFrame, valid: pd.DataFrame, k: int = 3) -> dict[str, np.ndarray]:
    """For each valid row, average the labels of the k nearest same-subject
    train rows by |date diff|. Reveals regime gap: dominates on holes (neighbors
    on both sides) and degrades on tails (only past neighbors)."""
    train = train.copy()
    valid = valid.copy()
    train["_d"] = pd.to_datetime(train["lifelog_date"])
    valid["_d"] = pd.to_datetime(valid["lifelog_date"])
    preds = {t: np.zeros(len(valid), dtype=float) for t in LABELS}
    by_subj = {s: g.reset_index(drop=True) for s, g in train.groupby("subject_id")}
    global_means = {t: float(train[t].mean()) for t in LABELS}
    for i, (_, row) in enumerate(valid.iterrows()):
        g = by_subj.get(row["subject_id"])
        if g is None or len(g) == 0:
            for t in LABELS:
                preds[t][i] = global_means[t]
            continue
        diff = (g["_d"] - row["_d"]).abs().dt.days.values
        order = np.argsort(diff)[:k]
        for t in LABELS:
            preds[t][i] = float(g.iloc[order][t].mean())
    return preds


def predict_tiny_logistic(
    train: pd.DataFrame, valid: pd.DataFrame, k_features: int = 20, C: float = 0.1
) -> dict[str, np.ndarray]:
    """Per target: SelectKBest(f_classif, k=20) on train fold + L2 logistic.
    Imputes NaN with 0 and standardizes."""
    drop_cols = ["subject_id", "lifelog_date", *LABELS]
    feat_cols = [c for c in train.columns if c not in drop_cols and pd.api.types.is_numeric_dtype(train[c])]
    Xtr_full = train[feat_cols].to_numpy(dtype=float, na_value=0.0)
    Xva_full = valid[feat_cols].to_numpy(dtype=float, na_value=0.0)
    preds = {}
    for t in LABELS:
        ytr = train[t].astype(int).to_numpy()
        if ytr.std() < 1e-6:
            preds[t] = np.full(len(valid), float(ytr.mean()), dtype=float)
            continue
        sel = SelectKBest(f_classif, k=min(k_features, Xtr_full.shape[1]))
        Xtr = sel.fit_transform(Xtr_full, ytr)
        Xva = sel.transform(Xva_full)
        sc = StandardScaler().fit(Xtr)
        Xtr = sc.transform(Xtr)
        Xva = sc.transform(Xva)
        clf = LogisticRegression(C=C, max_iter=2000, solver="lbfgs")
        clf.fit(Xtr, ytr)
        preds[t] = clf.predict_proba(Xva)[:, 1]
    return preds


MODELS = {
    "global_mean": predict_global_mean,
    "subject_prior_a20": predict_subject_prior,
    "neighbor_label_avg_k3": predict_neighbor_label_avg,
    "tiny_logistic_topk20": predict_tiny_logistic,
}


# ============== driver ==============

def score_one(preds: dict[str, np.ndarray], valid: pd.DataFrame) -> dict[str, float]:
    scores = {}
    for t in LABELS:
        y = valid[t].astype(int).values
        p = np.clip(preds[t], 0.03, 0.97)
        scores[t] = logloss(y, p)
    return scores


def main():
    df = load_train_with_features()
    rows = []
    for family, fpath in FOLD_FILES.items():
        cfg = json.loads(fpath.read_text())
        for fold in cfg["folds"]:
            train, valid = split_by_fold(df, fold)
            if len(valid) == 0:
                continue
            for model_name, fn in MODELS.items():
                preds = fn(train, valid)
                sc = score_one(preds, valid)
                row = {
                    "family": family,
                    "fold": fold.get("name"),
                    "model": model_name,
                    "n_train": int(len(train)),
                    "n_valid": int(len(valid)),
                    "mean_logloss": float(np.mean(list(sc.values()))),
                }
                for t in LABELS:
                    row[f"ll_{t}"] = sc[t]
                rows.append(row)
                print(
                    f"{family:13s} {fold.get('name'):24s} {model_name:24s}"
                    f"  ll={row['mean_logloss']:.4f}  n_tr={row['n_train']:3d} n_va={row['n_valid']:3d}"
                )

    res = pd.DataFrame(rows)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_CSV, index=False)
    print(f"\nwrote {RESULTS_CSV}")

    write_report(res)


def df_to_md(df: pd.DataFrame) -> str:
    """Minimal markdown table without the tabulate dependency."""
    cols = list(df.columns)
    idx_name = df.index.name or ""
    head = "| " + " | ".join([idx_name, *map(str, cols)]) + " |"
    sep = "|" + "|".join(["---"] * (1 + len(cols))) + "|"
    lines = [head, sep]
    for ix, row in df.iterrows():
        cells = [str(ix)] + [f"{v:.4f}" if isinstance(v, (int, float, np.floating)) and not pd.isna(v) else str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(res: pd.DataFrame) -> None:
    lines = []
    lines.append("# Hybrid validation v1 — results report\n")
    lines.append(
        "Three fold families (chrono_tail / hole_v1 / mirror_v1) scored on the\n"
        "same model zoo. Mirror family weights are sized to mimic the actual\n"
        "test inside/after composition (156/94 = 62%/38%) per subject.\n"
    )

    lines.append("\n## 1. Mean logloss by model × family (avg over folds in family)\n")
    agg = (
        res.groupby(["model", "family"])["mean_logloss"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    pivot_mean = agg.pivot(index="model", columns="family", values="mean").round(4)
    pivot_std = agg.pivot(index="model", columns="family", values="std").round(4)
    lines.append("**Mean over folds:**\n")
    lines.append(df_to_md(pivot_mean))
    lines.append("\n\n**Std over folds:**\n")
    lines.append(df_to_md(pivot_std))

    lines.append("\n\n## 2. Regime gap: tail minus hole (positive = tail harder)\n")
    if {"chrono_tail", "hole_v1"} <= set(pivot_mean.columns):
        gap = (pivot_mean["chrono_tail"] - pivot_mean["hole_v1"]).round(4).to_frame("tail_minus_hole")
        gap["mirror"] = pivot_mean.get("mirror_v1")
        lines.append(df_to_md(gap))
        lines.append(
            "\n\nInterpretation: a *large positive* gap means the model leans on hole-only "
            "advantage (neighbor labels). The neighbor_label_avg_k3 row is the canary: if its "
            "gap is large, the two regimes are genuinely different and chrono_tail CV alone is "
            "systematically too pessimistic *for hole-friendly models* (and too optimistic for "
            "hole-fragile models).\n"
        )

    lines.append("\n## 3. Per-target mean logloss (averaged over folds, by family)\n")
    long = res.melt(
        id_vars=["model", "family", "fold"],
        value_vars=[f"ll_{t}" for t in LABELS],
        var_name="target",
        value_name="ll",
    )
    long["target"] = long["target"].str.removeprefix("ll_")
    per_t = long.groupby(["family", "model", "target"])["ll"].mean().round(4).reset_index()
    for fam in ["chrono_tail", "hole_v1", "mirror_v1"]:
        sub = per_t[per_t["family"] == fam]
        if sub.empty:
            continue
        lines.append(f"\n### {fam}\n")
        tbl = sub.pivot(index="model", columns="target", values="ll").round(4)
        tbl["mean"] = tbl.mean(axis=1).round(4)
        lines.append(df_to_md(tbl))

    lines.append("\n\n## 4. Decision rules suggested by this table\n")
    lines.append(
        "- If `subject_prior_a20` mirror score ≈ subject_prior chrono_tail score, the\n"
        "  static-subject baseline is regime-stable and is the right anchor.\n"
        "- If `neighbor_label_avg_k3` has a large negative `tail_minus_hole` (much better on\n"
        "  hole), confirm: chrono_tail is *not* a substitute for the hole regime.\n"
        "- If `tiny_logistic_topk20` mirror score is *worse* than its chrono_tail score,\n"
        "  the public LB gap (CV 0.5933 → LB 0.6421) is at least partly explained by\n"
        "  hole-regime degradation, not by overfit per se.\n"
        "- Submission gate proposal: any new submission must satisfy\n"
        "      mirror_v1_avg ≤ best_known_mirror + 0.005\n"
        "    AND no per-target hole_v1 logloss worse than subject_prior_a20 + 0.01.\n"
    )

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
