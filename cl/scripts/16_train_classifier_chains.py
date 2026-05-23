#!/usr/bin/env python3
from __future__ import annotations

import json, re, sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.multioutput import ClassifierChain
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs


def load_folds():
    return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']


def valid_cols(df, cols):
    out=[]
    for c in cols:
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1:
            out.append(c)
    return out


def subset_cols(cols, subset):
    if subset=='semantic_v1_only':
        keys=('hr_','gps_','app_','wifi_','ble_','amb_')
        return [c for c in cols if any(k in c for k in keys) and '__' not in c and not c.startswith('h')]
    if subset=='semantic_all':
        keys=('hr_','gps_','app_','wifi_','ble_','amb_')
        return [c for c in cols if any(k in c for k in keys) and not c.startswith('h')]
    if subset=='sleep_no_routine':
        keys=('sleep','quiet_','screenoff_','late_','dark_','bright_')
        return [c for c in cols if any(k in c for k in keys) and '__dev_' not in c and '__prev_' not in c]
    if subset=='no_flat_no_routine':
        return [c for c in cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    return cols


def main():
    ensure_dirs()
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
    orders={
        'default': list(range(7)),
        'q_then_s_corr': [1,2,0,3,4,6,5],
        's_then_q': [3,4,6,5,0,1,2],
        'corr_blocks': [1,2,3,4,6,5,0],
    }
    rows=[]
    for subset in ['semantic_v1_only','semantic_all','sleep_no_routine','no_flat_no_routine']:
        cols=valid_cols(df, subset_cols(all_cols, subset))
        for k in [20,50,100,200]:
            if k>len(cols): continue
            for C in [0.003,0.01,0.03,0.1]:
                for order_name, order in orders.items():
                    for fold in load_folds():
                        valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
                        mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1).to_numpy()
                        Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
                        Ytr=df.loc[~mask,LABELS].astype(int).to_numpy(); Yva=df.loc[mask,LABELS].astype(int).to_numpy()
                        base=LogisticRegression(C=C, solver='liblinear', max_iter=1000)
                        pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('select',SelectKBest(f_classif,k=min(k,len(cols)))),('scale',RobustScaler()),('chain',ClassifierChain(base_estimator=base, order=order, random_state=42))])
                        try:
                            pipe.fit(Xtr,Ytr)
                            P=pipe.predict_proba(Xva)
                            if isinstance(P, list): P=np.vstack([p[:,1] for p in P]).T
                        except Exception as e:
                            P=np.tile(Ytr.mean(axis=0), (len(Yva),1))
                        P=np.clip(P,0.05,0.95)
                        scores={y:log_loss(Yva[:,i],P[:,i],labels=[0,1]) for i,y in enumerate(LABELS)}
                        rows.append({'model':'classifier_chain_logistic','subset':subset,'n_features':len(cols),'k':k,'C':C,'order':order_name,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{a}':b for a,b in scores.items()}})
    res=pd.DataFrame(rows).sort_values('mean_logloss')
    out=EXPERIMENT_DIR/'probe_classifier_chain_results.csv'
    res.to_csv(out,index=False)
    best=res.iloc[0].to_dict()
    (EXPERIMENT_DIR/'probe_classifier_chain_best.json').write_text(json.dumps(best,ensure_ascii=False,indent=2),encoding='utf-8')
    print('best',best)
    g=res.groupby(['subset','k','C','order'])['mean_logloss'].mean().reset_index().sort_values('mean_logloss').head(10)
    print(g.to_string(index=False))
    print('wrote',out)

if __name__=='__main__': main()
