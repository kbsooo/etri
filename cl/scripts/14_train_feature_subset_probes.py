#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs


def load_folds():
    return json.loads((OUT_DIR / "validation" / "folds_chrono.json").read_text())["folds"]


def valid_numeric_cols(df: pd.DataFrame, cols: list[str]) -> list[str]:
    out=[]
    for c in cols:
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum() == 0:
            continue
        if s.nunique(dropna=True) <= 1:
            continue
        out.append(c)
    return out


def subset_cols(all_cols: list[str], name: str) -> list[str]:
    if name == "all":
        return all_cols
    if name == "no_flat_hourly":
        return [c for c in all_cols if not re.match(r"h\d{2}_", c)]
    if name == "raw_no_subj_norm":
        return [c for c in all_cols if "__subj_" not in c]
    if name == "subj_norm_only":
        return [c for c in all_cols if "__subj_" in c]
    if name == "sleep_semantic_behavior_no_flat":
        keys=("sleep", "state_", "night_", "hr_", "gps_", "app_", "wifi_", "ble_", "amb_", "late_", "dark_", "bright_", "quiet_", "screenoff_")
        return [c for c in all_cols if (not re.match(r"h\d{2}_", c)) and any(k in c for k in keys)]
    if name == "sleep_only":
        keys=("sleep", "late_", "dark_", "bright_", "quiet_", "screenoff_")
        return [c for c in all_cols if any(k in c for k in keys)]
    if name == "semantic_only":
        keys=("hr_", "gps_", "app_", "wifi_", "ble_", "amb_")
        return [c for c in all_cols if any(k in c for k in keys)]
    if name == "daily_windows_only":
        keys=("screen_", "steps_", "distance_", "light_", "activity_", "charge_")
        return [c for c in all_cols if (not re.match(r"h\d{2}_", c)) and any(k in c for k in keys)]
    raise ValueError(name)


def evaluate(df, feature_cols, subset_name, k, C):
    rows=[]
    folds=load_folds()
    for fold in folds:
        valid_set={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
        is_valid=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid_set, axis=1).to_numpy()
        xtr=df.loc[~is_valid, feature_cols]
        xva=df.loc[is_valid, feature_cols]
        scores={}
        for y in LABELS:
            ytr=df.loc[~is_valid,y].astype(int).to_numpy()
            yva=df.loc[is_valid,y].astype(int).to_numpy()
            pipe=Pipeline([
                ('imp', SimpleImputer(strategy='median')),
                ('select', SelectKBest(f_classif, k=min(k, len(feature_cols)))),
                ('scale', RobustScaler()),
                ('clf', LogisticRegression(C=C, solver='liblinear', max_iter=1000)),
            ])
            try:
                pipe.fit(xtr, ytr)
                p=pipe.predict_proba(xva)[:,1]
            except Exception:
                p=np.full(len(yva), ytr.mean())
            p=np.clip(p,0.05,0.95)
            scores[y]=log_loss(yva,p,labels=[0,1])
        rows.append({'model':'feature_subset_selectk_logistic','subset':subset_name,'n_features':len(feature_cols),'k':k,'C':C,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{a}':b for a,b in scores.items()}})
    return rows


def main():
    ensure_dirs()
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
    rows=[]
    subsets=['all','no_flat_hourly','raw_no_subj_norm','subj_norm_only','sleep_semantic_behavior_no_flat','sleep_only','semantic_only','daily_windows_only']
    for subset in subsets:
        cols=valid_numeric_cols(df, subset_cols(all_cols, subset))
        if not cols:
            continue
        for k in [10,20,30,50,80,120,200]:
            if k > len(cols) and k != 10:
                continue
            for C in [0.001,0.003,0.01,0.03,0.1]:
                rows += evaluate(df, cols, subset, k, C)
    res=pd.DataFrame(rows).sort_values('mean_logloss')
    out=EXPERIMENT_DIR/'probe_feature_subset_selectk_results.csv'
    res.to_csv(out,index=False)
    best=res.iloc[0].to_dict()
    (EXPERIMENT_DIR/'probe_feature_subset_selectk_best.json').write_text(json.dumps(best,ensure_ascii=False,indent=2),encoding='utf-8')
    print('best', best)
    print('wrote', out)

if __name__=='__main__':
    main()
