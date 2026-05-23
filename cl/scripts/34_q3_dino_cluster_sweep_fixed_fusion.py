#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score, balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')

TARGET='Q3'

def folds():
    return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

def valid_cols(df, cols):
    out=[]
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1:
            out.append(c)
    return out

def sleep_cols(all_cols):
    return [c for c in all_cols if any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_')) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','dyncl_')) and '__dev_' not in c and '__prev_' not in c]

def make_clusters(emb, cols, k):
    x=emb[cols].to_numpy(dtype=float)
    x=SimpleImputer(strategy='median').fit_transform(x)
    x=StandardScaler().fit_transform(x)
    km=KMeans(n_clusters=k, random_state=42, n_init=50)
    cid=km.fit_predict(x); dist=km.transform(x)
    out=emb[['subject_id','lifelog_date']].copy()
    out[f'dyncl_dino_k{k}_cluster']=cid
    for j in range(k):
        out[f'dyncl_dino_k{k}_is{j}']=(cid==j).astype(float)
        out[f'dyncl_dino_k{k}_dist{j}']=dist[:,j]
    out[f'dyncl_dino_k{k}_mindist']=dist.min(axis=1)
    return out

def eval_pipe(df, cols, target=TARGET, mode='robust'):
    rows=[]
    for fold in folds():
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()
        ytr=df.loc[~mask,target].astype(int).to_numpy(); yva=df.loc[mask,target].astype(int).to_numpy()
        best=None
        for C in [0.0003,0.001,0.003,0.01,0.03,0.1,0.3,1.0]:
            scaler=RobustScaler() if mode=='robust' else StandardScaler()
            pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('scale',scaler),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])
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
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    emb=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_hourly_dino_temporal_embeddings.parquet'}')").df()
    emb['lifelog_date']=emb['lifelog_date'].astype(str)
    dcols=[c for c in emb.columns if c.startswith('ssl_dino_temporal_')]
    all_cluster_tables=[]; result_rows=[]; subject_rows=[]
    base=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in base.columns if c not in {'subject_id','sleep_date','lifelog_date','Q1','Q2','Q3','S1','S2','S3','S4'}]
    sleep=valid_cols(base,sleep_cols(all_cols))
    for k in range(3,11):
        cf=make_clusters(emb,dcols,k)
        all_cluster_tables.append(cf)
        df=base.merge(cf,on=['subject_id','lifelog_date'],how='left')
        clcols=[c for c in cf.columns if c not in {'subject_id','lifelog_date'}]
        configs={
            f'dino_k{k}_cluster_only':clcols,
            f'sleep_plus_dino_k{k}_fixed_all':sleep+clcols,
        }
        for name, cols in configs.items():
            rows=eval_pipe(df,cols)
            result_rows.append({'config':name,'k':k,'n_cols':len(cols),'avg_logloss':float(np.mean([r['logloss'] for r in rows])),'avg_auc':float(np.nanmean([r['auc'] for r in rows])),'avg_acc':float(np.mean([r['acc'] for r in rows])),**{r['fold_id']:r['logloss'] for r in rows},'best_Cs':json.dumps({r['fold_id']:r['C'] for r in rows})})
        # subject identity diagnostic from cluster features only
        sdf=train[['subject_id','lifelog_date']].merge(cf,on=['subject_id','lifelog_date'],how='left')
        rows=[]
        for fold in folds():
            valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
            mask=sdf.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()
            pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler()),('clf',LogisticRegression(C=0.1,solver='lbfgs',max_iter=1000,random_state=42))])
            pipe.fit(sdf.loc[~mask,clcols],sdf.loc[~mask,'subject_id'])
            pred=pipe.predict(sdf.loc[mask,clcols])
            rows.append(balanced_accuracy_score(sdf.loc[mask,'subject_id'],pred))
        subject_rows.append({'k':k,'cluster_subject_bal_acc':float(np.mean(rows))})
    res=pd.DataFrame(result_rows).sort_values('avg_logloss')
    subj=pd.DataFrame(subject_rows)
    merged=all_cluster_tables[0]
    for t in all_cluster_tables[1:]: merged=merged.merge(t,on=['subject_id','lifelog_date'],how='outer')
    merged.to_parquet(FEATURE_DIR/'ssl_dino_cluster_sweep_features.parquet',index=False)
    res.to_csv(EXPERIMENT_DIR/'probe_q3_dino_cluster_sweep_fusion.csv',index=False)
    subj.to_csv(EXPERIMENT_DIR/'probe_q3_dino_cluster_subject_diagnostic.csv',index=False)
    print('wrote', FEATURE_DIR/'ssl_dino_cluster_sweep_features.parquet')
    print('wrote', EXPERIMENT_DIR/'probe_q3_dino_cluster_sweep_fusion.csv')
    print('wrote', EXPERIMENT_DIR/'probe_q3_dino_cluster_subject_diagnostic.csv')
    print('\nBEST Q3 configs')
    print(res.head(20).to_string(index=False))
    print('\nSubject diagnostic')
    print(subj.to_string(index=False))

if __name__=='__main__': main()
