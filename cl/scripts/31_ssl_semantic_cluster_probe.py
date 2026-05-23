#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, OUT_DIR, ensure_dirs

TARGETS=["Q1","Q3"]

def folds():
    return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

def make_cluster_features(df, cols, prefix, k):
    x=df[cols].to_numpy(dtype=float)
    x=SimpleImputer(strategy='median').fit_transform(x)
    x=StandardScaler().fit_transform(x)
    km=KMeans(n_clusters=k, random_state=42, n_init=30)
    cid=km.fit_predict(x)
    dist=km.transform(x)
    out=df[['subject_id','lifelog_date']].copy()
    out[f'{prefix}_k{k}_cluster']=cid
    for j in range(k):
        out[f'{prefix}_k{k}_is{j}']=(cid==j).astype(float)
        out[f'{prefix}_k{k}_dist{j}']=dist[:,j]
    out[f'{prefix}_k{k}_mindist']=dist.min(axis=1)
    out[f'{prefix}_k{k}_entropy_proxy']=-(np.exp(-dist)/(np.exp(-dist).sum(axis=1,keepdims=True)+1e-9)*np.log(np.exp(-dist)/(np.exp(-dist).sum(axis=1,keepdims=True)+1e-9)+1e-9)).sum(axis=1)
    return out

def eval_cols(df, cols, target):
    rows=[]
    for fold in folds():
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()
        ytr=df.loc[~mask,target].astype(int).to_numpy(); yva=df.loc[mask,target].astype(int).to_numpy()
        best=None
        for C in [0.001,0.003,0.01,0.03,0.1,0.3,1.0]:
            pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])
            pipe.fit(df.loc[~mask,cols],ytr)
            p=np.clip(pipe.predict_proba(df.loc[mask,cols])[:,1],0.05,0.95)
            loss=log_loss(yva,p,labels=[0,1])
            if best is None or loss<best[0]: best=(loss,C,p)
        try: auc=roc_auc_score(yva,best[2])
        except Exception: auc=np.nan
        rows.append({'fold_id':fold['fold_id'],'logloss':best[0],'C':best[1],'auc':auc,'acc':accuracy_score(yva,best[2]>=0.5)})
    return rows

def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    ae=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_hourly_masked_ae_embeddings.parquet'}')").df()
    di=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_hourly_dino_temporal_embeddings.parquet'}')").df()
    emb=ae.merge(di,on=['subject_id','lifelog_date'],how='inner')
    methods={
        'masked_ae':[c for c in emb.columns if c.startswith('ssl_masked_ae_')],
        'dino_temporal':[c for c in emb.columns if c.startswith('ssl_dino_temporal_')],
        'both':[c for c in emb.columns if c.startswith('ssl_masked_ae_') or c.startswith('ssl_dino_temporal_')],
    }
    cluster_tables=[]; result_rows=[]
    for name, cols in methods.items():
        for k in [4,6,8,12]:
            cf=make_cluster_features(emb,cols,f'sslcl_{name}',k)
            cluster_tables.append(cf)
            df=train.merge(cf,on=['subject_id','lifelog_date'],how='left')
            feat_cols=[c for c in cf.columns if c not in {'subject_id','lifelog_date'}]
            for target in TARGETS:
                rows=eval_cols(df,feat_cols,target)
                result_rows.append({'method':name,'k':k,'target':target,'avg_logloss':float(np.mean([r['logloss'] for r in rows])),'avg_auc':float(np.nanmean([r['auc'] for r in rows])),'avg_acc':float(np.mean([r['acc'] for r in rows])),**{r['fold_id']:r['logloss'] for r in rows}})
    # merge all cluster features for reuse
    merged=cluster_tables[0]
    for t in cluster_tables[1:]:
        merged=merged.merge(t,on=['subject_id','lifelog_date'],how='outer')
    merged.to_parquet(FEATURE_DIR/'ssl_semantic_cluster_features.parquet',index=False)
    res=pd.DataFrame(result_rows).sort_values(['target','avg_logloss'])
    res.to_csv(EXPERIMENT_DIR/'probe_ssl_semantic_cluster_q_results.csv',index=False)
    print('wrote', FEATURE_DIR/'ssl_semantic_cluster_features.parquet')
    print('wrote', EXPERIMENT_DIR/'probe_ssl_semantic_cluster_q_results.csv')
    for target in TARGETS:
        print('\nBEST',target)
        print(res[res.target==target].head(10).to_string(index=False))

if __name__=='__main__': main()
