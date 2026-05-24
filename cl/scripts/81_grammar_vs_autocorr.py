"""Q1 — Is Q-family's lag effect real *grammar* (cross-target dependency) or
just temporal autocorrelation?

For each Q target Y in {Q1,Q2,Q3}, fit five logistic regressions on
chronologically held-out data and compare the held-out logloss / AUC:

  M0: subject_prior_a_tuned                              (anchor)
  M1: M0 + own_lag(Y_t-1)                                (autocorr only)
  M2: M0 + mean(Y over nearest +/- 3 same-subject days)  (local-smoothing)
  M3: M0 + own_lag(Y_t-1) + Y_t+1 (forward neighbor)     (hole-only oracle)
  M4: M0 + all-Q lags (Q1_t-1, Q2_t-1, Q3_t-1)           (cross-target grammar)
  M5: M4 + own_lag(Y_t+1)                                 (full Q grammar in hole)

Decision rules:
  - If M2 ≈ M1 → naive temporal smoothing == own_lag (no smoothing benefit)
  - If M4 - M1 > 0.005 logloss → cross-target grammar is real signal
  - If M5 - M4 > 0.005 → forward neighbors carry independent info (hole-only)
  - If M3 >> M1 → using y_{t+1} is huge (test 62% are holes, real lift available)

Evaluate on three regimes (chrono_tail / hole_v1 / mirror_v1).

Output:
  experiments/q1_grammar_vs_autocorr_report.md
  experiments/q1_grammar_vs_autocorr_per_model.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, logloss  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
VAL_DIR = ROOT / "outputs" / "validation"
FOLD_FILES = {
    "chrono_tail": VAL_DIR / "folds_chrono_tail_v2.json",
    "hole_v1": VAL_DIR / "folds_interleaved_hole_v1.json",
    "mirror_v1": VAL_DIR / "folds_subject_mirror_v1.json",
}
REPORT_MD = ROOT / "experiments" / "q1_grammar_vs_autocorr_report.md"
RESULTS_CSV = ROOT / "experiments" / "q1_grammar_vs_autocorr_per_model.csv"
Q_TARGETS = ["Q1", "Q2", "Q3"]
CLIP = (0.03, 0.97)


def load_train() -> pd.DataFrame:
    df = pd.read_csv(TRAIN_CSV)
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"]).dt.date.astype(str)
    df = df.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    return df


def subject_prior(train: pd.DataFrame, valid: pd.DataFrame, target: str, alpha: float) -> np.ndarray:
    g = float(train[target].mean())
    ps = train.groupby("subject_id")[target].sum()
    ns = train.groupby("subject_id")[target].count()
    smoothed = ((ps + alpha * g) / (ns + alpha)).to_dict()
    return np.array([smoothed.get(s, g) for s in valid["subject_id"]])


def own_lag_feature(train: pd.DataFrame, valid: pd.DataFrame, target: str, lag_days: int) -> np.ndarray:
    """For each valid row, return the value of `target` lag_days before (within
    same subject) using only train labels. NaN if not found."""
    out = np.full(len(valid), np.nan)
    by_subj = {s: g.set_index("lifelog_date")[target].to_dict() for s, g in train.groupby("subject_id")}
    valid_dates = pd.to_datetime(valid["lifelog_date"])
    for i, (s, d) in enumerate(zip(valid["subject_id"], valid_dates)):
        target_date = (d + pd.Timedelta(days=lag_days)).date().isoformat()
        v = by_subj.get(s, {}).get(target_date, np.nan)
        out[i] = v
    return out


def neighbor_mean(train: pd.DataFrame, valid: pd.DataFrame, target: str, window: int = 3) -> np.ndarray:
    """Mean of train labels within +/- `window` days of valid date, same subject."""
    out = np.full(len(valid), np.nan)
    train_by = {s: g.copy() for s, g in train.groupby("subject_id")}
    valid_dates = pd.to_datetime(valid["lifelog_date"])
    for s_dict in train_by.values():
        s_dict["_d"] = pd.to_datetime(s_dict["lifelog_date"])
    for i, (s, d) in enumerate(zip(valid["subject_id"], valid_dates)):
        g = train_by.get(s)
        if g is None or len(g) == 0:
            continue
        diff = (g["_d"] - d).dt.days.abs()
        mask = (diff <= window) & (diff > 0)
        if mask.any():
            out[i] = float(g.loc[mask, target].mean())
    return out


def build_features(train: pd.DataFrame, valid: pd.DataFrame, target: str, alpha: float) -> dict[str, dict[str, np.ndarray]]:
    """Compute the eight per-row feature columns once."""
    anchor_v = subject_prior(train, valid, target, alpha)
    anchor_t = subject_prior(train, train, target, alpha)
    feats = {
        "anchor_logit": (np.log(np.clip(anchor_t, 1e-3, 1 - 1e-3) / (1 - np.clip(anchor_t, 1e-3, 1 - 1e-3))),
                          np.log(np.clip(anchor_v, 1e-3, 1 - 1e-3) / (1 - np.clip(anchor_v, 1e-3, 1 - 1e-3)))),
        "own_lag_back": (own_lag_feature(train, train, target, -1),
                          own_lag_feature(train, valid, target, -1)),
        "own_lag_fwd": (own_lag_feature(train, train, target, +1),
                          own_lag_feature(train, valid, target, +1)),
        "neighbor_mean_3": (neighbor_mean(train, train, target, 3),
                             neighbor_mean(train, valid, target, 3)),
    }
    # cross-target lags: always include all 3 Q lags by name so MODELS can
    # reference them uniformly (the own-Q lag is identical to own_lag_back)
    for q in Q_TARGETS:
        feats[f"{q}_lag_back"] = (own_lag_feature(train, train, q, -1),
                                    own_lag_feature(train, valid, q, -1))
    return feats


def fit_predict(Xtr: np.ndarray, ytr: np.ndarray, Xva: np.ndarray) -> np.ndarray:
    """L2 logistic with NaN -> mean impute. Returns clipped probas."""
    means = np.nanmean(Xtr, axis=0)
    means[np.isnan(means)] = 0.5
    Xtr_i = np.where(np.isnan(Xtr), means, Xtr)
    Xva_i = np.where(np.isnan(Xva), means, Xva)
    if ytr.std() < 1e-6:
        return np.full(len(Xva_i), float(ytr.mean()))
    clf = LogisticRegression(C=1.0, max_iter=2000)
    clf.fit(Xtr_i, ytr)
    p = clf.predict_proba(Xva_i)[:, 1]
    return np.clip(p, CLIP[0], CLIP[1])


MODELS = {
    "M0_anchor": ["anchor_logit"],
    "M1_own_lag_back": ["anchor_logit", "own_lag_back"],
    "M2_neighbor_mean_3": ["anchor_logit", "neighbor_mean_3"],
    "M3_own_lag_back_fwd": ["anchor_logit", "own_lag_back", "own_lag_fwd"],
    "M4_all_q_lags_back": ["anchor_logit", "Q1_lag_back", "Q2_lag_back", "Q3_lag_back"],
    "M5_all_q_lags_back_fwd": ["anchor_logit", "own_lag_fwd", "Q1_lag_back", "Q2_lag_back", "Q3_lag_back"],
}


def split_by_fold(df: pd.DataFrame, fold: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    return df.iloc[tr_i].copy(), df.iloc[va_i].copy()


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
    alpha = 20.0

    rows = []
    for family, fpath in FOLD_FILES.items():
        cfg = json.loads(fpath.read_text())
        for fold in cfg["folds"]:
            train, valid = split_by_fold(df, fold)
            if len(valid) == 0:
                continue
            for target in Q_TARGETS:
                feats = build_features(train, valid, target, alpha)
                ytr = train[target].astype(int).to_numpy()
                yva = valid[target].astype(int).to_numpy()
                for model_name, cols in MODELS.items():
                    Xtr = np.column_stack([feats[c][0] for c in cols])
                    Xva = np.column_stack([feats[c][1] for c in cols])
                    p = fit_predict(Xtr, ytr, Xva)
                    ll = logloss(yva, p)
                    rows.append({
                        "family": family,
                        "fold": fold.get("name"),
                        "target": target,
                        "model": model_name,
                        "n_train": int(len(train)),
                        "n_valid": int(len(valid)),
                        "logloss": float(ll),
                    })

    res = pd.DataFrame(rows)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_CSV, index=False)
    print(f"wrote {RESULTS_CSV}")

    # report
    lines = []
    lines.append("# Q1 — Q-family grammar vs autocorr\n")
    lines.append(
        "For each Q target, we test whether *cross-target* lags (Q1→Q3, Q2→Q3 etc.) "
        "add information *beyond* own-target lag. If yes → grammar is real. "
        "If only own-lag works → it's just temporal autocorrelation.\n"
    )

    lines.append("\n## 1. Per-family × target × model (mean logloss across folds)\n")
    agg = res.groupby(["family", "target", "model"])["logloss"].mean().round(4).reset_index()
    for fam in ["chrono_tail", "hole_v1", "mirror_v1"]:
        sub = agg[agg["family"] == fam]
        if sub.empty:
            continue
        lines.append(f"\n### {fam}\n")
        pivot = sub.pivot(index="model", columns="target", values="logloss").round(4)
        pivot["Qavg"] = pivot.mean(axis=1).round(4)
        lines.append(df_to_md(pivot))

    lines.append("\n\n## 2. Key contrasts (averaged across folds)\n")
    pv = agg.pivot_table(index="model", columns=["family", "target"], values="logloss").round(4)
    # contrasts (positive = bad)
    contrasts = pd.DataFrame()
    for fam in ["chrono_tail", "hole_v1", "mirror_v1"]:
        tmp = res[res["family"] == fam].groupby(["target", "model"])["logloss"].mean().unstack("model")
        if tmp.empty:
            continue
        c = pd.DataFrame(index=tmp.index)
        c[f"{fam}: M1-M0"] = (tmp["M1_own_lag_back"] - tmp["M0_anchor"]).round(4)
        c[f"{fam}: M2-M1"] = (tmp["M2_neighbor_mean_3"] - tmp["M1_own_lag_back"]).round(4)
        c[f"{fam}: M3-M1"] = (tmp["M3_own_lag_back_fwd"] - tmp["M1_own_lag_back"]).round(4)
        c[f"{fam}: M4-M1"] = (tmp["M4_all_q_lags_back"] - tmp["M1_own_lag_back"]).round(4)
        c[f"{fam}: M5-M4"] = (tmp["M5_all_q_lags_back_fwd"] - tmp["M4_all_q_lags_back"]).round(4)
        contrasts = pd.concat([contrasts, c], axis=1)
    lines.append("Negative = better. M1=own lag, M2=neighbor mean, M3=+forward, M4=+cross-Q lags, M5=full.\n")
    lines.append(df_to_md(contrasts))

    lines.append(
        "\n\n## 3. Interpretation rules\n"
        "- **M2 ≈ M1 across families** → naive neighbor smoothing adds nothing over own-lag.\n"
        "- **M3 << M1 on hole_v1 only** → forward neighbor labels are huge on holes "
        "(structurally legitimate; 62% of test). Their absence on chrono_tail is expected.\n"
        "- **M4 < M1 on chrono_tail and mirror_v1 by > 0.005** → cross-Q grammar is real *causal* info.\n"
        "- **M4 ≈ M1** → 'grammar' is a misnomer, Q-lag effects are just autocorr.\n"
        "- **M5 - M4 ≈ M3 - M1** → forward info is additive to grammar (no interaction).\n"
    )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
