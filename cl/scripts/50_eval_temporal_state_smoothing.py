#!/usr/bin/env python3
"""Evaluate subject temporal-state smoothing under test-pattern masked validation.

This tests whether Q1/Q2/S4 should be treated as interleaved same-subject state
completion rather than pure future forecasting. It trains the existing base
feature model on masked-known rows, then blends its probabilities with a
same-subject time-decayed label smoother.
"""
from __future__ import annotations
import json, warnings
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

warnings.filterwarnings('ignore')
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT/'data'; FEATURE_DIR=ROOT/'features'; EXPERIMENT_DIR=ROOT/'experiments'; OUT_DIR=ROOT/'outputs'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']
KEYS=['subject_id','lifelog_date']; ID_COLS=['subject_id','sleep_date','lifelog_date']
DROP=set(ID_COLS+LABELS+['is_train'])
BASE_CFG={
    'Q1':('semantic_only',50,0.03),
    'Q2':('day_flat',20,0.01),
    'Q3':('dino_k4_cluster',10,0.30),
    'S1':('no_flat_hourly',20,0.10),
    'S2':('no_flat_hourly',20,0.001),
    'S3':('semantic_only',20,0.01),
    'S4':('sleep_plus_s4x',200,0.003),
}

def valid_cols(df, cols, known_mask):
    out=[]
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df.loc[known_mask,c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1:
            out.append(c)
    return out

def base_subset(all_cols, subset):
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_','q1qual_','q2lr_','s4evt_','cnproto_','q2proto_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_','q1qual_','q2lr_','s4evt_','cnproto_','q2proto_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_','q1qual_','q2lr_','s4evt_','cnproto_','q2proto_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    raise ValueError(subset)

def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def load_all():
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv', parse_dates=['sleep_date','lifelog_date']).assign(is_train=1)
    sample=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv', parse_dates=['sleep_date','lifelog_date']).assign(is_train=0)
    for y in LABELS: sample[y]=np.nan
    df=pd.concat([train,sample],ignore_index=True)
    paths=[
        FEATURE_DIR/'model_features_v0.parquet',
        FEATURE_DIR/'ssl_semantic_cluster_features.parquet',
        FEATURE_DIR/'prior_sleep_window_features_v1.parquet',
        FEATURE_DIR/'prior_sleep_proxy_features_v1.parquet',
        FEATURE_DIR/'public_failure_followup_features_v1.parquet',
    ]
    for p in paths:
        if p.exists():
            feat=con.execute(f"select * from read_parquet('{p}')").df()
            for k in KEYS:
                if k in feat.columns:
                    feat[k]=feat[k].astype(str)
            df[KEYS]=df[KEYS].astype(str)
            dup=[c for c in feat.columns if c in df.columns and c not in KEYS]
            if dup: feat=feat.rename(columns={c:f'{c}__{p.stem}' for c in dup})
            df=df.merge(feat,on=KEYS,how='left')
    df['sleep_date']=pd.to_datetime(df['sleep_date']); df['lifelog_date']=pd.to_datetime(df['lifelog_date'])
    return df

def make_testpattern_mask(train, sample, seed):
    """Hold out train rows whose within-subject rank resembles actual test rows."""
    rng=np.random.default_rng(seed)
    mask=np.zeros(len(train), dtype=bool)
    for sid, sub in train.groupby('subject_id'):
        sub=sub.sort_values('sleep_date')
        tst=sample[sample.subject_id==sid].sort_values('sleep_date')
        n=min(len(sub)-2, max(3, len(tst)))
        # Match real test's tendency: some mid-sequence gaps and many later rows.
        ranks=np.linspace(0,1,len(sub))
        if len(tst):
            all_dates=pd.concat([sub[['sleep_date']],tst[['sleep_date']]]).sort_values('sleep_date').reset_index(drop=True)
            test_pos=all_dates.index[all_dates['sleep_date'].isin(tst['sleep_date'])].to_numpy()
            center=np.median(test_pos/max(1,len(all_dates)-1))
        else:
            center=0.65
        prob=0.35 + np.exp(-0.5*((ranks-center)/0.25)**2) + 0.6*ranks
        prob=prob/prob.sum()
        chosen=rng.choice(sub.index.to_numpy(), size=n, replace=False, p=prob)
        mask[train.index.get_indexer(chosen)] = True
    return mask

def make_tail_mask(train, frac=0.36):
    mask=np.zeros(len(train), dtype=bool)
    for sid, sub in train.groupby('subject_id'):
        chosen=sub.sort_values('sleep_date').tail(max(3, int(round(len(sub)*frac)))).index
        mask[train.index.get_indexer(chosen)] = True
    return mask

def temporal_label_smooth(known, query, target, tau, alpha, use_future):
    out=np.zeros(len(query),float)
    g=float(known[target].mean())
    for sid, qsub in query.groupby('subject_id'):
        k=known[known.subject_id==sid]
        if len(k)==0:
            out[query.index.get_indexer(qsub.index)] = g; continue
        kd=k.sleep_date.values.astype('datetime64[D]').astype(int)
        qd=qsub.sleep_date.values.astype('datetime64[D]').astype(int)
        dist=np.abs(qd[:,None]-kd[None,:]).astype(float)
        if not use_future:
            dist=np.where(kd[None,:] < qd[:,None], dist, np.inf)
        w=np.exp(-dist/tau); w[~np.isfinite(w)]=0
        p=(w @ k[target].values.astype(float) + alpha*g)/(w.sum(axis=1)+alpha)
        out[query.index.get_indexer(qsub.index)] = np.clip(p,0.02,0.98)
    return out

def base_predict_for(df, known_mask, query_mask, target, cols_cache):
    subset,k,C=BASE_CFG[target]
    all_cols=[c for c in df.columns if c not in DROP]
    cache_key=(target, tuple(known_mask.tolist()))
    cols=valid_cols(df, base_subset(all_cols,subset), known_mask)
    pipe=make_pipe(k,C,len(cols))
    pipe.fit(df.loc[known_mask,cols], df.loc[known_mask,target].astype(int).to_numpy())
    return np.clip(pipe.predict_proba(df.loc[query_mask,cols])[:,1],0.02,0.98)

def main():
    EXPERIMENT_DIR.mkdir(exist_ok=True); OUT_DIR.mkdir(exist_ok=True)
    df=load_all()
    train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    # Recreate merged df as train only for validation to keep masks simple.
    rows=[]
    taus=[3,7,14,30]; alphas=[1,5,10]; blend_ws=[0,0.05,0.10,0.20,0.30,0.40]
    masks=[]
    for seed in range(6): masks.append(('testpattern',seed,make_testpattern_mask(train,sample,seed),True))
    masks.append(('tail',0,make_tail_mask(train),False))
    for split,seed,val_mask,use_future in masks:
        known_mask=~val_mask
        known=train.loc[known_mask].copy(); val=train.loc[val_mask].copy()
        for y in LABELS:
            qmask=val_mask
            pbase=base_predict_for(train, known_mask, qmask, y, None)
            ytrue=val[y].astype(int).to_numpy()
            base_loss=log_loss(ytrue,pbase,labels=[0,1])
            for tau in taus:
                for alpha in alphas:
                    ps=temporal_label_smooth(known,val,y,tau,alpha,use_future=use_future)
                    for w in blend_ws:
                        p=np.clip((1-w)*pbase + w*ps,0.02,0.98)
                        rows.append({'split':split,'seed':seed,'target':y,'tau':tau,'alpha':alpha,'w':w,'logloss':log_loss(ytrue,p,labels=[0,1]),'base_logloss':base_loss,'smooth_only_logloss':log_loss(ytrue,ps,labels=[0,1])})
    res=pd.DataFrame(rows)
    res.to_csv(EXPERIMENT_DIR/'temporal_state_smoothing_masked_results.csv',index=False)
    # Select targetwise best by testpattern mean, require not worse than base and tail sanity.
    tp=res[res.split=='testpattern']
    summary=tp.groupby(['target','tau','alpha','w'])[['logloss','base_logloss','smooth_only_logloss']].mean().reset_index()
    best=summary.sort_values(['target','logloss']).groupby('target').head(5)
    print('\n### testpattern best per target')
    print(best.to_string(index=False))
    print('\n### base vs selected best')
    selected=[]
    for y,g in summary.groupby('target'):
        b=float(g[g.w.eq(0)]['logloss'].mean())
        row=g.sort_values('logloss').iloc[0].to_dict()
        row['base_mean']=b; row['delta']=row['logloss']-b
        selected.append(row)
    sel=pd.DataFrame(selected).sort_values('target')
    print(sel[['target','tau','alpha','w','logloss','base_mean','delta','smooth_only_logloss']].to_string(index=False))
    sel.to_csv(EXPERIMENT_DIR/'temporal_state_smoothing_selected.csv',index=False)
    # Build conservative actual test candidate: only apply if delta < -0.003; otherwise base.
    # Train base on all train, smooth test using all train labels with future allowed (all known train labels available).
    sub=sample[ID_COLS].copy().reset_index(drop=True)
    base_sub=sample[ID_COLS].copy().reset_index(drop=True)
    used={}
    for y in LABELS:
        pbase=base_predict_for(pd.concat([train,sample],ignore_index=True), np.r_[np.ones(len(train),dtype=bool), np.zeros(len(sample),dtype=bool)], np.r_[np.zeros(len(train),dtype=bool), np.ones(len(sample),dtype=bool)], y, None)
        chosen=sel[sel.target.eq(y)].iloc[0]
        apply = (chosen['delta'] < -0.003) and (chosen['w'] > 0)
        if apply:
            ps=temporal_label_smooth(train,sample,y,float(chosen.tau),float(chosen.alpha),use_future=True)
            p=np.clip((1-float(chosen.w))*pbase + float(chosen.w)*ps,0.02,0.98)
        else:
            ps=None; p=pbase
        sub[y]=p; base_sub[y]=pbase
        used[y]={'apply_smoothing':bool(apply),'tau':float(chosen.tau),'alpha':float(chosen.alpha),'w':float(chosen.w),'masked_delta':float(chosen.delta)}
    out=OUT_DIR/'submission_temporal_state_smoothing_prob.csv'
    sub.to_csv(out,index=False)
    (EXPERIMENT_DIR/'submission_temporal_state_smoothing_used.json').write_text(json.dumps(used,indent=2),encoding='utf-8')
    # prediction shift vs base
    shifts=[]
    for y in LABELS:
        d=np.abs(sub[y].to_numpy()-base_sub[y].to_numpy())
        shifts.append({'target':y,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(sub[y],base_sub[y])[0,1]) if d.max()>0 else 1.0})
    sh=pd.DataFrame(shifts); sh.to_csv(EXPERIMENT_DIR/'temporal_state_smoothing_submission_shift.csv',index=False)
    print('\n### wrote',out)
    print(json.dumps(used,indent=2))
    print('\n### shift vs base')
    print(sh.to_string(index=False))

if __name__=='__main__':
    main()
