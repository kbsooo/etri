#!/usr/bin/env python3
"""Observation-process deep diagnostics for CH2026 lifelog sleep labels.

No submissions are generated. Outputs focus on: sensor coverage/missingness, time-window
semantics, negative controls, raw identity context, and subject-specific label language.
"""
from __future__ import annotations

import ast
import json
import math
import warnings
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import mutual_info_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "ch2025_data_items"
EXP = ROOT / "experiments"
FEAT = ROOT / "features"
EXP.mkdir(exist_ok=True)
FEAT.mkdir(exist_ok=True)
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
IDS = ["subject_id", "sleep_date", "lifelog_date"]
MODALITY_FILES = {
    "ac": "ch2025_mACStatus.parquet",
    "activity": "ch2025_mActivity.parquet",
    "ambience": "ch2025_mAmbience.parquet",
    "ble": "ch2025_mBle.parquet",
    "gps": "ch2025_mGps.parquet",
    "m_light": "ch2025_mLight.parquet",
    "screen": "ch2025_mScreenStatus.parquet",
    "usage": "ch2025_mUsageStats.parquet",
    "wifi": "ch2025_mWifi.parquet",
    "hr": "ch2025_wHr.parquet",
    "w_light": "ch2025_wLight.parquet",
    "pedo": "ch2025_wPedo.parquet",
}


def safe_len(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return 0
    if isinstance(x, (list, tuple, dict)):
        return len(x)
    if isinstance(x, str):
        try:
            return len(ast.literal_eval(x))
        except Exception:
            return 1
    return 1


def flatten_records(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    if isinstance(x, str):
        try:
            x = ast.literal_eval(x)
        except Exception:
            return []
    if isinstance(x, dict):
        return [x]
    if isinstance(x, (list, tuple, np.ndarray)):
        return list(x)
    return []


def longest_zero_run(hours_present):
    arr = [1 if h in hours_present else 0 for h in range(24)]
    best = cur = 0
    for v in arr:
        if v == 0:
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def add_dates(df):
    out = df.copy()
    out["sleep_date"] = pd.to_datetime(out["sleep_date"])
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"])
    out["date"] = out["lifelog_date"].dt.date.astype(str)
    return out


def load_base():
    train = add_dates(pd.read_csv(DATA / "ch2026_metrics_train.csv"))
    sample = add_dates(pd.read_csv(DATA / "ch2026_submission_sample.csv"))
    train["split"] = "train"
    sample["split"] = "test"
    for c in LABELS:
        sample[c] = np.nan
    all_rows = pd.concat([train, sample], ignore_index=True)
    states_path = EXP / "advanced_ds_row_latent_states.csv"
    if states_path.exists():
        states = pd.read_csv(states_path)
        states["lifelog_date"] = pd.to_datetime(states["lifelog_date"])
        all_rows = all_rows.merge(states[["subject_id", "lifelog_date", "latent_state", "state_confidence"]], on=["subject_id", "lifelog_date"], how="left")
        train = train.merge(states[["subject_id", "lifelog_date", "latent_state", "state_confidence"]], on=["subject_id", "lifelog_date"], how="left")
    return train, sample, all_rows


def read_raw(mod):
    p = RAW / MODALITY_FILES[mod]
    df = pd.read_parquet(p)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date.astype(str)
    df["hour"] = df["timestamp"].dt.hour.astype(int)
    return df


def build_coverage(all_rows):
    keys = all_rows[["subject_id", "date", "split"]].drop_duplicates().copy()
    cov = keys.copy()
    hourly_long = []
    for mod in MODALITY_FILES:
        df = read_raw(mod)
        value_cols = [c for c in df.columns if c not in {"subject_id", "timestamp", "date", "hour"}]
        main = value_cols[0] if value_cols else None
        df["record_n"] = 1
        if main is not None:
            if df[main].dtype == "object":
                df["item_n"] = df[main].map(safe_len)
            else:
                df["item_n"] = df[main].notna().astype(int)
        else:
            df["item_n"] = 1
        h = df.groupby(["subject_id", "date", "hour"], as_index=False).agg(
            record_n=("record_n", "sum"), item_n=("item_n", "sum")
        )
        h["modality"] = mod
        hourly_long.append(h)
        g = h.groupby(["subject_id", "date"]).agg(
            **{
                f"{mod}_record_n": ("record_n", "sum"),
                f"{mod}_item_n": ("item_n", "sum"),
                f"{mod}_active_hours": ("hour", "nunique"),
                f"{mod}_night_hours": ("hour", lambda s: int(sum(x in [0,1,2,3,4,5,22,23] for x in set(s)))),
                f"{mod}_day_hours": ("hour", lambda s: int(sum(6 <= x <= 21 for x in set(s)))),
                f"{mod}_longest_missing_hours": ("hour", lambda s: longest_zero_run(set(s))),
            }
        ).reset_index()
        cov = cov.merge(g, on=["subject_id", "date"], how="left")
    count_cols = [c for c in cov.columns if c not in ["subject_id", "date", "split"]]
    cov[count_cols] = cov[count_cols].fillna(0)
    cov["any_sensor_active_hours"] = cov[[c for c in cov.columns if c.endswith("_active_hours")]].gt(0).sum(axis=1)
    cov.to_parquet(FEAT / "observation_coverage_features.parquet", index=False)
    pd.concat(hourly_long, ignore_index=True).to_csv(EXP / "observation_hourly_coverage_long.csv", index=False)
    return cov, pd.concat(hourly_long, ignore_index=True)


def univariate_auc_table(df, features, targets, prefix, state_col=None):
    rows = []
    for ycol in targets:
        y = df[ycol]
        mask = y.notna()
        if mask.sum() < 20 or y[mask].nunique() < 2:
            continue
        for f in features:
            x = df.loc[mask, f].astype(float).replace([np.inf, -np.inf], np.nan).fillna(0)
            if x.nunique() < 2:
                continue
            yy = y[mask].astype(int)
            try:
                auc = roc_auc_score(yy, x)
                auc_dir = max(auc, 1 - auc)
            except Exception:
                auc = auc_dir = np.nan
            rows.append({
                "analysis": prefix, "target": ycol, "feature": f,
                "auc_raw": auc, "auc_absdir": auc_dir,
                "mean_pos": float(x[yy == 1].mean()), "mean_neg": float(x[yy == 0].mean()),
                "diff_pos_minus_neg": float(x[yy == 1].mean() - x[yy == 0].mean()),
                "n": int(mask.sum()), "pos_rate": float(yy.mean()),
            })
    return pd.DataFrame(rows)


def cv_logistic_eval(df, features, target, include_subject=False, shuffle_y=False, shift_features=False, random_state=42):
    d = df[["subject_id", target] + features].copy()
    d = d[d[target].notna()].reset_index(drop=True)
    if d[target].nunique() < 2 or len(d) < 40:
        return None
    if shift_features:
        for f in features:
            d[f] = d.groupby("subject_id")[f].shift(1)
    y = d[target].astype(int).to_numpy()
    if shuffle_y:
        rng = np.random.default_rng(random_state)
        ys = []
        for sid, idx in d.groupby("subject_id").groups.items():
            vals = y[list(idx)].copy(); rng.shuffle(vals); ys.extend(zip(idx, vals))
        yy = np.array([v for _, v in sorted(ys)])
    else:
        yy = y
    X = d[features + (["subject_id"] if include_subject else [])]
    numeric = features
    if include_subject:
        pre = ColumnTransformer([
            ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), numeric),
            ("sid", OneHotEncoder(handle_unknown="ignore"), ["subject_id"]),
        ])
    else:
        pre = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
    pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(C=0.1, penalty="l2", solver="liblinear", max_iter=1000, class_weight="balanced"))])
    cv = StratifiedKFold(n_splits=min(5, max(2, min(np.bincount(yy)))), shuffle=True, random_state=random_state)
    probs = np.zeros(len(yy))
    for tr, va in cv.split(X, yy):
        pipe.fit(X.iloc[tr], yy[tr])
        probs[va] = pipe.predict_proba(X.iloc[va])[:, 1]
    base_p = np.repeat(np.clip(yy.mean(), 0.02, 0.98), len(yy))
    try: auc = roc_auc_score(yy, probs)
    except Exception: auc = np.nan
    return {
        "target": target, "n": len(yy), "pos_rate": float(yy.mean()),
        "auc": float(auc) if not np.isnan(auc) else np.nan,
        "logloss": float(log_loss(yy, np.clip(probs, 0.02, 0.98), labels=[0,1])),
        "base_logloss": float(log_loss(yy, base_p, labels=[0,1])),
        "logloss_improvement": float(log_loss(yy, base_p, labels=[0,1]) - log_loss(yy, np.clip(probs, 0.02, 0.98), labels=[0,1])),
    }


def coverage_associations(train, sample, cov):
    base = pd.concat([train, sample], ignore_index=True)
    base["date"] = base["lifelog_date"].dt.date.astype(str)
    d = base.merge(cov, on=["subject_id", "date", "split"], how="left")
    feats = [c for c in cov.columns if c not in ["subject_id", "date", "split"]]
    assoc = univariate_auc_table(d[d.split == "train"], feats, LABELS, "coverage_vs_label")
    assoc.to_csv(EXP / "observation_coverage_label_association.csv", index=False)
    if "latent_state" in d.columns:
        # one-vs-rest state association
        dd = d[d["latent_state"].notna()].copy()
        state_rows = []
        for st in sorted(dd["latent_state"].dropna().unique()):
            dd[f"state_{int(st)}"] = (dd["latent_state"] == st).astype(int)
            state_rows.append(univariate_auc_table(dd, feats, [f"state_{int(st)}"], "coverage_vs_latent_state"))
        pd.concat(state_rows, ignore_index=True).to_csv(EXP / "observation_coverage_state_association.csv", index=False)
    # train/test shift
    dd = d.copy(); dd["is_test"] = (dd["split"] == "test").astype(int)
    shift = univariate_auc_table(dd, feats, ["is_test"], "coverage_train_test_shift")
    shift.to_csv(EXP / "observation_coverage_train_test_shift.csv", index=False)
    # multivariate negative control / coverage-only predictive power
    results = []
    top_feats = assoc.groupby("feature")["auc_absdir"].max().sort_values(ascending=False).head(80).index.tolist() if len(assoc) else feats[:80]
    for t in LABELS:
        for name, opts in [
            ("coverage_only", dict(include_subject=False, shuffle_y=False, shift_features=False)),
            ("coverage_plus_subject", dict(include_subject=True, shuffle_y=False, shift_features=False)),
            ("subject_label_shuffle", dict(include_subject=True, shuffle_y=True, shift_features=False)),
            ("feature_shift_plus_subject", dict(include_subject=True, shuffle_y=False, shift_features=True)),
        ]:
            r = cv_logistic_eval(d[d.split == "train"], top_feats, t, **opts)
            if r:
                r["control"] = name; results.append(r)
    pd.DataFrame(results).to_csv(EXP / "observation_negative_control_coverage_results.csv", index=False)
    return d, feats


def hourly_time_window_signatures(train, hourly):
    rows = []
    hwide = hourly.pivot_table(index=["subject_id", "date", "hour"], columns="modality", values="record_n", aggfunc="sum", fill_value=0).reset_index()
    # windows relative to lifelog date. offset=0 is same lifelog date, -1 previous day, +1 next day.
    for offset in [-1, 0, 1]:
        tmp = train[["subject_id", "lifelog_date"] + LABELS].copy()
        tmp["date"] = (tmp["lifelog_date"] + pd.to_timedelta(offset, unit="D")).dt.date.astype(str)
        merged = hwide.merge(tmp, on=["subject_id", "date"], how="inner")
        for mod in MODALITY_FILES:
            if mod not in merged.columns: continue
            for hour in range(24):
                mh = merged[merged.hour == hour]
                if len(mh) < 20: continue
                for t in LABELS:
                    if mh[t].nunique() < 2: continue
                    x = mh[mod].astype(float); y = mh[t].astype(int)
                    try: auc = roc_auc_score(y, x); auc_abs = max(auc, 1-auc)
                    except Exception: auc = auc_abs = np.nan
                    rows.append({"target": t, "modality": mod, "offset_day": offset, "hour": hour, "auc_absdir": auc_abs,
                                 "mean_pos": float(x[y==1].mean()), "mean_neg": float(x[y==0].mean()),
                                 "diff_pos_minus_neg": float(x[y==1].mean()-x[y==0].mean()), "n": len(mh)})
    sig = pd.DataFrame(rows)
    sig.to_csv(EXP / "observation_hourly_signature_by_target.csv", index=False)
    if len(sig):
        win = sig.assign(window=lambda x: pd.cut(x.hour, [-1,5,11,17,21,23], labels=["night00_05","morning06_11","day12_17","evening18_21","late22_23"]))
        rank = win.groupby(["target","modality","offset_day","window"], observed=True).agg(
            mean_auc_absdir=("auc_absdir","mean"), max_auc_absdir=("auc_absdir","max"),
            mean_abs_diff=("diff_pos_minus_neg", lambda s: float(np.nanmean(np.abs(s))))
        ).reset_index().sort_values(["target","max_auc_absdir"], ascending=[True, False])
        rank.to_csv(EXP / "observation_window_signal_ranking.csv", index=False)
        return sig, rank
    return sig, pd.DataFrame()


def token_key(prefix, token):
    if token is None or (isinstance(token, float) and np.isnan(token)):
        return None
    return f"{prefix}:{str(token).strip()}"


def build_identity_features(all_rows, max_tokens_per_mod=300):
    target_keys = all_rows[["subject_id", "date", "split"]].drop_duplicates()
    token_counts = defaultdict(Counter)
    # wifi bssid
    for mod, col, fields in [("wifi", "m_wifi", ["bssid"]), ("ble", "m_ble", ["address", "device_class"]), ("usage", "m_usage_stats", ["app_name"]), ("ambience", "m_ambience", ["label0"] )]:
        df = read_raw(mod)
        main = [c for c in df.columns if c not in {"subject_id","timestamp","date","hour"}][0]
        for _, r in df.iterrows():
            key = (r.subject_id, r.date)
            recs = flatten_records(r[main])
            for rec in recs:
                if mod == "ambience":
                    if isinstance(rec, (list, tuple)) and rec:
                        tok = token_key("amb", rec[0])
                        if tok: token_counts[key][tok] += 1
                elif isinstance(rec, dict):
                    for f in fields:
                        tok = token_key(f"{mod}_{f}", rec.get(f))
                        if tok: token_counts[key][tok] += 1
    # restrict vocab by global freq, preserving interpretable tokens
    global_counts = Counter()
    for c in token_counts.values(): global_counts.update(c)
    vocab = {tok for tok, _ in global_counts.most_common(max_tokens_per_mod * 4)}
    dicts = []
    keys = []
    for _, r in target_keys.iterrows():
        key = (r.subject_id, r.date)
        keys.append(key)
        dicts.append({k: v for k, v in token_counts.get(key, {}).items() if k in vocab})
    vec = DictVectorizer(sparse=True)
    X = vec.fit_transform(dicts)
    feat_names = np.array(vec.get_feature_names_out())
    # save compact daily sparse as dense enough (700 rows x ~1200 max)
    dense = pd.DataFrame(X.toarray(), columns=feat_names)
    dense.insert(0, "date", [k[1] for k in keys])
    dense.insert(0, "subject_id", [k[0] for k in keys])
    dense.to_parquet(FEAT / "observation_identity_token_features.parquet", index=False)
    return dense, feat_names.tolist()


def identity_associations(train, identity):
    tr = train.copy(); tr["date"] = tr["lifelog_date"].dt.date.astype(str)
    d = tr.merge(identity, on=["subject_id", "date"], how="left").fillna(0)
    feats = [c for c in identity.columns if c not in ["subject_id", "date"]]
    rows = []
    for t in LABELS + (["latent_state"] if "latent_state" in d.columns else []):
        if t == "latent_state":
            # MI for multiclass states
            mask = d[t].notna(); y = d.loc[mask, t].astype(int)
            if y.nunique() < 2: continue
            # prefilter by token presence count
            cand = [f for f in feats if d.loc[mask, f].sum() >= 3]
            X = d.loc[mask, cand].astype(float)
            if len(cand) == 0: continue
            mi = mutual_info_classif(X, y, discrete_features=True, random_state=0)
            for f, m in sorted(zip(cand, mi), key=lambda z: z[1], reverse=True)[:300]:
                rows.append({"target": t, "token": f, "score_type": "mutual_info", "score": float(m), "presence_days": int((X[f] > 0).sum())})
        else:
            mask = d[t].notna(); y = d.loc[mask, t].astype(int)
            if y.nunique() < 2: continue
            for f in feats:
                present = (d.loc[mask, f] > 0).astype(int)
                if present.sum() < 3 or present.nunique() < 2: continue
                tab = pd.crosstab(present, y)
                if tab.shape != (2,2): continue
                try:
                    chi2, p, _, _ = chi2_contingency(tab + 0.5)
                    rate_present = y[present == 1].mean(); rate_absent = y[present == 0].mean()
                    lift = rate_present - rate_absent
                except Exception: continue
                rows.append({"target": t, "token": f, "score_type": "chi2", "score": float(chi2), "p_value": float(p),
                             "presence_days": int(present.sum()), "rate_present": float(rate_present), "rate_absent": float(rate_absent),
                             "lift_present_minus_absent": float(lift)})
    out = pd.DataFrame(rows).sort_values(["target","score"], ascending=[True, False])
    out.to_csv(EXP / "observation_identity_token_association.csv", index=False)
    return out


def subject_label_language(train):
    rows = []
    for sid, g in train.sort_values("lifelog_date").groupby("subject_id"):
        for t in LABELS:
            y = g[t].astype(int).to_numpy()
            rows.append({"subject_id": sid, "metric": "prevalence", "target": t, "value": float(y.mean()), "n": len(y)})
            if len(y) > 1:
                rows.append({"subject_id": sid, "metric": "lag1_agreement", "target": t, "value": float((y[1:] == y[:-1]).mean()), "n": len(y)-1})
                if len(np.unique(y[:-1])) > 1:
                    try: rows.append({"subject_id": sid, "metric": "lag1_auc", "target": t, "value": float(roc_auc_score(y[1:], y[:-1])), "n": len(y)-1})
                    except Exception: pass
        for i,a in enumerate(LABELS):
            for b in LABELS[i+1:]:
                if g[a].nunique() > 1 and g[b].nunique() > 1:
                    corr = g[[a,b]].corr().iloc[0,1]
                    rows.append({"subject_id": sid, "metric": "pair_corr", "target": f"{a}-{b}", "value": float(corr), "n": len(g)})
        # rare/contradictory patterns
        rare_defs = {
            "S2_0_S3orS4_1": ((g.S2 == 0) & ((g.S3 == 1) | (g.S4 == 1))).mean(),
            "Q2_Q3_conflict": (g.Q2 != g.Q3).mean(),
            "S1_1_S2_0_S3_1": ((g.S1 == 1) & (g.S2 == 0) & (g.S3 == 1)).mean(),
        }
        for k,v in rare_defs.items(): rows.append({"subject_id": sid, "metric": "contradiction_rate", "target": k, "value": float(v), "n": len(g)})
    out = pd.DataFrame(rows)
    out.to_csv(EXP / "observation_subject_label_language.csv", index=False)
    # transition singleton anomalies
    anom = []
    for sid, g in train.sort_values("lifelog_date").groupby("subject_id"):
        for t in LABELS:
            vals = g[t].astype(int).to_numpy(); dates = g["lifelog_date"].dt.date.astype(str).to_list()
            for i in range(1, len(vals)-1):
                if vals[i-1] == vals[i+1] and vals[i] != vals[i-1]:
                    anom.append({"subject_id": sid, "lifelog_date": dates[i], "target": t, "prev": int(vals[i-1]), "cur": int(vals[i]), "next": int(vals[i+1])})
    pd.DataFrame(anom).to_csv(EXP / "observation_singleton_label_anomalies.csv", index=False)
    return out


def write_report(files):
    def top_csv(path, n=8, sort_col=None):
        p = EXP / path
        if not p.exists(): return "(missing)"
        df = pd.read_csv(p)
        if sort_col and sort_col in df.columns:
            df = df.sort_values(sort_col, ascending=False)
        return '```\n' + df.head(n).to_string(index=False) + '\n```'
    report = f"""# Observation-process deep diagnostics

This is a no-submission data-science audit. It asks whether the labels are driven by behavior, sensor observability, temporal alignment, raw identity/context, or subject-specific label language.

## Files produced

{chr(10).join('- `' + f + '`' for f in files)}

## 1. Sensor coverage / missingness

Top univariate coverage-label associations by direction-free AUC:

{top_csv('observation_coverage_label_association.csv', 12, 'auc_absdir')}

Top train/test coverage shifts:

{top_csv('observation_coverage_train_test_shift.csv', 12, 'auc_absdir')}

## 2. Coverage-only negative controls

If shuffled/shifted/subject-augmented controls stay strong, the signal is not clean day-level behavior.

{top_csv('observation_negative_control_coverage_results.csv', 20, 'logloss_improvement')}

## 3. Time-window / alignment signatures

Best target-window-modality signals:

{top_csv('observation_window_signal_ranking.csv', 20, 'max_auc_absdir')}

## 4. Raw identity/context tokens

Strongest token-label/state associations:

{top_csv('observation_identity_token_association.csv', 25, 'score')}

## 5. Subject-specific label language

Subject-level prevalence, pair-correlation, persistence, and contradiction rates are in `observation_subject_label_language.csv`; singleton temporal anomalies are in `observation_singleton_label_anomalies.csv`.

## Interpretation checklist

- Coverage/missingness with AUC > ~0.65 means the target/state partly reflects sensor availability or device wearing/phone availability, not only behavior values.
- Train/test coverage AUC > ~0.65 means hidden rows are not a purely random hole under the observed sensor process.
- Shifted-feature or subject-shuffled controls close to real performance indicate static subject/context artifacts.
- Offset/window asymmetry indicates which calendar date actually matches the self-report label; weak asymmetry means the signal is broad subject routine rather than precise sleep-night behavior.
- Identity tokens with large lift are context fingerprints; useful for interpretation, but dangerous for public/private generalization if they mostly encode subject/place.
"""
    (EXP / "observation_process_deep_diagnostics_report.md").write_text(report)


def main():
    train, sample, all_rows = load_base()
    files = []
    cov, hourly = build_coverage(all_rows); files += ["features/observation_coverage_features.parquet", "experiments/observation_hourly_coverage_long.csv"]
    merged, cov_feats = coverage_associations(train, sample, cov); files += [
        "experiments/observation_coverage_label_association.csv", "experiments/observation_coverage_state_association.csv",
        "experiments/observation_coverage_train_test_shift.csv", "experiments/observation_negative_control_coverage_results.csv"]
    hourly_time_window_signatures(train, hourly); files += ["experiments/observation_hourly_signature_by_target.csv", "experiments/observation_window_signal_ranking.csv"]
    identity, _ = build_identity_features(all_rows); files += ["features/observation_identity_token_features.parquet"]
    identity_associations(train, identity); files += ["experiments/observation_identity_token_association.csv"]
    subject_label_language(train); files += ["experiments/observation_subject_label_language.csv", "experiments/observation_singleton_label_anomalies.csv"]
    write_report(files); files += ["experiments/observation_process_deep_diagnostics_report.md"]
    print(json.dumps({"ok": True, "files": files}, indent=2))

if __name__ == "__main__":
    main()
