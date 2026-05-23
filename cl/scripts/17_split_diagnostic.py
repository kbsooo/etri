#!/usr/bin/env python3
from __future__ import annotations

import json, sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, ensure_dirs


def valid_cols(df, cols):
    out=[]
    for c in cols:
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
    return out


def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
    keys=('hr_','gps_','app_','wifi_','ble_','amb_')
    semantic=valid_cols(df,[c for c in all_cols if any(k in c for k in keys) and not c.startswith('h')])
    noflat=valid_cols(df,[c for c in all_cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c])
    rows=[]
    for subset,cols in [('semantic',semantic),('noflat',noflat)]:
      for splitter_name in ['random_kfold','subject_group_holdout']:
        if splitter_name=='random_kfold':
            splits=list(KFold(n_splits=5, shuffle=True, random_state=42).split(df))
        else:
            subs=sorted(df.subject_id.unique())
            splits=[]
            for i in range(5):
                valid_sub=set(subs[i::5])
                va=np.where(df.subject_id.isin(valid_sub))[0]; tr=np.where(~df.subject_id.isin(valid_sub))[0]
                splits.append((tr,va))
        for k in [20,50,100,200]:
          if k>len(cols): continue
          for C in [0.001,0.003,0.01,0.03,0.1]:
            fold_scores=[]; target_scores={y:[] for y in LABELS}
            for tr,va in splits:
                Xtr=df.iloc[tr][cols]; Xva=df.iloc[va][cols]
                scores=[]
                for y in LABELS:
                    ytr=df.iloc[tr][y].astype(int).to_numpy(); yva=df.iloc[va][y].astype(int).to_numpy()
                    pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,len(cols)))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))])
                    try:
                        pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xva)[:,1]
                    except Exception:
                        p=np.full(len(yva), ytr.mean())
                    p=np.clip(p,0.05,0.95)
                    ll=log_loss(yva,p,labels=[0,1]); scores.append(ll); target_scores[y].append(ll)
                fold_scores.append(np.mean(scores))
            rows.append({'model':'split_diagnostic_logistic','splitter':splitter_name,'subset':subset,'k':k,'C':C,'mean_logloss':float(np.mean(fold_scores)),**{f'logloss_{y}':float(np.mean(v)) for y,v in target_scores.items()}})
    res=pd.DataFrame(rows).sort_values('mean_logloss')
    out=EXPERIMENT_DIR/'probe_split_diagnostic_results.csv'; res.to_csv(out,index=False)
    print(res.head(12).to_string(index=False)); print('wrote',out)

if __name__=='__main__': main()
