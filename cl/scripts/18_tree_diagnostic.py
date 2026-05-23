#!/usr/bin/env python3
from __future__ import annotations

import json, sys, re
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs


def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

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
    subsets={
      'semantic_v1':[c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and '__' not in c and not c.startswith('h')],
      'noflat_no_routine':[c for c in all_cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c],
      'sleep':[c for c in all_cols if any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_')) and '__dev_' not in c and '__prev_' not in c],
    }
    rows=[]
    models=[]
    for n in [100,300]:
        models.append((f'extratrees{n}', ExtraTreesClassifier(n_estimators=n, max_depth=None, min_samples_leaf=5, max_features='sqrt', random_state=42, n_jobs=-1)))
        models.append((f'rf{n}', RandomForestClassifier(n_estimators=n, max_depth=4, min_samples_leaf=8, max_features='sqrt', random_state=42, n_jobs=-1)))
    for subset, rawcols in subsets.items():
        cols=valid_cols(df, rawcols)
        for k in [20,50,100,200,500]:
          if k>len(cols): continue
          for mname, model in models:
            for fold in folds():
              valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
              mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid,axis=1).to_numpy()
              Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
              scores={}
              for y in LABELS:
                ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
                pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,len(cols)))),('clf',model)])
                try:
                  pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xva)[:,1]
                except Exception:
                  p=np.full(len(yva),ytr.mean())
                p=np.clip(p,0.05,0.95)
                scores[y]=log_loss(yva,p,labels=[0,1])
              rows.append({'model':mname,'subset':subset,'n_features':len(cols),'k':k,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{a}':b for a,b in scores.items()}})
    res=pd.DataFrame(rows).sort_values('mean_logloss')
    out=EXPERIMENT_DIR/'probe_tree_diagnostic_results.csv'; res.to_csv(out,index=False)
    print(res.head(10).to_string(index=False))
    print('avg best'); print(res.groupby(['model','subset','k'])['mean_logloss'].mean().reset_index().sort_values('mean_logloss').head(10).to_string(index=False))
    print('wrote',out)

if __name__=='__main__': main()
