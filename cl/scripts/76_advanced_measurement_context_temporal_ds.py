#!/usr/bin/env python3
"""Higher-order diagnostics for tiny lifelog labels.

No submissions. Adds:
1) Bernoulli low-rank measurement model / label loadings.
2) Subject-calibrated residual anomaly analysis.
3) Subject-debiased raw identity token association via within-subject permutations.
4) Temporal influence network controlling subject prevalence.
5) Context-token event study around token appearance/disappearance.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXP = ROOT / "experiments"
FEAT = ROOT / "features"
EXP.mkdir(exist_ok=True)
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def load_train():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    train["sleep_date"] = pd.to_datetime(train["sleep_date"])
    train["lifelog_date"] = pd.to_datetime(train["lifelog_date"])
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    states = EXP / "advanced_ds_row_latent_states.csv"
    if states.exists():
        st = pd.read_csv(states)
        st["lifelog_date"] = pd.to_datetime(st["lifelog_date"])
        train = train.merge(st[["subject_id", "lifelog_date", "latent_state", "state_confidence"]], on=["subject_id", "lifelog_date"], how="left")
    train["date"] = train["lifelog_date"].dt.date.astype(str)
    return train


def bernoulli_lowrank(Y, k=1, l2=0.02, seed=0, maxiter=1000):
    """Fit P(Y_il=1)=sigmoid(row_bias_i + label_bias_l + U_i V_l). Diagnostic only."""
    rng = np.random.default_rng(seed)
    n, m = Y.shape
    y = Y.astype(float)
    label_init = logit(np.clip(y.mean(axis=0), 0.02, 0.98))
    row_init = logit(np.clip(y.mean(axis=1), 0.02, 0.98)) - logit(np.clip(y.mean(), 0.02, 0.98))
    U0 = rng.normal(0, 0.15, size=(n, k))
    V0 = rng.normal(0, 0.15, size=(m, k))
    x0 = np.r_[row_init, label_init, U0.ravel(), V0.ravel()]

    def unpack(x):
        rb = x[:n]
        lb = x[n:n+m]
        U = x[n+m:n+m+n*k].reshape(n, k)
        V = x[n+m+n*k:].reshape(m, k)
        return rb, lb, U, V

    def obj(x):
        rb, lb, U, V = unpack(x)
        eta = rb[:, None] + lb[None, :] + U @ V.T
        # stable BCE
        loss = np.logaddexp(0, eta).sum() - (y * eta).sum()
        pen = l2 * (np.square(rb).sum() + np.square(lb).sum() + np.square(U).sum() + np.square(V).sum())
        return float(loss + pen)

    res = minimize(obj, x0, method="L-BFGS-B", options={"maxiter": maxiter, "maxls": 50})
    rb, lb, U, V = unpack(res.x)
    P = expit(rb[:, None] + lb[None, :] + U @ V.T)
    bce = -(y * np.log(np.clip(P, 1e-6, 1-1e-6)) + (1-y) * np.log(np.clip(1-P, 1e-6, 1-1e-6)))
    n_params = n + m + n*k + m*k
    bic = 2 * bce.sum() + n_params * np.log(n*m)
    return {"k": k, "success": bool(res.success), "loss": float(bce.sum()), "mean_logloss": float(bce.mean()), "bic": float(bic), "row_bias": rb, "label_bias": lb, "U": U, "V": V, "P": P, "bce": bce}


def measurement_model(train):
    Y = train[LABELS].astype(int).to_numpy()
    fits = []
    best_by_k = []
    for k in [0, 1, 2, 3]:
        if k == 0:
            p = np.tile(np.clip(Y.mean(axis=0), 1e-4, 1-1e-4), (len(Y), 1))
            bce = -(Y*np.log(p)+(1-Y)*np.log(1-p))
            bic = 2*bce.sum() + len(LABELS)*np.log(Y.size)
            fit = {"k":0,"loss":float(bce.sum()),"mean_logloss":float(bce.mean()),"bic":float(bic),"P":p,"bce":bce,"U":np.zeros((len(Y),0)),"V":np.zeros((len(LABELS),0)),"row_bias":np.zeros(len(Y)),"label_bias":logit(np.clip(Y.mean(axis=0),.02,.98))}
        else:
            candidates = [bernoulli_lowrank(Y, k=k, seed=s) for s in range(4)]
            fit = min(candidates, key=lambda d: d["loss"])
        fits.append(fit)
        best_by_k.append({"k": k, "loss": fit["loss"], "mean_logloss": fit["mean_logloss"], "bic": fit["bic"]})
    pd.DataFrame(best_by_k).to_csv(EXP / "advanced76_measurement_lowrank_fit.csv", index=False)
    best = min(fits, key=lambda d: d["bic"])
    # But also save K=2/K=3 loadings because BIC can prefer K=0 in tiny data; use best nonzero by loss for structure.
    struct = min([f for f in fits if f["k"] > 0], key=lambda d: d["loss"])
    load_rows = []
    for j, lab in enumerate(LABELS):
        row = {"label": lab, "label_bias": float(struct["label_bias"][j]), "empirical_rate": float(Y[:,j].mean())}
        for c in range(struct["k"]):
            row[f"loading_{c+1}"] = float(struct["V"][j,c])
        load_rows.append(row)
    pd.DataFrame(load_rows).to_csv(EXP / "advanced76_measurement_label_loadings.csv", index=False)
    row_score = train[["subject_id","sleep_date","lifelog_date","date"] + LABELS].copy()
    for c in range(struct["k"]):
        row_score[f"latent_factor_{c+1}"] = struct["U"][:,c]
    row_score["row_bias_severity"] = struct["row_bias"]
    row_score["measurement_residual_bce"] = struct["bce"].sum(axis=1)
    row_score["max_label_residual"] = struct["bce"].max(axis=1)
    row_score["worst_residual_label"] = [LABELS[i] for i in struct["bce"].argmax(axis=1)]
    if "latent_state" in train.columns:
        row_score["mixture_latent_state"] = train["latent_state"]
    row_score.to_csv(EXP / "advanced76_measurement_row_scores_anomalies.csv", index=False)
    # subject calibration from model factors
    subj = row_score.groupby("subject_id").agg(
        n=("subject_id","size"),
        residual_mean=("measurement_residual_bce","mean"),
        severity_mean=("row_bias_severity","mean"),
        severity_std=("row_bias_severity","std"),
    ).reset_index()
    for lab in LABELS:
        subj[f"prev_{lab}"] = train.groupby("subject_id")[lab].mean().values
    subj.to_csv(EXP / "advanced76_subject_calibration_measurement.csv", index=False)
    return struct


def residual_anomaly_context(train):
    rows = pd.read_csv(EXP / "advanced76_measurement_row_scores_anomalies.csv")
    cov_path = FEAT / "observation_coverage_features.parquet"
    if cov_path.exists():
        cov = pd.read_parquet(cov_path)
        d = rows.merge(cov, on=["subject_id","date"], how="left")
        feat_cols = [c for c in cov.columns if c not in ["subject_id","date","split"]]
        out = []
        top = d["measurement_residual_bce"].quantile(0.9)
        d["high_residual"] = (d["measurement_residual_bce"] >= top).astype(int)
        for f in feat_cols:
            x = d[f].fillna(0).astype(float); y = d["high_residual"]
            if x.nunique() < 2: continue
            try: auc = roc_auc_score(y, x); auc_abs = max(auc, 1-auc)
            except Exception: continue
            out.append({"feature": f, "auc_absdir_for_high_residual": auc_abs, "mean_high": float(x[y==1].mean()), "mean_other": float(x[y==0].mean()), "diff_high_minus_other": float(x[y==1].mean()-x[y==0].mean())})
        pd.DataFrame(out).sort_values("auc_absdir_for_high_residual", ascending=False).to_csv(EXP / "advanced76_residual_anomaly_coverage_association.csv", index=False)


def subject_debiased_token_association(train, n_perm=80, top_n=160):
    token_path = FEAT / "observation_identity_token_features.parquet"
    if not token_path.exists():
        return
    tok = pd.read_parquet(token_path)
    d = train.merge(tok, on=["subject_id","date"], how="left").fillna(0)
    feats = [c for c in tok.columns if c not in ["subject_id","date"]]
    # prefilter frequent enough but not ubiquitous
    freq = (d[feats] > 0).sum().sort_values(ascending=False)
    feats = freq[(freq >= 5) & (freq <= len(d)-5)].head(top_n).index.tolist()
    rng = np.random.default_rng(123)
    rows = []
    for lab in LABELS:
        y = d[lab].astype(float)
        y_center = y - d.groupby("subject_id")[lab].transform("mean")
        for f in feats:
            x = (d[f] > 0).astype(float)
            # within-subject centered covariance; removes pure subject prevalence/token ownership
            x_center = x - x.groupby(d["subject_id"]).transform("mean")
            obs = float(np.mean(x_center * y_center))
            if abs(obs) < 1e-5: continue
            null = []
            for _ in range(n_perm):
                yp = y.copy()
                for sid, idx in d.groupby("subject_id").groups.items():
                    vals = yp.loc[list(idx)].to_numpy().copy(); rng.shuffle(vals); yp.loc[list(idx)] = vals
                ypc = yp - yp.groupby(d["subject_id"]).transform("mean")
                null.append(float(np.mean(x_center * ypc)))
            null = np.array(null)
            p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (len(null) + 1)
            if p <= 0.08:
                rows.append({"target": lab, "token": f, "within_subject_cov": obs, "perm_p": p,
                             "presence_days": int(x.sum()), "raw_rate_present": float(y[x==1].mean()), "raw_rate_absent": float(y[x==0].mean())})
    out = pd.DataFrame(rows)
    if len(out):
        out = out.sort_values(["perm_p", "target", "within_subject_cov"], ascending=[True, True, False])
    out.to_csv(EXP / "advanced76_subject_debiased_token_association.csv", index=False)


def temporal_influence_network(train):
    # Build lag/lead rows within subject. Predict target_t using target_{t-1} and other labels_{t-1}, controlling subject.
    d = train.sort_values(["subject_id","lifelog_date"]).copy()
    for lab in LABELS:
        d[f"lag1_{lab}"] = d.groupby("subject_id")[lab].shift(1)
        d[f"lead1_{lab}"] = d.groupby("subject_id")[lab].shift(-1)
    rows = []
    for target in LABELS:
        use = d.dropna(subset=[f"lag1_{l}" for l in LABELS] + [target]).copy()
        if use[target].nunique() < 2 or len(use) < 50: continue
        X_cols = [f"lag1_{l}" for l in LABELS]
        X = use[X_cols + ["subject_id"]]
        y = use[target].astype(int).to_numpy()
        pre = ColumnTransformer([
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), X_cols),
            ("sid", OneHotEncoder(handle_unknown="ignore"), ["subject_id"]),
        ])
        pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(C=0.25, solver="liblinear", class_weight="balanced", max_iter=1000))])
        # CV full vs subject-only vs own-lag-only
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        probs = np.zeros(len(y)); probs_sid = np.zeros(len(y)); probs_own = np.zeros(len(y))
        for tr, va in cv.split(X, y):
            pipe.fit(X.iloc[tr], y[tr]); probs[va] = pipe.predict_proba(X.iloc[va])[:,1]
            sid_pipe = Pipeline([("pre", ColumnTransformer([("sid", OneHotEncoder(handle_unknown="ignore"), ["subject_id"])])), ("clf", LogisticRegression(C=0.25, solver="liblinear", class_weight="balanced", max_iter=1000))])
            sid_pipe.fit(X.iloc[tr][["subject_id"]], y[tr]); probs_sid[va] = sid_pipe.predict_proba(X.iloc[va][["subject_id"]])[:,1]
            own_cols = [f"lag1_{target}", "subject_id"]
            own_pre = ColumnTransformer([
                ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), [f"lag1_{target}"]),
                ("sid", OneHotEncoder(handle_unknown="ignore"), ["subject_id"]),
            ])
            own_pipe = Pipeline([("pre", own_pre), ("clf", LogisticRegression(C=0.25, solver="liblinear", class_weight="balanced", max_iter=1000))])
            own_pipe.fit(X.iloc[tr][own_cols], y[tr]); probs_own[va] = own_pipe.predict_proba(X.iloc[va][own_cols])[:,1]
        base = np.repeat(np.clip(y.mean(), .02, .98), len(y))
        rows.append({"target": target, "edge": "ALL_LAGS", "coef": np.nan, "auc": roc_auc_score(y, probs),
                     "ll_improve_vs_base": log_loss(y, base, labels=[0,1]) - log_loss(y, np.clip(probs,.02,.98), labels=[0,1]),
                     "ll_improve_vs_subject_only": log_loss(y, np.clip(probs_sid,.02,.98), labels=[0,1]) - log_loss(y, np.clip(probs,.02,.98), labels=[0,1]),
                     "ll_improve_vs_own_lag": log_loss(y, np.clip(probs_own,.02,.98), labels=[0,1]) - log_loss(y, np.clip(probs,.02,.98), labels=[0,1]),
                     "n": len(y)})
        pipe.fit(X, y)
        coefs = pipe.named_steps["clf"].coef_[0][:len(X_cols)]
        for col, coef in zip(X_cols, coefs):
            rows.append({"target": target, "edge": col.replace("lag1_", "") + "_lag_to_" + target, "coef": float(coef), "auc": np.nan,
                         "ll_improve_vs_base": np.nan, "ll_improve_vs_subject_only": np.nan, "ll_improve_vs_own_lag": np.nan, "n": len(y)})
    pd.DataFrame(rows).to_csv(EXP / "advanced76_temporal_influence_network.csv", index=False)


def context_event_study(train):
    deb_path = EXP / "advanced76_subject_debiased_token_association.csv"
    token_path = FEAT / "observation_identity_token_features.parquet"
    if not deb_path.exists() or not token_path.exists(): return
    deb = pd.read_csv(deb_path)
    if len(deb) == 0: return
    tok = pd.read_parquet(token_path)
    # choose top 30 debiased tokens, then examine label rates before/during/after presence episodes
    top_tokens = deb.sort_values("perm_p").token.drop_duplicates().head(30).tolist()
    d = train.merge(tok[["subject_id","date"] + top_tokens], on=["subject_id","date"], how="left").fillna(0)
    rows = []
    for token in top_tokens:
        for sid, g in d.sort_values("lifelog_date").groupby("subject_id"):
            present = (g[token] > 0).astype(int).to_numpy()
            if present.sum() == 0: continue
            for i, val in enumerate(present):
                if val != 1: continue
                prev_present = present[i-1] if i > 0 else np.nan
                next_present = present[i+1] if i < len(present)-1 else np.nan
                phase = "continuing"
                if i == 0 or prev_present == 0: phase = "appearance"
                elif i == len(present)-1 or next_present == 0: phase = "disappearance_edge"
                for lab in LABELS:
                    rows.append({"token": token, "subject_id": sid, "phase": phase, "target": lab, "y": int(g.iloc[i][lab])})
    ev = pd.DataFrame(rows)
    if len(ev):
        summ = ev.groupby(["token","phase","target"]).agg(n=("y","size"), rate=("y","mean")).reset_index()
        base = train[LABELS].mean().rename("global_rate").reset_index().rename(columns={"index":"target"})
        summ = summ.merge(base, on="target", how="left")
        summ["lift_vs_global"] = summ["rate"] - summ["global_rate"]
        summ.sort_values(["token","target","phase"]).to_csv(EXP / "advanced76_context_token_event_study.csv", index=False)


def write_report():
    def tbl(name, n=12, sort=None, asc=False):
        p = EXP / name
        if not p.exists(): return "(missing)"
        df = pd.read_csv(p)
        if sort and sort in df.columns: df = df.sort_values(sort, ascending=asc)
        return "```\n" + df.head(n).to_string(index=False) + "\n```"
    report = f"""# Advanced measurement/context/temporal data-science diagnostics

This extends observation-process diagnostics into measurement theory and subject-debiased context analysis. No submissions generated.

## Produced files

- `advanced76_measurement_lowrank_fit.csv`
- `advanced76_measurement_label_loadings.csv`
- `advanced76_measurement_row_scores_anomalies.csv`
- `advanced76_subject_calibration_measurement.csv`
- `advanced76_residual_anomaly_coverage_association.csv`
- `advanced76_subject_debiased_token_association.csv`
- `advanced76_temporal_influence_network.csv`
- `advanced76_context_token_event_study.csv`

## 1. Bernoulli measurement model fit

Lower mean logloss means the label matrix is better explained by latent row factors; BIC penalizes tiny-data overparameterization.

{tbl('advanced76_measurement_lowrank_fit.csv', 10)}

Label loadings from the strongest nonzero latent-factor model:

{tbl('advanced76_measurement_label_loadings.csv', 10)}

Subject calibration summary:

{tbl('advanced76_subject_calibration_measurement.csv', 10, 'residual_mean', False)}

## 2. High-residual/noisy label rows vs sensor coverage

Rows badly fit by the label measurement model are candidate label-noise, transition, or multi-state days. Coverage associations:

{tbl('advanced76_residual_anomaly_coverage_association.csv', 12, 'auc_absdir_for_high_residual', False)}

## 3. Subject-debiased identity-token associations

These survive within-subject label permutation tests, so they are less likely to be pure subject fingerprint. Still small-N and context-specific.

{tbl('advanced76_subject_debiased_token_association.csv', 20, 'perm_p', True)}

## 4. Temporal influence network controlling subject

`ALL_LAGS` rows show predictive value of all previous-day labels beyond subject-only and own-lag baselines. Edge rows are regularized coefficients.

{tbl('advanced76_temporal_influence_network.csv', 40)}

## 5. Context event study

For top subject-debiased tokens, this checks whether labels change on token appearance/continuation/disappearance days.

{tbl('advanced76_context_token_event_study.csv', 30, 'lift_vs_global', False)}

## Interpretation notes

- If low-rank label factors group Q/S items differently from the earlier mixture states, the labels have multiple measurement axes rather than one severity axis.
- If BIC does not prefer complex factors but residual anomalies are structured, the data has sparse exceptions/noise rather than smooth latent dimensions.
- Subject-debiased token results are stronger evidence than raw BSSID chi-square because subject prevalence is removed by within-subject centering and permutation.
- Temporal influence edges are not causal. They indicate label grammar: which previous-day answers help complete current answers after controlling subject.
"""
    (EXP / "advanced76_data_science_report.md").write_text(report)


def main():
    train = load_train()
    measurement_model(train)
    residual_anomaly_context(train)
    subject_debiased_token_association(train)
    temporal_influence_network(train)
    context_event_study(train)
    write_report()
    files = [
        "advanced76_measurement_lowrank_fit.csv", "advanced76_measurement_label_loadings.csv",
        "advanced76_measurement_row_scores_anomalies.csv", "advanced76_subject_calibration_measurement.csv",
        "advanced76_residual_anomaly_coverage_association.csv", "advanced76_subject_debiased_token_association.csv",
        "advanced76_temporal_influence_network.csv", "advanced76_context_token_event_study.csv",
        "advanced76_data_science_report.md",
    ]
    print(json.dumps({"ok": True, "files": [str(EXP / f) for f in files]}, indent=2))

if __name__ == "__main__":
    main()
