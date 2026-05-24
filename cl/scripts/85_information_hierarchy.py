"""Axis 2 — Information hierarchy.

For each target, decompose mean logloss reduction by progressively adding info
sources to an L2 logistic. The point is NOT picking the best model; it is to
classify *what kind of info* each target actually responds to.

Sources (added cumulatively):
  S0  global_prior
  S1  + subject dummies
  S2  + calendar (day_of_week sin/cos, days_since_first, is_weekend)
  S3  + own neighbor labels (own_lag_back, own_lag_fwd)
  S4  + other-target neighbor labels (6 other targets × {back, fwd})
  S5  + 1-factor latent label state (fit on train labels only)
  S6  + engineered sensor features (top-30 F-test from semantic + sleep_block + mechanism)
  S7  + coverage features (top-20 F-test from observation_coverage_features)
  S8  + subject-debiased context tokens (the 5 Q2-surviving BSSIDs/apps)
  S9  ALL (just S8 again, here for symmetry)

Eval: mirror_v1 (3 seeds). Report:
  - per target, per source set: mean ± std logloss
  - incremental Δlogloss when each source is added

Diagnostic only. No submission. No 3rd-decimal interpretation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, logloss  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
MIRROR = ROOT / "outputs" / "validation" / "folds_subject_mirror_v1.json"
REPORT_MD = ROOT / "experiments" / "axis2_information_hierarchy_report.md"
RESULTS_CSV = ROOT / "experiments" / "axis2_information_hierarchy_results.csv"

# Q2 survivors from script 84
SURVIVING_TOKENS = [
    "usage_app_name:카카오 T",
    "wifi_bssid:b4:a9:4f:3f:32:5b",
    "wifi_bssid:60:29:d5:4a:47:d3",
    "usage_app_name:Google Play 서비스",
    "usage_app_name:LG ThinQ",
]


def load_all() -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    tr = pd.read_csv(TRAIN_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    feats = {}
    for fname, key in [
        ("semantic_features_v1.parquet", "semantic"),
        ("sleep_block_features_v1.parquet", "sleep"),
        ("mechanism_sleep_load_features_v2.parquet", "mech"),
        ("observation_coverage_features.parquet", "cov"),
        ("observation_identity_token_features.parquet", "ident"),
    ]:
        p = ROOT / "features" / fname
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        if "date" in d.columns and "lifelog_date" not in d.columns:
            d = d.rename(columns={"date": "lifelog_date"})
        d["lifelog_date"] = pd.to_datetime(d["lifelog_date"]).dt.date.astype(str)
        feats[key] = d
    return tr, feats


def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    d = pd.to_datetime(df["lifelog_date"])
    out = df.copy()
    out["cal_dow_sin"] = np.sin(2 * np.pi * d.dt.dayofweek / 7)
    out["cal_dow_cos"] = np.cos(2 * np.pi * d.dt.dayofweek / 7)
    out["cal_is_weekend"] = (d.dt.dayofweek >= 5).astype(int)
    base = d.groupby(df["subject_id"]).transform("min")
    out["cal_days_since_first"] = (d - base).dt.days
    return out


def own_lag_array(train: pd.DataFrame, df: pd.DataFrame, target: str, lag_days: int) -> np.ndarray:
    out = np.full(len(df), np.nan)
    by = {s: g.set_index("lifelog_date")[target].to_dict() for s, g in train.groupby("subject_id")}
    dates = pd.to_datetime(df["lifelog_date"])
    for i, (s, d) in enumerate(zip(df["subject_id"], dates)):
        tgt = (d + pd.Timedelta(days=lag_days)).date().isoformat()
        out[i] = by.get(s, {}).get(tgt, np.nan)
    return out


def latent_factor(train_labels: np.ndarray, valid_labels_proxy: np.ndarray, k: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """1-factor SVD on label residuals after subject removal. Returns train and
    valid latent scores. Valid scores are computed by projecting valid label
    estimates (= subject mean labels) onto the train basis — this only encodes
    subject identity through the latent space and is conservative."""
    centered = train_labels - train_labels.mean(axis=0, keepdims=True)
    svd = TruncatedSVD(n_components=k, random_state=0)
    z_tr = svd.fit_transform(centered)
    centered_v = valid_labels_proxy - train_labels.mean(axis=0, keepdims=True)
    z_va = svd.transform(centered_v)
    return z_tr, z_va


def select_topk_cols(X: pd.DataFrame, y: np.ndarray, k: int) -> list[str]:
    if X.empty or X.shape[1] == 0:
        return []
    Xa = X.to_numpy(dtype=float, na_value=0.0)
    if y.std() < 1e-6:
        return list(X.columns[:k])
    sel = SelectKBest(f_classif, k=min(k, X.shape[1]))
    sel.fit(Xa, y)
    chosen = X.columns[sel.get_support()].tolist()
    return chosen


def fit_score(Xtr: np.ndarray, ytr: np.ndarray, Xva: np.ndarray, yva: np.ndarray) -> float:
    if ytr.std() < 1e-6 or Xtr.shape[1] == 0:
        p = np.full(len(yva), float(ytr.mean()))
        return logloss(yva, np.clip(p, 0.03, 0.97))
    means = np.nanmean(Xtr, axis=0)
    means[np.isnan(means)] = 0.0
    Xtr_i = np.where(np.isnan(Xtr), means, Xtr)
    Xva_i = np.where(np.isnan(Xva), means, Xva)
    sc = StandardScaler().fit(Xtr_i)
    Xtr_s, Xva_s = sc.transform(Xtr_i), sc.transform(Xva_i)
    clf = LogisticRegression(C=0.5, max_iter=2000)
    clf.fit(Xtr_s, ytr)
    p = np.clip(clf.predict_proba(Xva_s)[:, 1], 0.03, 0.97)
    return float(logloss(yva, p))


def build_source_features(train: pd.DataFrame, valid: pd.DataFrame, target: str, feats: dict[str, pd.DataFrame]) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """Build per-source feature blocks. Each value is (X_train, X_valid)."""
    out: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}

    # S0: global -> empty matrix; we'll use intercept-only logreg = global mean
    out["S0_global"] = (pd.DataFrame({"const": np.ones(len(train))}), pd.DataFrame({"const": np.ones(len(valid))}))

    # S1: + subject dummies
    sd = pd.get_dummies(pd.concat([train["subject_id"], valid["subject_id"]]), prefix="subj", drop_first=True).astype(float)
    sd_tr = sd.iloc[:len(train)].reset_index(drop=True)
    sd_va = sd.iloc[len(train):].reset_index(drop=True)
    out["S1_subject"] = (sd_tr, sd_va)

    # S2: + calendar
    cal_tr_full = add_calendar(train)
    cal_va_full = add_calendar(valid)
    cal_cols = ["cal_dow_sin", "cal_dow_cos", "cal_is_weekend", "cal_days_since_first"]
    out["S2_calendar"] = (cal_tr_full[cal_cols].reset_index(drop=True), cal_va_full[cal_cols].reset_index(drop=True))

    # S3: + own neighbor labels
    onb = pd.DataFrame({
        f"{target}_lag_back": own_lag_array(train, train, target, -1),
        f"{target}_lag_fwd": own_lag_array(train, train, target, +1),
    })
    onb_va = pd.DataFrame({
        f"{target}_lag_back": own_lag_array(train, valid, target, -1),
        f"{target}_lag_fwd": own_lag_array(train, valid, target, +1),
    })
    out["S3_own_neighbor"] = (onb, onb_va)

    # S4: + other-target neighbor labels (all 6 others × back+fwd)
    cols = {}
    cols_va = {}
    for t in LABELS:
        if t == target:
            continue
        cols[f"{t}_lag_back"] = own_lag_array(train, train, t, -1)
        cols[f"{t}_lag_fwd"] = own_lag_array(train, train, t, +1)
        cols_va[f"{t}_lag_back"] = own_lag_array(train, valid, t, -1)
        cols_va[f"{t}_lag_fwd"] = own_lag_array(train, valid, t, +1)
    out["S4_other_neighbor"] = (pd.DataFrame(cols), pd.DataFrame(cols_va))

    # S5: + latent state. Train labels matrix -> SVD; valid uses subject mean as label proxy.
    tr_lab = train[LABELS].to_numpy(dtype=float)
    subj_mean_map = train.groupby("subject_id")[LABELS].mean()
    subj_mean_va = subj_mean_map.reindex(valid["subject_id"].values).to_numpy(dtype=float)
    z_tr, z_va = latent_factor(tr_lab, subj_mean_va, k=1)
    out["S5_latent"] = (pd.DataFrame(z_tr, columns=["z1"]), pd.DataFrame(z_va, columns=["z1"]))

    # S6: + engineered sensor features (top-30 F-test from semantic + sleep + mech)
    eng_parts_tr, eng_parts_va = [], []
    for key in ("semantic", "sleep", "mech"):
        if key not in feats:
            continue
        d = feats[key]
        join_cols = ["subject_id", "lifelog_date"]
        num_cols = [c for c in d.columns if c not in join_cols and pd.api.types.is_numeric_dtype(d[c])]
        d_tr = train[join_cols].merge(d[join_cols + num_cols], on=join_cols, how="left").drop(columns=join_cols)
        d_va = valid[join_cols].merge(d[join_cols + num_cols], on=join_cols, how="left").drop(columns=join_cols)
        eng_parts_tr.append(d_tr)
        eng_parts_va.append(d_va)
    if eng_parts_tr:
        eng_tr = pd.concat(eng_parts_tr, axis=1).loc[:, ~pd.concat(eng_parts_tr, axis=1).columns.duplicated()]
        eng_va = pd.concat(eng_parts_va, axis=1).loc[:, ~pd.concat(eng_parts_va, axis=1).columns.duplicated()]
        y_for_sel = train[target].astype(int).values
        chosen = select_topk_cols(eng_tr.fillna(0.0), y_for_sel, k=30)
        out["S6_engineered"] = (eng_tr[chosen].reset_index(drop=True), eng_va[chosen].reset_index(drop=True))
    else:
        out["S6_engineered"] = (pd.DataFrame(), pd.DataFrame())

    # S7: + coverage (top-20 F-test from coverage parquet)
    cov = feats.get("cov")
    if cov is not None:
        join_cols = ["subject_id", "lifelog_date"]
        num_cols = [c for c in cov.columns if c not in join_cols + ["split"] and pd.api.types.is_numeric_dtype(cov[c])]
        cov_tr = train[join_cols].merge(cov[join_cols + num_cols], on=join_cols, how="left").drop(columns=join_cols)
        cov_va = valid[join_cols].merge(cov[join_cols + num_cols], on=join_cols, how="left").drop(columns=join_cols)
        chosen = select_topk_cols(cov_tr.fillna(0.0), train[target].astype(int).values, k=20)
        out["S7_coverage"] = (cov_tr[chosen].reset_index(drop=True), cov_va[chosen].reset_index(drop=True))
    else:
        out["S7_coverage"] = (pd.DataFrame(), pd.DataFrame())

    # S8: + subject-debiased context tokens (Q2 survivors only)
    ident = feats.get("ident")
    if ident is not None:
        ident_cols = set(ident.columns)
        present = [t for t in SURVIVING_TOKENS if t in ident_cols]
        if present:
            join_cols = ["subject_id", "lifelog_date"]
            tok_tr = train[join_cols].merge(ident[join_cols + present], on=join_cols, how="left").drop(columns=join_cols)
            tok_va = valid[join_cols].merge(ident[join_cols + present], on=join_cols, how="left").drop(columns=join_cols)
            out["S8_context_tokens"] = (tok_tr.reset_index(drop=True), tok_va.reset_index(drop=True))
        else:
            out["S8_context_tokens"] = (pd.DataFrame(), pd.DataFrame())
    else:
        out["S8_context_tokens"] = (pd.DataFrame(), pd.DataFrame())

    return out


HIERARCHY = [
    "S0_global",
    "S1_subject",
    "S2_calendar",
    "S3_own_neighbor",
    "S4_other_neighbor",
    "S5_latent",
    "S6_engineered",
    "S7_coverage",
    "S8_context_tokens",
]


def cumulative_features(blocks: dict[str, tuple[pd.DataFrame, pd.DataFrame]], up_to: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts_tr, parts_va = [], []
    for k in HIERARCHY[: up_to + 1]:
        tr, va = blocks[k]
        if tr.shape[1] > 0:
            parts_tr.append(tr)
            parts_va.append(va)
    if not parts_tr:
        return pd.DataFrame({"const": np.ones(1)}), pd.DataFrame({"const": np.ones(1)})
    return pd.concat(parts_tr, axis=1), pd.concat(parts_va, axis=1)


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


def marginal_features(blocks: dict[str, tuple[pd.DataFrame, pd.DataFrame]], single_key: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """anchor (S0+S1) + that one source only."""
    anchor_keys = ["S0_global", "S1_subject"]
    keys = list(dict.fromkeys(anchor_keys + [single_key]))
    parts_tr, parts_va = [], []
    for k in keys:
        tr, va = blocks[k]
        if tr.shape[1] > 0:
            parts_tr.append(tr)
            parts_va.append(va)
    if not parts_tr:
        return pd.DataFrame({"const": np.ones(1)}), pd.DataFrame({"const": np.ones(1)})
    return pd.concat(parts_tr, axis=1), pd.concat(parts_va, axis=1)


def main():
    df, feats = load_all()
    cfg = json.loads(MIRROR.read_text())
    rows = []
    marginal_rows = []
    for fold in cfg["folds"]:
        train, valid = split_by_fold(df, fold)
        if len(valid) == 0:
            continue
        for target in LABELS:
            blocks = build_source_features(train, valid, target, feats)
            ytr = train[target].astype(int).to_numpy()
            yva = valid[target].astype(int).to_numpy()
            # cumulative
            for level, name in enumerate(HIERARCHY):
                Xtr, Xva = cumulative_features(blocks, level)
                ll = fit_score(Xtr.to_numpy(dtype=float, na_value=0.0), ytr, Xva.to_numpy(dtype=float, na_value=0.0), yva)
                rows.append({
                    "fold": fold.get("name"),
                    "target": target,
                    "level": level,
                    "source_set": name,
                    "n_features": int(Xtr.shape[1]),
                    "logloss": ll,
                })
            # marginal anchored: S0+S1 + each Sk alone
            for name in HIERARCHY:
                if name in ("S0_global", "S1_subject"):
                    continue
                Xtr, Xva = marginal_features(blocks, name)
                ll = fit_score(Xtr.to_numpy(dtype=float, na_value=0.0), ytr, Xva.to_numpy(dtype=float, na_value=0.0), yva)
                marginal_rows.append({
                    "fold": fold.get("name"),
                    "target": target,
                    "source_set": name,
                    "n_features": int(Xtr.shape[1]),
                    "logloss": ll,
                })
            print(f"{fold.get('name'):16s} {target}  done")

    res = pd.DataFrame(rows)
    res_marg = pd.DataFrame(marginal_rows)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_CSV, index=False)
    res_marg.to_csv(RESULTS_CSV.with_suffix(".marginal.csv"), index=False)
    print(f"wrote {RESULTS_CSV}")

    # aggregate
    agg = res.groupby(["target", "source_set", "level"]).agg(mean_ll=("logloss", "mean"), std_ll=("logloss", "std")).round(4).reset_index()

    lines = []
    lines.append("# Axis 2 — Information hierarchy\n")
    lines.append(
        "Mirror_v1 fold family (3 seeds). Cumulative source additions left→right.\n"
        "Negative Δ = adding that source helped on that target.\n"
    )

    pivot_mean = agg.pivot(index="source_set", columns="target", values="mean_ll").reindex(HIERARCHY).round(4)
    pivot_mean["Tavg"] = pivot_mean.mean(axis=1).round(4)
    lines.append("\n## 1. Cumulative mean logloss per target (mirror_v1, 3 seeds)\n")
    lines.append(df_to_md(pivot_mean))

    delta = pivot_mean.diff().round(4)
    delta.iloc[0] = np.nan
    lines.append("\n\n## 2. Incremental Δlogloss when adding each source (cumulative)\n")
    lines.append(
        "WARNING: with 250 train rows, cumulative model overfits as more features are added. "
        "Use Section 3 (marginal) for the actual information contribution.\n"
    )
    lines.append(df_to_md(delta))

    # marginal contribution table
    anchor_mean = pivot_mean.loc["S1_subject"]  # baseline is S0+S1 cumulative
    marg_agg = res_marg.groupby(["target", "source_set"])["logloss"].mean().unstack("source_set").round(4)
    marg_delta = marg_agg.sub(anchor_mean, axis=0).round(4)
    marg_delta = marg_delta.T  # rows = sources, cols = targets
    marg_delta = marg_delta.loc[[k for k in HIERARCHY if k in marg_delta.index]]
    marg_delta["Tavg"] = marg_delta.mean(axis=1).round(4)
    lines.append("\n\n## 3. Marginal Δlogloss vs (S0+S1) anchor — each source added ALONE\n")
    lines.append(
        "This is the clean information-contribution table. Each row = (anchor + that source). "
        "Negative = that source has real signal on top of (global + subject). Positive = adding "
        "that source on top of (global + subject) hurts (likely overfit or signal absorbed by S1).\n"
    )
    lines.append(df_to_md(marg_delta))

    # which source dominates per target
    dominant = {}
    for t in LABELS:
        col = delta[t].dropna()
        if col.empty:
            dominant[t] = "none"
            continue
        # find the single biggest negative delta (most-helpful source)
        best = col.idxmin()
        best_val = col.min()
        dominant[t] = f"{best} ({best_val:+.4f})"

    lines.append("\n\n## 3. Dominant source per target (largest single Δ)\n")
    dom_df = pd.Series(dominant, name="dominant_source").to_frame()
    lines.append(df_to_md(dom_df))

    # final std on full-stack
    final_std = agg[agg["source_set"] == HIERARCHY[-1]][["target", "std_ll"]].set_index("target")
    lines.append("\n\n## 4. Fold-to-fold std on the full-stack model (CI proxy)\n")
    lines.append("Any Δ inside this std is not a real improvement.\n\n")
    lines.append(df_to_md(final_std.round(4)))

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
