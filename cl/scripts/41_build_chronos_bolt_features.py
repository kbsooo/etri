#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd, torch
from chronos import ChronosBoltPipeline

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ensure_dirs

CHANNELS=['screen_use_sum_h','steps_sum_h','distance_sum_h','mlight_mean_h','wlight_mean_h','activity_mean_h','screen_n_h','pedo_n_h','activity_n_h']

def main():
    ensure_dirs(); con=duckdb.connect()
    tb=con.execute(f"select * from read_parquet('{FEATURE_DIR/'timebin_1h_features.parquet'}')").df()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv'); test=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')
    keys=pd.concat([train[['subject_id','lifelog_date']],test[['subject_id','lifelog_date']]],ignore_index=True).drop_duplicates().sort_values(['subject_id','lifelog_date']).reset_index(drop=True)
    keys['lifelog_date']=keys['lifelog_date'].astype(str)
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
            if pd.notna(v): X[i,h,j]=float(v); Obs[i,h,j]=1
    # daily channel summaries: log total for count/sum channels, mean for sensor means.
    D={}
    for j,c in enumerate(CHANNELS):
        if c.endswith('_mean_h'):
            val=np.divide((X[:,:,j]*Obs[:,:,j]).sum(axis=1), np.maximum(Obs[:,:,j].sum(axis=1),1))
        else:
            val=X[:,:,j].sum(axis=1)
        D[c]=np.log1p(np.maximum(val,0))
    feat=keys.copy()
    pipe=ChronosBoltPipeline.from_pretrained('amazon/chronos-bolt-tiny', device_map='cpu')
    min_hist=7; max_hist=32
    for c,series in D.items():
        rows=[]; contexts=[]; meta=[]
        for sid in keys.subject_id.unique():
            inds=np.where(keys.subject_id.to_numpy()==sid)[0]
            inds=inds[np.argsort(keys.loc[inds,'lifelog_date'].to_numpy())]
            vals=series[inds]
            for pos,i in enumerate(inds):
                if pos < min_hist:
                    continue
                hist=vals[max(0,pos-max_hist):pos]
                if len(hist) >= min_hist:
                    contexts.append(torch.tensor(hist,dtype=torch.float32))
                    meta.append((i, vals[pos]))
        preds={}
        if contexts:
            # pad variable contexts manually with NaN left padding; chronos accepts list/tensor-like contexts.
            batch_size=128
            for start in range(0,len(contexts),batch_size):
                ctx=contexts[start:start+batch_size]
                q, mean = pipe.predict_quantiles(ctx, prediction_length=1, quantile_levels=[0.1,0.5,0.9])
                q=q.detach().cpu().numpy()[:,0,:]; mean=mean.detach().cpu().numpy()[:,0]
                for n,(i,actual) in enumerate(meta[start:start+batch_size]):
                    preds[i]=(actual, mean[n], q[n,0], q[n,1], q[n,2])
        base=c.replace('_h','').replace('_sum','').replace('_mean','')
        for i in range(len(keys)):
            if i in preds:
                actual, mean, q10, q50, q90=preds[i]
                resid=actual-q50
                feat.loc[i,f'ext_chronos_{base}_actual_log']=actual
                feat.loc[i,f'ext_chronos_{base}_pred_mean']=mean
                feat.loc[i,f'ext_chronos_{base}_pred_q50']=q50
                feat.loc[i,f'ext_chronos_{base}_resid']=resid
                feat.loc[i,f'ext_chronos_{base}_abs_resid']=abs(resid)
                feat.loc[i,f'ext_chronos_{base}_interval_width']=q90-q10
                feat.loc[i,f'ext_chronos_{base}_below_q10']=float(actual<q10)
                feat.loc[i,f'ext_chronos_{base}_above_q90']=float(actual>q90)
            else:
                for suffix in ['actual_log','pred_mean','pred_q50','resid','abs_resid','interval_width','below_q10','above_q90']:
                    feat.loc[i,f'ext_chronos_{base}_{suffix}']=np.nan
        print('chronos channel done', c, len(preds))
    num=[c for c in feat.columns if c.startswith('ext_chronos_')]
    feat['ext_chronos_total_abs_resid']=feat[[c for c in num if c.endswith('_abs_resid')]].sum(axis=1, min_count=1)
    feat['ext_chronos_total_interval_width']=feat[[c for c in num if c.endswith('_interval_width')]].sum(axis=1, min_count=1)
    feat.to_parquet(FEATURE_DIR/'external_chronos_bolt_features_v1.parquet',index=False)
    print('wrote', FEATURE_DIR/'external_chronos_bolt_features_v1.parquet', feat.shape)
    print(feat.head(12).to_string(index=False))

if __name__=='__main__': main()
