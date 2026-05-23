#!/usr/bin/env python3
"""Big-swing experiment generator.

Runs several deliberately high-variance families:
1) feature+temporal graph/retrieval label propagation,
2) multi-target joint label-state surgery,
3) subject-regime routing,
4) cross-night episode-only mechanism model,
5) SSL/prototype-only model.

This is meant to create submission candidates and diagnostics, not to choose a safe
public-LB golf file automatically.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import warnings

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEAT = ROOT / "features"
OUT = ROOT / "outputs"
EXP = ROOT / "experiments"
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
IDS = ["subject_id", "sleep_date", "lifelog_date"]
KEYS = ["subject_id", "lifelog_date"]


def logit(p):
    p = np.clip(np.asarray(p, dtype=float), 0.02, 0.98)
    return np.log(p / (1 - p))


def sigmoid(x):
    return 1 / (1 + np.exp(-np.asarray(x)))


def read_sub(name: str) -> pd.DataFrame:
    p = OUT / name
    if not p.exists():
        raise FileNotFoundError(p)
    return pd.read_csv(p)


def assert_ids(a: pd.DataFrame, b: pd.DataFrame):
    if not a[IDS].astype(str).equals(b[IDS].astype(str)):
        raise ValueError("ID mismatch")


def load_base_table(feature_paths: list[Path] | None = None) -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).assign(is_train=1)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).assign(is_train=0)
    for y in LABELS:
        sample[y] = np.nan
    df = pd.concat([train, sample], ignore_index=True)
    df[KEYS] = df[KEYS].astype(str)
    con = duckdb.connect()
    if feature_paths is None:
        feature_paths = [
            FEAT / "model_features_v0.parquet",
            FEAT / "daily_window_features.parquet",
            FEAT / "routine_deviation_features_v1.parquet",
            FEAT / "sleep_block_features_v1.parquet",
            FEAT / "mechanism_sleep_load_features_v2.parquet",
            FEAT / "crossnight_day_flat_features_v2.parquet",
            FEAT / "public_failure_followup_features_v1.parquet",
            FEAT / "prior_sleep_window_features_v1.parquet",
            FEAT / "prior_sleep_proxy_features_v1.parquet",
            FEAT / "s2_routine_axes_v1.parquet",
            FEAT / "human_hypothesis_q2s2_features_v1.parquet",
            FEAT / "ssl_hourly_dino_temporal_embeddings.parquet",
            FEAT / "ssl_hourly_masked_ae_embeddings.parquet",
            FEAT / "ssl_semantic_cluster_features.parquet",
            FEAT / "ssl_dino_cluster_sweep_features.parquet",
        ]
    for p in feature_paths:
        if not p.exists():
            continue
        feat = con.execute(f"select * from read_parquet('{p}')").df()
        for k in KEYS:
            if k in feat.columns:
                feat[k] = feat[k].astype(str)
        # Merge only by subject_id+lifelog_date. sleep_date duplicates are harmless but annoying.
        if not set(KEYS).issubset(feat.columns):
            continue
        drop = [c for c in feat.columns if c in ["sleep_date"]]
        if drop:
            feat = feat.drop(columns=drop)
        dup = [c for c in feat.columns if c in df.columns and c not in KEYS]
        if dup:
            feat = feat.rename(columns={c: f"{c}__{p.stem}" for c in dup})
        df = df.merge(feat, on=KEYS, how="left")
    df["sleep_date"] = pd.to_datetime(df["sleep_date"])
    df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
    return df


def numeric_cols(df: pd.DataFrame, prefixes: tuple[str, ...] | None = None, contains: tuple[str, ...] | None = None, max_cols=600):
    bad = set(IDS + KEYS + LABELS + ["is_train"])
    cols = []
    for c in df.columns:
        if c in bad:
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            continue
        if prefixes and not c.startswith(prefixes):
            continue
        if contains and not any(s in c for s in contains):
            continue
        s = pd.to_numeric(df.loc[df.is_train.eq(1), c], errors="coerce")
        if s.notna().sum() >= 50 and s.nunique(dropna=True) > 2:
            cols.append(c)
    # Prefer compact non-hourly columns first for graph stability.
    cols = sorted(cols, key=lambda c: (c.startswith("h") or c.startswith("cn_h") or c.startswith("day_h"), c))
    return cols[:max_cols]


def fit_predict_logreg(df, cols, target, train_mask, query_mask, k=80, C=0.03):
    cols = [c for c in cols if c in df.columns]
    if not cols:
        raise ValueError("no columns")
    y = df.loc[train_mask, target].astype(int).to_numpy()
    if len(np.unique(y)) < 2:
        return np.repeat(float(np.mean(y)), int(query_mask.sum()))
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sel", SelectKBest(f_classif, k=min(k, len(cols)))),
        ("scale", RobustScaler()),
        ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
    ])
    pipe.fit(df.loc[train_mask, cols], y)
    return np.clip(pipe.predict_proba(df.loc[query_mask, cols])[:, 1], 0.02, 0.98)


def prep_matrix(df, cols, fit_mask, query_mask=None):
    imp = SimpleImputer(strategy="median")
    sc = StandardScaler()
    Xfit = imp.fit_transform(df.loc[fit_mask, cols])
    Xfit = sc.fit_transform(Xfit)
    if query_mask is None:
        return Xfit, imp, sc
    Xq = sc.transform(imp.transform(df.loc[query_mask, cols]))
    return Xfit, Xq, imp, sc


def temporal_kernel(known, query, tau=10.0, future=True):
    kd = known.sleep_date.values.astype("datetime64[D]").astype(int)
    qd = query.sleep_date.values.astype("datetime64[D]").astype(int)
    dist = np.abs(qd[:, None] - kd[None, :]).astype(float)
    if not future:
        dist = np.where(kd[None, :] < qd[:, None], dist, np.inf)
    w = np.exp(-dist / tau)
    w[~np.isfinite(w)] = 0
    return w


def graph_predict(df, known_mask, query_mask, target, cols, *, k_same=10, k_global=35, tau=10, same_w=0.70, feat_w=0.30, alpha=2.0, future=True):
    known = df.loc[known_mask].copy().reset_index(drop=True)
    query = df.loc[query_mask].copy().reset_index(drop=True)
    y = known[target].astype(float).to_numpy()
    g = float(np.nanmean(y))
    if len(cols) < 3:
        return np.repeat(g, len(query))
    Xk, Xq, _, _ = prep_matrix(pd.concat([known, query], ignore_index=True), cols, np.r_[np.ones(len(known), bool), np.zeros(len(query), bool)], np.r_[np.zeros(len(known), bool), np.ones(len(query), bool)])
    D = euclidean_distances(Xq, Xk)
    # Global feature KNN kernel.
    Wg = np.zeros_like(D)
    kg = min(k_global, D.shape[1])
    idx = np.argpartition(D, kth=kg-1, axis=1)[:, :kg]
    row = np.arange(D.shape[0])[:, None]
    local_scale = np.median(D[row, idx], axis=1, keepdims=True) + 1e-6
    Wg[row, idx] = np.exp(-D[row, idx] / local_scale)
    # Same-subject temporal-feature kernel.
    Ws = np.zeros_like(D)
    for sid, qidx in query.groupby("subject_id").groups.items():
        kidx = np.flatnonzero(known.subject_id.astype(str).to_numpy() == str(sid))
        if len(kidx) == 0:
            continue
        qpos = np.array(list(qidx), dtype=int)
        Dt = temporal_kernel(known.iloc[kidx], query.iloc[qpos], tau=tau, future=future)
        Df = D[np.ix_(qpos, kidx)]
        kk = min(k_same, len(kidx))
        ii = np.argpartition(Df, kth=kk-1, axis=1)[:, :kk]
        rr = np.arange(len(qpos))[:, None]
        scale = np.median(Df[rr, ii], axis=1, keepdims=True) + 1e-6
        Wloc = np.exp(-Df / scale) * (0.25 + Dt)
        mask = np.zeros_like(Wloc)
        mask[rr, ii] = 1
        Wloc *= mask
        Ws[np.ix_(qpos, kidx)] = Wloc
    W = same_w * Ws + feat_w * Wg
    p = (W @ y + alpha * g) / (W.sum(axis=1) + alpha)
    return np.clip(p, 0.02, 0.98)


def make_testpattern_masks(train, sample, seeds=range(6)):
    masks = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        mask = np.zeros(len(train), dtype=bool)
        for sid, sub in train.groupby("subject_id"):
            sub = sub.sort_values("sleep_date")
            tst = sample[sample.subject_id == sid].sort_values("sleep_date")
            n = min(len(sub) - 2, max(3, len(tst)))
            ranks = np.linspace(0, 1, len(sub))
            center = 0.70
            if len(tst):
                all_dates = pd.concat([sub[["sleep_date"]], tst[["sleep_date"]]]).sort_values("sleep_date").reset_index(drop=True)
                test_pos = all_dates.index[all_dates["sleep_date"].isin(tst["sleep_date"])].to_numpy()
                center = np.median(test_pos / max(1, len(all_dates)-1))
            prob = 0.30 + np.exp(-0.5*((ranks-center)/0.25)**2) + 0.5*ranks
            prob = prob/prob.sum()
            chosen = rng.choice(sub.index.to_numpy(), size=n, replace=False, p=prob)
            mask[train.index.get_indexer(chosen)] = True
        masks.append((f"testpattern{seed}", mask, True))
    # tail sanity
    mask = np.zeros(len(train), dtype=bool)
    for sid, sub in train.groupby("subject_id"):
        chosen = sub.sort_values("sleep_date").tail(max(3, int(round(len(sub)*0.36)))).index
        mask[train.index.get_indexer(chosen)] = True
    masks.append(("tail", mask, False))
    return masks


def save_candidate(name, df, refs, notes):
    path = OUT / name
    df.to_csv(path, index=False)
    rows = []
    for ref_name, ref in refs.items():
        assert_ids(df, ref)
        for y in LABELS:
            d = np.abs(df[y].to_numpy(float) - ref[y].to_numpy(float))
            rows.append({
                "candidate": name,
                "ref": ref_name,
                "target": y,
                "changed_rows": int((d > 1e-12).sum()),
                "mean_abs_delta": float(d.mean()),
                "p95_abs_delta": float(np.quantile(d, .95)),
                "max_abs_delta": float(d.max()),
                "mean_prob_shift": float(df[y].mean() - ref[y].mean()),
                "corr": float(np.corrcoef(df[y], ref[y])[0,1]) if d.max() > 0 else 1.0,
            })
    pd.DataFrame(rows).to_csv(EXP / f"{name.replace('.csv','')}_shift.csv", index=False)
    (EXP / f"{name.replace('.csv','')}_notes.json").write_text(json.dumps(notes | {"file": str(path)}, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main():
    OUT.mkdir(exist_ok=True); EXP.mkdir(exist_ok=True)
    df = load_base_table()
    train = df[df.is_train.eq(1)].copy().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    sample = df[df.is_train.eq(0)].copy().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    all_df = pd.concat([train, sample], ignore_index=True)
    known_mask = np.r_[np.ones(len(train), dtype=bool), np.zeros(len(sample), dtype=bool)]
    query_mask = ~known_mask

    base = read_sub("submission_base_v4_replicate_prob.csv")
    anchor = read_sub("submission_meta_anchor_w02_noq3_prob.csv")
    w03 = read_sub("submission_lbdiag_w03_noq3_q2w02_prob.csv")
    refs = {"base": base, "anchor": anchor, "w03": w03}

    # ---------- 1) Graph/retrieval label propagation ----------
    graph_cols = numeric_cols(all_df, contains=("sleep", "quiet", "screen", "steps", "activity", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "sslcl", "dyncl"), max_cols=500)
    graph_preds = sample[IDS].copy().reset_index(drop=True)
    graph_used = {}
    for y in LABELS:
        gp = graph_predict(all_df, known_mask, query_mask, y, graph_cols, k_same=12, k_global=45, tau=14, same_w=0.75, feat_w=0.25, alpha=2.5, future=True)
        graph_preds[y] = gp
        graph_used[y] = {"mean": float(np.mean(gp)), "std": float(np.std(gp))}
    graph_preds.to_csv(EXP / "big_swing_graph_raw_predictions.csv", index=False)

    c_graph_all = anchor.copy()
    for y in ["Q1", "S1", "S2", "S3", "S4"]:
        c_graph_all[y] = np.clip(0.55*anchor[y] + 0.45*graph_preds[y], .02, .98)
    c_graph_all["Q2"] = np.clip(0.80*anchor["Q2"] + 0.20*graph_preds["Q2"], .02, .98)
    c_graph_all["Q3"] = base["Q3"]
    save_candidate("submission_big_graph_state_noq3_prob.csv", c_graph_all, refs, {"family": "graph_label_propagation", "graph_cols": len(graph_cols), "used": graph_used, "rationale": "same-subject temporal-feature KNN + global feature KNN label diffusion; Q3 frozen, Q2 capped"})

    c_graph_s = anchor.copy()
    for y in ["S1", "S2", "S3", "S4"]:
        c_graph_s[y] = np.clip(0.45*anchor[y] + 0.55*graph_preds[y], .02, .98)
    c_graph_s["Q1"] = np.clip(0.75*anchor["Q1"] + 0.25*graph_preds["Q1"], .02, .98)
    c_graph_s["Q2"] = base["Q2"]; c_graph_s["Q3"] = base["Q3"]
    save_candidate("submission_big_graph_s_family_prob.csv", c_graph_s, refs, {"family": "graph_label_propagation", "variant": "S-family heavy, Q2/Q3 frozen"})

    # ---------- 2) Multi-target joint label-state surgery ----------
    Y = train[LABELS].astype(float).to_numpy()
    label_mean = Y.mean(axis=0)
    label_std = Y.std(axis=0) + 1e-6
    Z = (Y - label_mean) / label_std
    corr = np.corrcoef(Z, rowvar=False)
    # Leading state excluding Q3.
    use = [0,1,3,4,5,6]
    vals, vecs = np.linalg.eigh(corr[np.ix_(use, use)])
    v = vecs[:, np.argmax(vals)]
    if v[0] < 0: v = -v
    load = np.zeros(len(LABELS)); load[use] = v
    P = anchor[LABELS].to_numpy(float)
    Zp = (P - label_mean) / label_std
    state = Zp @ load / (np.sum(np.abs(load)) + 1e-6)
    c_joint = anchor.copy()
    for j,y in enumerate(LABELS):
        if y == "Q3":
            c_joint[y] = base[y]
            continue
        lam = 0.20 if y in ["Q2"] else 0.32
        # Convert latent state into a conservative logit nudge.
        c_joint[y] = np.clip(sigmoid(logit(anchor[y]) + lam * load[j] * state), .02, .98)
    save_candidate("submission_big_joint_label_state_noq3_prob.csv", c_joint, refs, {"family": "multi_target_joint_label_state", "label_corr": corr.round(4).tolist(), "leading_loadings": dict(zip(LABELS, load.round(4).tolist()))})

    # ---------- 3) Subject-regime routing ----------
    # Regime score: label autocorr + routine regularity. Route high-state subjects to graph/w03; low-state to anchor/base.
    regime = {}
    rcols = [c for c in graph_cols if any(s in c for s in ("axis_", "routine", "sleep", "quiet", "screen"))][:120]
    for sid, sub in train.groupby("subject_id"):
        sub = sub.sort_values("sleep_date")
        flips = []
        for y in LABELS:
            vals = sub[y].astype(int).to_numpy()
            if len(vals) > 1:
                flips.append(np.mean(np.abs(np.diff(vals))))
        flip_rate = float(np.mean(flips)) if flips else 0.5
        # lower feature entropy/proxy via std of compact routine cols after median fill
        if rcols:
            X = sub[rcols].apply(pd.to_numeric, errors="coerce")
            regularity = float(np.nanmean(1/(1+np.nanstd(X.to_numpy(float), axis=0))))
        else:
            regularity = 0.5
        score = (1 - flip_rate) + 0.3 * regularity
        regime[str(sid)] = {"flip_rate": flip_rate, "regularity": regularity, "state_score": score, "high_state": bool(score >= 0.82)}
    c_reg = anchor.copy()
    for i,row in sample.reset_index(drop=True).iterrows():
        sid = str(row.subject_id); high = regime.get(sid, {}).get("high_state", False)
        for y in LABELS:
            if y == "Q3":
                c_reg.loc[i,y] = base.loc[i,y]
            elif high and y in ["Q1","S1","S2","S3","S4"]:
                c_reg.loc[i,y] = np.clip(0.45*w03.loc[i,y] + 0.55*c_graph_all.loc[i,y], .02, .98)
            elif y == "Q2":
                c_reg.loc[i,y] = np.clip(0.85*anchor.loc[i,y] + 0.15*graph_preds.loc[i,y], .02, .98)
            else:
                c_reg.loc[i,y] = np.clip(0.80*anchor.loc[i,y] + 0.20*graph_preds.loc[i,y], .02, .98)
    save_candidate("submission_big_subject_regime_graph_prob.csv", c_reg, refs, {"family": "subject_regime_routing", "regime": regime, "rationale": "subjects with low label flip/high routine regularity get aggressive graph/state; others stay close to anchor"})

    # ---------- 4) Cross-night episode mechanism model ----------
    episode_cols = numeric_cols(all_df, prefixes=("cn_h", "day_h", "s4x_", "q1qual_", "q2lr_", "psw_", "pswp_"), max_cols=700)
    ep = sample[IDS].copy().reset_index(drop=True)
    for y in LABELS:
        C = 0.01 if y in ["Q2", "Q3"] else 0.03
        k = 80 if y in ["Q1","S4"] else 50
        ep[y] = fit_predict_logreg(all_df, episode_cols, y, known_mask, query_mask, k=k, C=C)
    ep.to_csv(EXP / "big_swing_episode_raw_predictions.csv", index=False)
    c_ep = anchor.copy()
    for y,w in {"Q1":0.35,"Q2":0.18,"S1":0.25,"S2":0.22,"S4":0.40}.items():
        c_ep[y] = np.clip((1-w)*anchor[y] + w*ep[y], .02, .98)
    c_ep["Q3"] = base["Q3"]
    save_candidate("submission_big_crossnight_episode_prob.csv", c_ep, refs, {"family": "crossnight_episode_mechanism", "episode_cols": len(episode_cols), "rationale": "episode/cross-night features only, blended into sleep-sensitive targets"})

    # ---------- 5) SSL/prototype-only model ----------
    ssl_cols = numeric_cols(all_df, prefixes=("ssl_", "sslcl_", "dyncl_"), max_cols=250)
    sslp = sample[IDS].copy().reset_index(drop=True)
    # Add fresh tiny prototypes from SSL embeddings, fitted transductively.
    emb_cols = [c for c in ssl_cols if c.startswith(("ssl_dino_temporal_", "ssl_masked_ae_"))]
    proto_feats = []
    if len(emb_cols) >= 4:
        X, _, _ = prep_matrix(all_df, emb_cols[:96], np.ones(len(all_df), dtype=bool))
        for k in [4, 8, 12]:
            km = KMeans(n_clusters=k, random_state=130+k, n_init=20).fit(X)
            dist = km.transform(X)
            labels = km.labels_
            for j in range(k):
                col = f"fresh_ssl_k{k}_is{j}"
                all_df[col] = (labels == j).astype(float)
                proto_feats.append(col)
            all_df[f"fresh_ssl_k{k}_mindist"] = dist.min(axis=1)
            proto_feats.append(f"fresh_ssl_k{k}_mindist")
    ssl_cols2 = ssl_cols + proto_feats
    for y in LABELS:
        sslp[y] = fit_predict_logreg(all_df, ssl_cols2, y, known_mask, query_mask, k=60, C=0.03)
    sslp.to_csv(EXP / "big_swing_ssl_raw_predictions.csv", index=False)
    c_ssl = anchor.copy()
    for y,w in {"Q1":0.20,"Q3":0.30,"S2":0.35,"S4":0.25}.items():
        c_ssl[y] = np.clip((1-w)*anchor[y] + w*sslp[y], .02, .98)
    c_ssl["Q2"] = base["Q2"]
    save_candidate("submission_big_ssl_prototype_prob.csv", c_ssl, refs, {"family": "temporal_ssl_prototypes", "ssl_cols": len(ssl_cols2), "fresh_proto_cols": len(proto_feats), "rationale": "SSL/prototype-only head blended into Q3/S2/S4/Q1; Q2 frozen"})

    # ---------- Compact validation probe for graph/episode/ssl raw heads ----------
    val_rows = []
    masks = make_testpattern_masks(train, sample, seeds=range(4))
    compact_cols = {
        "graph": graph_cols,
        "episode": episode_cols,
        "ssl": ssl_cols2,
    }
    for split, vm, future in masks:
        known = ~vm
        train_df = train.copy()
        for fam, cols in compact_cols.items():
            for y in LABELS:
                try:
                    if fam == "graph":
                        p = graph_predict(train_df, known, vm, y, cols, k_same=10, k_global=35, tau=14, alpha=2.5, future=future)
                    else:
                        p = fit_predict_logreg(train_df, cols, y, known, vm, k=60, C=0.03)
                    loss = log_loss(train_df.loc[vm, y].astype(int), p, labels=[0,1])
                    base_rate = np.repeat(train_df.loc[known, y].mean(), vm.sum())
                    null_loss = log_loss(train_df.loc[vm, y].astype(int), np.clip(base_rate, .02, .98), labels=[0,1])
                    val_rows.append({"split": split, "family": fam, "target": y, "logloss": loss, "null_logloss": null_loss, "delta_vs_null": loss-null_loss})
                except Exception as e:
                    val_rows.append({"split": split, "family": fam, "target": y, "error": str(e)})
    val = pd.DataFrame(val_rows)
    val.to_csv(EXP / "big_swing_family_validation_probe.csv", index=False)

    # Candidate master summary.
    cand_files = sorted(OUT.glob("submission_big_*_prob.csv"))
    summary = []
    for p in cand_files:
        dfc = pd.read_csv(p)
        row = {"file": p.name}
        for refname, ref in refs.items():
            ds = []
            for y in LABELS:
                ds.append(np.abs(dfc[y].to_numpy(float)-ref[y].to_numpy(float)).mean())
            row[f"mean_abs_vs_{refname}"] = float(np.mean(ds))
            row[f"max_target_mean_abs_vs_{refname}"] = float(np.max(ds))
        summary.append(row)
    summ = pd.DataFrame(summary).sort_values("mean_abs_vs_anchor", ascending=False)
    summ.to_csv(EXP / "big_swing_all_candidate_summary.csv", index=False)
    report = [
        "# Big-swing all-experiment report",
        "",
        "Generated five structural candidate families: graph label propagation, joint label-state, subject-regime routing, cross-night episode, and SSL prototypes.",
        "",
        "## Candidate movement summary",
        summ.to_string(index=False, float_format=lambda x: f"{x:.6f}"),
        "",
        "## Validation probe mean delta vs null",
        val.dropna(subset=["delta_vs_null"]).groupby(["family","target"])["delta_vs_null"].mean().reset_index().to_string(index=False, float_format=lambda x: f"{x:.6f}"),
        "",
        "## Notes",
        "- These are high-variance candidates; movement size is intentional.",
        "- Graph candidates are the cleanest structural state-completion test.",
        "- Episode and SSL candidates are independent representation-family tests.",
        "- Q3 is frozen in most files because prior diagnostics treated it as risky/unstable.",
    ]
    (EXP / "big_swing_all_experiment_report.md").write_text("\n".join(report), encoding="utf-8")
    print("wrote", EXP / "big_swing_all_experiment_report.md")
    print(summ.to_string(index=False))
    print("\nvalidation delta vs null")
    print(val.dropna(subset=["delta_vs_null"]).groupby(["family","target"])["delta_vs_null"].mean().reset_index().to_string(index=False))


if __name__ == "__main__":
    main()
