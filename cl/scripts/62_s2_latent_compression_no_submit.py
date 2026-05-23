#!/usr/bin/env python3
"""No-submit S2 latent-compression experiments.

Purpose: the previous hand-written routine axes were too lossy.  This script
keeps the richer existing S2 feature families, compresses them fold-locally with
small unsupervised latent methods, and probes S2 with regularized logistic
heads across multiple validation views.

No submission files are written.
"""
from __future__ import annotations

import importlib.util
import json
import warnings
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA, NMF, TruncatedSVD
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
FEAT = ROOT / "features"
EXP = ROOT / "experiments"

spec = importlib.util.spec_from_file_location("ts", ROOT / "scripts/50_eval_temporal_state_smoothing.py")
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)

TARGET = "S2"
ID = ["subject_id", "lifelog_date"]


class KMeansDistances(BaseEstimator, TransformerMixin):
    def __init__(self, n_clusters=8, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def fit(self, X, y=None):
        n_clusters = min(self.n_clusters, max(2, len(X) // 8))
        self.model_ = MiniBatchKMeans(
            n_clusters=n_clusters,
            random_state=self.random_state,
            batch_size=128,
            n_init=10,
            max_iter=200,
        )
        self.model_.fit(X)
        return self

    def transform(self, X):
        d = self.model_.transform(X)
        # Smaller distance to state prototype should be larger/more readable.
        return -d


def load_df() -> pd.DataFrame:
    df = ts.load_all()
    # Include previous human/S2 axes only as optional side track if available;
    # baseline comparisons remain the existing S2 base feature family.
    con = duckdb.connect()
    for p in [FEAT / "human_hypothesis_q2s2_features_v1.parquet", FEAT / "s2_routine_axes_v1.parquet"]:
        if p.exists():
            extra = con.execute(f"select * from read_parquet('{p}')").df()
            for k in ID:
                if k in extra.columns:
                    extra[k] = extra[k].astype(str)
            df[ID] = df[ID].astype(str)
            dup = [c for c in extra.columns if c in df.columns and c not in ID]
            if dup:
                extra = extra.rename(columns={c: f"{c}__{p.stem}" for c in dup})
            df = df.merge(extra, on=ID, how="left")
    df["sleep_date"] = pd.to_datetime(df["sleep_date"])
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
    return df


def valid_cols(df: pd.DataFrame, mask: np.ndarray, cols: list[str]) -> list[str]:
    out = []
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df.loc[mask, c], errors="coerce")
        if s.notna().sum() > 20 and s.nunique(dropna=True) > 1:
            out.append(c)
    return out


def make_random_gap_mask(train: pd.DataFrame, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 620)
    mask = np.zeros(len(train), bool)
    for _, g in train.groupby("subject_id"):
        idx = g.sort_values("sleep_date").index.to_numpy()
        if len(idx) <= 4:
            continue
        n = max(3, int(round(len(idx) * 0.28)))
        ranks = np.linspace(0, 1, len(idx))
        prob = 0.18 + 0.65 * ranks + np.exp(-0.5 * ((ranks - 0.55) / 0.22) ** 2)
        prob = prob / prob.sum()
        chosen = rng.choice(idx, size=min(n, len(idx) - 2), replace=False, p=prob)
        mask[train.index.get_indexer(chosen)] = True
    return mask


def get_masks(train: pd.DataFrame, sample: pd.DataFrame):
    masks = []
    # Official-ish chrono folds if available.
    fpath = ROOT / "outputs/validation/folds_chrono.json"
    if fpath.exists():
        folds = json.loads(fpath.read_text())["folds"]
        for fold in folds:
            valid = {(x["subject_id"], str(x["lifelog_date"])[:10]) for x in fold["valid_keys"]}
            val_mask = train.apply(
                lambda r: (r.subject_id, pd.Timestamp(r.lifelog_date).strftime("%Y-%m-%d")) in valid,
                axis=1,
            ).to_numpy()
            if val_mask.sum() > 0:
                masks.append(("chrono", fold["fold_id"], val_mask))
    for seed in range(6):
        masks.append(("testpattern", seed, ts.make_testpattern_mask(train, sample, seed)))
    for seed in range(6):
        masks.append(("random_gap", seed, make_random_gap_mask(train, seed)))
    for frac in [0.20, 0.30, 0.40, 0.50]:
        masks.append((f"tail{frac:.2f}", int(frac * 100), ts.make_tail_mask(train, frac=frac)))
    return masks


def feature_sets(all_cols: list[str]) -> dict[str, list[str]]:
    noflat = ts.base_subset(all_cols, "no_flat_hourly")
    dayflat = ts.base_subset(all_cols, "day_flat")
    axes = [c for c in all_cols if c.startswith("axis_")]
    human_s2 = [c for c in all_cols if c.startswith("human_s2") or c.startswith("human_hyp_s2")]
    return {
        "existing_no_flat": noflat,
        "day_flat_hourly": dayflat,
        "combo_existing_dayflat": list(dict.fromkeys(noflat + dayflat)),
        "combo_existing_dayflat_axes": list(dict.fromkeys(noflat + dayflat + axes + human_s2)),
    }


def make_latent_pipe(kind: str, n: int, C: float) -> Pipeline:
    if kind == "pca":
        steps = [
            ("imp", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("latent", PCA(n_components=n, random_state=42, svd_solver="randomized")),
            ("post", RobustScaler()),
            ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
        ]
    elif kind == "svd":
        steps = [
            ("imp", SimpleImputer(strategy="median")),
            ("scale", StandardScaler(with_mean=False)),
            ("latent", TruncatedSVD(n_components=n, random_state=42)),
            ("post", RobustScaler()),
            ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
        ]
    elif kind == "nmf":
        steps = [
            ("imp", SimpleImputer(strategy="median")),
            ("scale", MinMaxScaler()),
            ("latent", NMF(n_components=n, random_state=42, init="nndsvda", max_iter=600, alpha_W=0.01, alpha_H=0.01, l1_ratio=0.1)),
            ("post", RobustScaler()),
            ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
        ]
    elif kind == "kmeans":
        steps = [
            ("imp", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("latent", KMeansDistances(n_clusters=n, random_state=42)),
            ("post", RobustScaler()),
            ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
        ]
    else:
        raise ValueError(kind)
    return Pipeline(steps)


def make_raw_pipe(k: int, C: float, ncols: int) -> Pipeline:
    return Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sel", SelectKBest(f_classif, k=min(k, ncols))),
        ("scale", RobustScaler()),
        ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
    ])


def auc_safe(y, p):
    return roc_auc_score(y, p) if len(set(y)) == 2 else np.nan


def fit_predict_loss(model, Xtr, ytr, Xva, yva):
    model.fit(Xtr, ytr)
    p = np.clip(model.predict_proba(Xva)[:, 1], 0.02, 0.98)
    return log_loss(yva, p, labels=[0, 1]), auc_safe(yva, p)


def run_eval():
    EXP.mkdir(exist_ok=True)
    FEAT.mkdir(exist_ok=True)
    df = load_df()
    train = df[df.is_train.eq(1)].copy().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    sample = df[df.is_train.eq(0)].copy().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    all_cols = [c for c in train.columns if c not in ts.DROP]
    sets = feature_sets(all_cols)
    masks = get_masks(train, sample)

    rows = []
    selected = []
    y_all = train[TARGET].astype(int).to_numpy()
    for split, seed, val_mask in masks:
        known_mask = ~val_mask
        yva = train.loc[val_mask, TARGET].astype(int).to_numpy()
        pbase = ts.base_predict_for(train, known_mask, val_mask, TARGET, None)
        base_loss = log_loss(yva, pbase, labels=[0, 1])
        rows.append({
            "split": split, "seed": seed, "target": TARGET, "source": "existing_base_cfg",
            "model": "basecfg", "n": np.nan, "C": np.nan, "k": np.nan,
            "logloss": base_loss, "auc": auc_safe(yva, pbase), "ncols": np.nan,
        })

        for source, cols0 in sets.items():
            cols = valid_cols(train, known_mask, cols0)
            if not cols:
                continue
            Xtr = train.loc[known_mask, cols]
            ytr = train.loc[known_mask, TARGET].astype(int).to_numpy()
            Xva = train.loc[val_mask, cols]

            # Raw SelectK sanity: if latent loses, this tells us compression is the issue.
            for k in [8, 12, 20, 32, 60]:
                if k > len(cols) * 2:
                    continue
                for C in [0.001, 0.003, 0.01, 0.03]:
                    model = make_raw_pipe(k, C, len(cols))
                    loss, auc = fit_predict_loss(model, Xtr, ytr, Xva, yva)
                    rows.append({"split": split, "seed": seed, "target": TARGET, "source": source, "model": "raw_selectk", "n": np.nan, "C": C, "k": k, "logloss": loss, "auc": auc, "ncols": len(cols)})
                    if split == "testpattern" and seed == 0 and source in ["existing_no_flat", "combo_existing_dayflat"] and k in [20, 32] and C in [0.001, 0.003]:
                        try:
                            names = np.array(cols)[model.named_steps["sel"].get_support()]
                            for nm in names:
                                selected.append({"source": source, "model": "raw_selectk", "k": k, "C": C, "feature": nm})
                        except Exception:
                            pass

            max_n = min(64, max(2, len(cols) - 1), max(2, known_mask.sum() - 2))
            for kind in ["pca", "svd", "nmf", "kmeans"]:
                for n in [2, 4, 8, 16, 32]:
                    if n > max_n:
                        continue
                    for C in [0.001, 0.003, 0.01, 0.03]:
                        try:
                            model = make_latent_pipe(kind, n, C)
                            loss, auc = fit_predict_loss(model, Xtr, ytr, Xva, yva)
                        except Exception as e:
                            rows.append({"split": split, "seed": seed, "target": TARGET, "source": source, "model": kind, "n": n, "C": C, "k": np.nan, "logloss": np.nan, "auc": np.nan, "ncols": len(cols), "error": str(e)[:160]})
                            continue
                        rows.append({"split": split, "seed": seed, "target": TARGET, "source": source, "model": kind, "n": n, "C": C, "k": np.nan, "logloss": loss, "auc": auc, "ncols": len(cols)})

    res = pd.DataFrame(rows)
    res.to_csv(EXP / "s2_latent_compression_eval_results.csv", index=False)
    if selected:
        pd.DataFrame(selected).drop_duplicates().to_csv(EXP / "s2_latent_compression_selected_raw_features.csv", index=False)
    summarize(res)
    build_full_unsup_features(df, sets)


def summarize(res: pd.DataFrame):
    clean = res.dropna(subset=["logloss"]).copy()
    base = clean[clean.source.eq("existing_base_cfg")][["split", "seed", "logloss"]].rename(columns={"logloss": "base_loss"})
    clean = clean.merge(base, on=["split", "seed"], how="left")
    clean["delta_vs_base"] = clean.logloss - clean.base_loss
    clean["group"] = clean.split.map(lambda x: "tail" if str(x).startswith("tail") else x)
    clean.to_csv(EXP / "s2_latent_compression_eval_summary_long.csv", index=False)

    summ = clean.groupby(["group", "source", "model", "n", "k", "C"], dropna=False).agg(
        logloss=("logloss", "mean"),
        delta=("delta_vs_base", "mean"),
        auc=("auc", "mean"),
        runs=("logloss", "size"),
        ncols=("ncols", "mean"),
    ).reset_index()
    summ.to_csv(EXP / "s2_latent_compression_eval_summary.csv", index=False)

    # Coarse robustness: average by group, then mean/worst across groups.
    by_group = summ.groupby(["source", "model", "n", "k", "C", "group"], dropna=False).agg(delta=("delta", "mean"), logloss=("logloss", "mean"), auc=("auc", "mean")).reset_index()
    robust = by_group.groupby(["source", "model", "n", "k", "C"], dropna=False).agg(
        mean_delta=("delta", "mean"),
        worst_delta=("delta", "max"),
        best_group_delta=("delta", "min"),
        groups=("group", "nunique"),
        mean_auc=("auc", "mean"),
    ).reset_index().sort_values(["mean_delta", "worst_delta"])
    robust.to_csv(EXP / "s2_latent_compression_robust_ranking.csv", index=False)

    lines = ["# S2 latent-compression no-submit experiments", "", "No submission files were created.", ""]
    for group in ["chrono", "testpattern", "random_gap", "tail"]:
        sub = summ[summ.group.eq(group)].sort_values(["logloss", "delta"]).head(15)
        if len(sub) == 0:
            continue
        lines += [f"## {group} best", sub.to_string(index=False, float_format=lambda x: f"{x:.4f}"), ""]
    lines += ["## Robust coarse ranking across split groups", robust.head(25).to_string(index=False, float_format=lambda x: f"{x:.4f}"), ""]

    # Diagnostics: does latent beat raw/base consistently?
    lat = robust[robust.model.isin(["pca", "svd", "nmf", "kmeans"])].head(12)
    raw = robust[robust.model.eq("raw_selectk")].head(12)
    lines += ["## Best latent-only", lat.to_string(index=False, float_format=lambda x: f"{x:.4f}"), ""]
    lines += ["## Best raw-selectK sanity", raw.to_string(index=False, float_format=lambda x: f"{x:.4f}"), ""]
    out = EXP / "s2_latent_compression_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", EXP / "s2_latent_compression_eval_results.csv")
    print("wrote", EXP / "s2_latent_compression_eval_summary.csv")
    print("wrote", EXP / "s2_latent_compression_robust_ranking.csv")
    print("wrote", out)
    print("\n".join(lines[:120]))


def build_full_unsup_features(df: pd.DataFrame, sets: dict[str, list[str]]):
    """Write unsupervised all-row latent features for later diagnostics only.

    This uses no labels.  It is intentionally not a submission candidate.
    """
    all_rows = df.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    out = all_rows[ID].copy()
    configs = [
        ("existing_no_flat", "pca", 8), ("existing_no_flat", "pca", 16),
        ("combo_existing_dayflat", "pca", 8), ("combo_existing_dayflat", "pca", 16),
        ("combo_existing_dayflat", "kmeans", 8),
    ]
    mask = np.ones(len(all_rows), bool)
    for source, kind, n in configs:
        cols = valid_cols(all_rows, mask, sets[source])
        if not cols:
            continue
        pipe = make_latent_pipe(kind, n, C=0.003)
        # Fit only preprocessing+latent, not classifier.
        prep = Pipeline(pipe.steps[:-1])
        Z = prep.fit_transform(all_rows[cols])
        for j in range(Z.shape[1]):
            out[f"s2lat_{source}_{kind}{n}_{j:02d}"] = Z[:, j]
    path = FEAT / "s2_latent_compression_v1.parquet"
    out.to_parquet(path, index=False)
    print("wrote", path, out.shape)


if __name__ == "__main__":
    run_eval()
