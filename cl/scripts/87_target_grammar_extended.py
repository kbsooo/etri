"""Axis 4 — Target / label grammar extended.

Four diagnostics:
  A. Pairwise mutual information MI(Y_i, Y_j) using empirical joint
  B. Conditional MI CMI(Y_i, Y_j | latent_state) where latent_state is the
     1-factor IRT score from advanced76 (or recomputed here)
  C. Prev/next label pattern × P(y=1 | pattern) for each target
  D. Transition vs non-transition day mean feature delta on a small feature
     vocabulary (sleep_block + mechanism + coverage selected cols)

Output:
  experiments/axis4_target_grammar_report.md
  experiments/axis4_target_grammar_tables.csv

Diagnostic only. No submission. No 3rd-decimal claims.
"""
from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
SLEEP_PARQ = ROOT / "features" / "sleep_block_features_v1.parquet"
MECH_PARQ = ROOT / "features" / "mechanism_sleep_load_features_v2.parquet"
COV_PARQ = ROOT / "features" / "observation_coverage_features.parquet"
REPORT_MD = ROOT / "experiments" / "axis4_target_grammar_report.md"
RESULTS_CSV = ROOT / "experiments" / "axis4_target_grammar_tables.csv"


def H(p: np.ndarray, eps=1e-12) -> np.ndarray:
    p = np.clip(p, eps, 1 - eps)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


def empirical_MI(x: np.ndarray, y: np.ndarray, eps=1e-12) -> float:
    """Mutual information for two binary variables."""
    n = len(x)
    if n == 0:
        return 0.0
    p00 = float(((x == 0) & (y == 0)).mean()) + eps
    p01 = float(((x == 0) & (y == 1)).mean()) + eps
    p10 = float(((x == 1) & (y == 0)).mean()) + eps
    p11 = float(((x == 1) & (y == 1)).mean()) + eps
    px = np.array([p00 + p01, p10 + p11])
    py = np.array([p00 + p10, p01 + p11])
    pxy = np.array([[p00, p01], [p10, p11]])
    mi = 0.0
    for i in range(2):
        for j in range(2):
            mi += pxy[i, j] * np.log(pxy[i, j] / (px[i] * py[j]))
    return float(mi)


def empirical_CMI(x, y, z_disc) -> float:
    """CMI(X;Y|Z) summed over discrete z."""
    total = 0.0
    for z_val in np.unique(z_disc):
        mask = z_disc == z_val
        if mask.sum() < 5:
            continue
        p_z = float(mask.mean())
        total += p_z * empirical_MI(x[mask], y[mask])
    return float(total)


def latent_state(train_labels: np.ndarray, k: int = 1, n_bins: int = 4) -> np.ndarray:
    centered = train_labels - train_labels.mean(axis=0, keepdims=True)
    z = TruncatedSVD(n_components=k, random_state=0).fit_transform(centered).flatten()
    binned = pd.qcut(z, q=n_bins, labels=False, duplicates="drop")
    return np.asarray(binned)


def df_to_md(df):
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
    df = pd.read_csv(TRAIN_CSV)
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"]).dt.date.astype(str)
    df = df.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    Y = df[LABELS].to_numpy(dtype=int)
    n = len(df)
    print(f"n={n} labels={LABELS}")

    # =============== A. Pairwise MI ===============
    mi_mat = np.zeros((7, 7))
    for i, j in product(range(7), range(7)):
        mi_mat[i, j] = empirical_MI(Y[:, i], Y[:, j])
    mi_df = pd.DataFrame(mi_mat, index=LABELS, columns=LABELS).round(4)
    print("MI matrix:\n", mi_df)

    # =============== B. CMI given latent state (4-bin) ===============
    z = latent_state(Y, k=1, n_bins=4)
    cmi_mat = np.zeros((7, 7))
    for i, j in product(range(7), range(7)):
        if i == j:
            continue
        cmi_mat[i, j] = empirical_CMI(Y[:, i], Y[:, j], z)
    cmi_df = pd.DataFrame(cmi_mat, index=LABELS, columns=LABELS).round(4)

    # Reduction = MI - CMI: how much of i-j association is explained by latent state
    reduction = (mi_df - cmi_df).round(4)

    # =============== C. Prev/next pattern × P(y) ===============
    df["_d"] = pd.to_datetime(df["lifelog_date"])
    df = df.sort_values(["subject_id", "_d"]).reset_index(drop=True)
    pattern_rows = []
    for target in LABELS:
        prev_vals, next_vals = [], []
        for s, g in df.groupby("subject_id"):
            g = g.sort_values("_d").reset_index(drop=True)
            t_dates = pd.to_datetime(g["lifelog_date"])
            y = g[target].astype(int).values
            for i in range(len(g)):
                d = t_dates.iloc[i]
                # prev day
                prev_mask = t_dates == d - pd.Timedelta(days=1)
                next_mask = t_dates == d + pd.Timedelta(days=1)
                prev_vals.append(int(y[prev_mask.values][0]) if prev_mask.any() else -1)
                next_vals.append(int(y[next_mask.values][0]) if next_mask.any() else -1)
        prev_vals = np.array(prev_vals)
        next_vals = np.array(next_vals)
        y_all = df[target].astype(int).values
        for pp, nn in product([-1, 0, 1], [-1, 0, 1]):
            mask = (prev_vals == pp) & (next_vals == nn)
            if mask.sum() < 5:
                continue
            pattern_rows.append({
                "target": target,
                "prev": pp,
                "next": nn,
                "n": int(mask.sum()),
                "P_y_eq_1": float(y_all[mask].mean()),
            })
    pat_df = pd.DataFrame(pattern_rows)

    # =============== D. Transition vs non-transition day feature delta ===============
    # Transition day = own-target value flips vs previous-day same-subject value.
    sleep = pd.read_parquet(SLEEP_PARQ)
    sleep["lifelog_date"] = pd.to_datetime(sleep["lifelog_date"]).dt.date.astype(str)
    mech = pd.read_parquet(MECH_PARQ)
    mech["lifelog_date"] = pd.to_datetime(mech["lifelog_date"]).dt.date.astype(str)
    cov = pd.read_parquet(COV_PARQ)
    if "date" in cov.columns:
        cov = cov.rename(columns={"date": "lifelog_date"})
    cov["lifelog_date"] = pd.to_datetime(cov["lifelog_date"]).dt.date.astype(str)

    join_cols = ["subject_id", "lifelog_date"]
    base = df[join_cols + LABELS].copy()
    feats = base.merge(sleep, on=join_cols, how="left").merge(mech, on=join_cols, how="left").merge(cov, on=join_cols, how="left")
    feat_cols = [c for c in feats.columns if c not in join_cols + LABELS + ["_d", "split"] and pd.api.types.is_numeric_dtype(feats[c])]

    # for each target, compute mean(feature | transition) vs mean(feature | non-transition)
    transition_summary = []
    for target in LABELS:
        feats_t = feats.sort_values(join_cols).copy()
        feats_t["prev_y"] = feats_t.groupby("subject_id")[target].shift(1)
        feats_t["is_transition"] = (feats_t[target] != feats_t["prev_y"]) & feats_t["prev_y"].notna()
        feats_t["is_nontransition"] = (feats_t[target] == feats_t["prev_y"]) & feats_t["prev_y"].notna()
        if feats_t["is_transition"].sum() < 5:
            continue
        mu_t = feats_t.loc[feats_t["is_transition"], feat_cols].mean()
        mu_n = feats_t.loc[feats_t["is_nontransition"], feat_cols].mean()
        sd_n = feats_t.loc[feats_t["is_nontransition"], feat_cols].std().replace(0, np.nan)
        delta_z = ((mu_t - mu_n) / sd_n).abs().sort_values(ascending=False).head(5)
        for fname, val in delta_z.items():
            transition_summary.append({"target": target, "feature": fname, "abs_z_delta": float(val)})
    trans_df = pd.DataFrame(transition_summary)

    # =============== Q/S axis decomposition ===============
    q_block = Y[:, [0, 1, 2]]
    s_block = Y[:, [3, 4, 5, 6]]
    q_mi_internal = float(np.mean([empirical_MI(q_block[:, i], q_block[:, j]) for i in range(3) for j in range(i + 1, 3)]))
    s_mi_internal = float(np.mean([empirical_MI(s_block[:, i], s_block[:, j]) for i in range(4) for j in range(i + 1, 4)]))
    qs_mi_cross = float(np.mean([empirical_MI(q_block[:, i], s_block[:, j]) for i in range(3) for j in range(4)]))

    # =============== save ===============
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_CSV.open("w") as f:
        f.write("# section A: pairwise MI\n")
        mi_df.to_csv(f, mode="a")
        f.write("\n# section B: CMI given latent state (4-bin)\n")
        cmi_df.to_csv(f, mode="a")
        f.write("\n# section B.2: MI - CMI reduction by latent state\n")
        reduction.to_csv(f, mode="a")
        f.write("\n# section C: prev/next pattern × P(y)\n")
        pat_df.to_csv(f, mode="a", index=False)
        f.write("\n# section D: top-5 feature abs z-delta on transition day\n")
        trans_df.to_csv(f, mode="a", index=False)
    print(f"wrote {RESULTS_CSV}")

    lines = []
    lines.append("# Axis 4 — Target / label grammar extended\n")
    lines.append("\n## A. Pairwise mutual information MI(Y_i, Y_j) (nats)\n")
    lines.append(df_to_md(mi_df))

    lines.append("\n\n## B. Conditional MI given 4-bin latent state\n")
    lines.append(df_to_md(cmi_df))

    lines.append("\n\n## B.2. MI − CMI: how much pair association is *explained* by latent state\n")
    lines.append("Large values = latent state captures the i-j relationship; pair is conditionally near-independent given state.\n\n")
    lines.append(df_to_md(reduction))

    lines.append("\n\n## C. Prev/next pattern × P(y=1) per target\n")
    lines.append("prev/next: -1 = missing, 0 = label 0, 1 = label 1. Sample size in `n`.\n\n")
    pat_pivot = pat_df.pivot_table(index=["target", "prev"], columns="next", values="P_y_eq_1").round(3)
    lines.append(pat_pivot.to_string())

    lines.append("\n\n## D. Top-5 features with largest |z-delta| on transition days, per target\n")
    if not trans_df.empty:
        for t in LABELS:
            sub = trans_df[trans_df["target"] == t].sort_values("abs_z_delta", ascending=False).head(5)
            if sub.empty:
                continue
            lines.append(f"\n### {t}\n")
            lines.append(df_to_md(sub.set_index("feature")[["abs_z_delta"]].round(3)))

    lines.append(
        f"\n\n## E. Q/S axis decomposition\n"
        f"- mean MI within Q-family (Q1↔Q2↔Q3): **{q_mi_internal:.4f}**\n"
        f"- mean MI within S-family (S1↔S2↔S3↔S4): **{s_mi_internal:.4f}**\n"
        f"- mean MI Q×S cross: **{qs_mi_cross:.4f}**\n"
        f"\nIf within-family >> cross-family → Q and S live on separate latent axes; a single latent factor cannot model both simultaneously.\n"
    )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
