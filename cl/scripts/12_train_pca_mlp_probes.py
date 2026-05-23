#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs


def folds():
    return json.loads((OUT_DIR / "validation" / "folds_chrono.json").read_text())["folds"]


def eval_model(pipe_factory, name):
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
    fcols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
    rows=[]
    for fold in folds():
        valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid,axis=1).to_numpy()
        xtr=df.loc[~mask,fcols]; xva=df.loc[mask,fcols]
        scores={}
        for y in LABELS:
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            pipe=pipe_factory()
            try:
                pipe.fit(xtr,ytr)
                p=pipe.predict_proba(xva)[:,1]
            except Exception:
                p=np.full(len(yva), ytr.mean())
            p=np.clip(p,0.05,0.95)
            scores[y]=log_loss(yva,p,labels=[0,1])
        rows.append({'model':name,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{k}':v for k,v in scores.items()}})
    return rows


def main():
    ensure_dirs()
    all_rows=[]
    for ncomp in [8,16,32,64]:
        def factory(ncomp=ncomp):
            return Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler()),('pca',PCA(n_components=ncomp, random_state=42)),('clf',LogisticRegression(C=0.03,solver='liblinear',max_iter=1000))])
        rows=eval_model(factory, f'pca{ncomp}_logistic')
        for r in rows: r['n_components']=ncomp
        all_rows+=rows
    for hidden in [(8,), (16,), (16,8), (32,16)]:
        def factory(hidden=hidden):
            return Pipeline([('imp',SimpleImputer(strategy='median')),('scale',RobustScaler()),('clf',MLPClassifier(hidden_layer_sizes=hidden, alpha=0.1, learning_rate_init=0.001, max_iter=500, early_stopping=True, random_state=42))])
        rows=eval_model(factory, f'mlp_{hidden}')
        for r in rows: r['hidden']=str(hidden)
        all_rows+=rows
    res=pd.DataFrame(all_rows).sort_values('mean_logloss')
    out=EXPERIMENT_DIR/'probe_pca_mlp_results.csv'
    res.to_csv(out,index=False)
    best=res.iloc[0].to_dict()
    (EXPERIMENT_DIR/'probe_pca_mlp_best.json').write_text(json.dumps(best,ensure_ascii=False,indent=2),encoding='utf-8')
    print('best',best)
    print('wrote',out)

if __name__=='__main__': main()
