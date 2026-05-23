#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ensure_dirs

CHANNELS=[
    'screen_use_sum_h','steps_sum_h','distance_sum_h','mlight_mean_h','wlight_mean_h',
    'activity_mean_h','screen_n_h','pedo_n_h','mlight_n_h','wlight_n_h','activity_n_h'
]
WINDOWS={'all':list(range(24)),'night':list(range(0,6)),'morning':list(range(6,12)),'day':list(range(12,18)),'evening':list(range(18,24)),'late':[21,22,23],'sleepwin':[21,22,23,0,1,2,3,4,5]}

def main():
    ensure_dirs(); con=duckdb.connect()
    tb=con.execute(f"select * from read_parquet('{FEATURE_DIR/'timebin_1h_features.parquet'}')").df()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv'); test=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')
    keys=pd.concat([train[['subject_id','lifelog_date']],test[['subject_id','lifelog_date']]],ignore_index=True).drop_duplicates().sort_values(['subject_id','lifelog_date']).reset_index(drop=True)
    # Fill a 24h tensor and add observed-mask channels. Public TS foundation model proxies:
    # (1) generic seasonal hour-of-day forecast residual, (2) subject routine residual,
    # (3) PCA latent/prototype over standardized day tokens. These are cheap ablations before
    # heavier Chronos/MOMENT installs.
    idx={(r.subject_id,str(r.lifelog_date)):i for i,r in keys.iterrows()}
    X=np.zeros((len(keys),24,len(CHANNELS)),dtype=float); Obs=np.zeros_like(X)
    for r in tb.itertuples(index=False):
        key=(getattr(r,'subject_id'),str(getattr(r,'lifelog_date')))
        if key not in idx: continue
        h=int(getattr(r,'hour'))
        if not 0<=h<24: continue
        i=idx[key]
        for j,c in enumerate(CHANNELS):
            v=getattr(r,c,np.nan)
            if pd.notna(v): X[i,h,j]=float(v); Obs[i,h,j]=1.0
    # log1p heavy-tailed positive channels except light/activity counts safe too.
    Xlog=np.sign(X)*np.log1p(np.abs(X))
    # Global hour-channel expected value and subject hour-channel expected value (input-only, no labels).
    global_hc=np.nanmean(np.where(Obs>0,Xlog,np.nan),axis=0)
    global_hc=np.nan_to_num(global_hc, nan=0.0)
    subj_hc={}
    for sid in keys.subject_id.unique():
        m=(keys.subject_id==sid).to_numpy(); vals=np.where(Obs[m]>0,Xlog[m],np.nan)
        subj_hc[sid]=np.nan_to_num(np.nanmean(vals,axis=0), nan=0.0)
    rows=[]
    for i,r in keys.iterrows():
        sid=r.subject_id; rec={'subject_id':sid,'lifelog_date':str(r.lifelog_date)}
        G=Xlog[i]-global_hc
        S=Xlog[i]-subj_hc[sid]
        # naive next-hour residual: observed current h minus previous hour value for routine disruption.
        P=Xlog[i]-np.roll(Xlog[i],1,axis=0)
        for name,arr in [('global',G),('subj',S),('diffprev',P)]:
            absarr=np.abs(arr)
            for w,hrs in WINDOWS.items():
                vals=arr[hrs,:]; avals=absarr[hrs,:]
                rec[f'ext_tsfm_{name}_{w}_mae']=float(np.mean(avals))
                rec[f'ext_tsfm_{name}_{w}_rmse']=float(np.sqrt(np.mean(vals*vals)))
                rec[f'ext_tsfm_{name}_{w}_maxabs']=float(np.max(avals))
                for j,c in enumerate(CHANNELS):
                    base=c.replace('_h','').replace('_sum','').replace('_mean','')
                    rec[f'ext_tsfm_{name}_{w}_{base}_mae']=float(np.mean(avals[:,j]))
        # missingness/routine irregularity
        for w,hrs in WINDOWS.items():
            rec[f'ext_tsfm_obs_{w}_coverage']=float(Obs[i,hrs,:].mean())
            rec[f'ext_tsfm_obs_{w}_missing_rate']=float(1-Obs[i,hrs,:].mean())
        rows.append(rec)
    feat=pd.DataFrame(rows)
    # PCA latent + clusters over day residual tensor.
    Z=np.concatenate([Xlog.reshape(len(keys),-1), Obs.reshape(len(keys),-1)],axis=1)
    Z=StandardScaler().fit_transform(Z)
    ncomp=min(24,Z.shape[0]-1,Z.shape[1])
    pca=PCA(n_components=ncomp,random_state=42).fit_transform(Z)
    for j in range(ncomp): feat[f'ext_tsfm_pca_z{j:02d}']=pca[:,j]
    for k in [4,6,8,12]:
        km=KMeans(n_clusters=k,random_state=42,n_init=30).fit(pca[:,:min(12,ncomp)])
        lab=km.labels_; dist=km.transform(pca[:,:min(12,ncomp)])
        feat[f'ext_tsfm_k{k}_cluster']=lab
        feat[f'ext_tsfm_k{k}_mindist']=dist.min(axis=1)
        for c in range(k):
            feat[f'ext_tsfm_k{k}_is{c}']=(lab==c).astype(float)
            feat[f'ext_tsfm_k{k}_dist{c}']=dist[:,c]
    feat.to_parquet(FEATURE_DIR/'external_tsfm_proxy_features_v1.parquet',index=False)
    print('wrote', FEATURE_DIR/'external_tsfm_proxy_features_v1.parquet', feat.shape)
    print(feat.head().to_string(index=False))

if __name__=='__main__': main()
