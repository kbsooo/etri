#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, EXPERIMENT_DIR, OUT_DIR, LABELS, ID_COLS, ensure_dirs
warnings.filterwarnings('ignore')
KEYS=['subject_id','lifelog_date']; DROP=set(ID_COLS+LABELS+['is_train'])
BASE_CFG={'Q1':('semantic_only',50,0.03),'Q2':('day_flat',20,0.01),'Q3':('dino_k4_cluster',10,0.30),'S1':('no_flat_hourly',20,0.10),'S2':('no_flat_hourly',20,0.001),'S3':('semantic_only',20,0.01),'S4':('sleep_plus_s4x',200,0.003)}
BAD_CFG=dict(BASE_CFG); BAD_CFG.update({'Q1':('semantic_only+psw_all',100,0.009),'Q2':('day_flat+psw_sleep',40,0.003),'S4':('sleep_plus_s4x+psw_all',200,0.009)})
FOLLOW_CFG=dict(BASE_CFG); FOLLOW_CFG['S4']=('s4evt+sleep+cnproto',200,0.003)

def load_all():
    con=duckdb.connect(); train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv').assign(is_train=1)
    paths=[FEATURE_DIR/'model_features_v0.parquet',FEATURE_DIR/'ssl_semantic_cluster_features.parquet',FEATURE_DIR/'prior_sleep_window_features_v1.parquet',FEATURE_DIR/'prior_sleep_proxy_features_v1.parquet',FEATURE_DIR/'public_failure_followup_features_v1.parquet']
    df=train.copy()
    for p in paths:
        if p.exists():
            feat=con.execute(f"select * from read_parquet('{p}')").df(); dup=[c for c in feat.columns if c in df.columns and c not in KEYS]
            if dup: feat=feat.rename(columns={c:f'{c}__{p.stem}' for c in dup})
            df=df.merge(feat,on=KEYS,how='left')
    df['lifelog_dt']=pd.to_datetime(df['lifelog_date'])
    return df

def base_subset(all_cols, subset):
    if subset=='semantic_only': return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','q2lr_','q1qual_','s4evt_','cnproto_','q2proto_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly': return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','q2lr_','q1qual_','s4evt_','cnproto_','q2proto_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x': return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_','q1qual_','q2lr_','s4evt_','cnproto_','q2proto_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    if subset=='psw_all': return [c for c in all_cols if c.startswith('psw_')]
    if subset=='psw_sleep': return [c for c in all_cols if c.startswith('psw_sw_overnight') or c.startswith('psw_sw_presleep') or c.startswith('psw_sw_fullctx')]
    if subset.endswith('+psw_all'): return base_subset(all_cols,subset[:-8])+base_subset(all_cols,'psw_all')
    if subset.endswith('+psw_sleep'): return base_subset(all_cols,subset[:-10])+base_subset(all_cols,'psw_sleep')
    if subset=='s4evt+sleep+cnproto': return [c for c in all_cols if c.startswith('s4evt_')]+base_subset(all_cols,'sleep_plus_s4x')+[c for c in all_cols if c.startswith('cnproto_')]
    raise ValueError(subset)

def valid_cols(df, cols):
    out=[]; seen=set()
    for c in cols:
        if c in seen or c not in df.columns: continue
        seen.add(c); s=pd.to_numeric(df[c],errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
    return out

def pipe(k,C,n): return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,n))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def make_splits(df):
    splits=[]
    # existing chrono folds
    for fold in json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']:
        valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
        va=df.apply(lambda r:(r.subject_id,r.lifelog_date) in valid,axis=1).to_numpy(); tr=~va
        splits.append((fold['fold_id'],tr,va))
    # last 14 and 21 rows per subject
    for n in [14,21]:
        va=np.zeros(len(df),dtype=bool)
        for sid,g in df.sort_values('lifelog_dt').groupby('subject_id'):
            va[g.tail(min(n,len(g)//2)).index]=True
        splits.append((f'chrono_tail_{n}',~va,va))
    # leave-one-subject diagnostics
    for sid in sorted(df.subject_id.unique()):
        va=(df.subject_id==sid).to_numpy(); splits.append((f'loso_{sid}',~va,va))
    return splits

def eval_cfg(df,cfg,name):
    all_cols=[c for c in df.columns if c not in DROP and c!='lifelog_dt']; cache={}; rows=[]
    for split_id,tr,va in make_splits(df):
        scores={}
        for y,(subset,k,C) in cfg.items():
            if subset not in cache: cache[subset]=valid_cols(df,base_subset(all_cols,subset))
            cols=cache[subset]
            m=pipe(k,C,len(cols)); m.fit(df.loc[tr,cols],df.loc[tr,y].astype(int))
            p=np.clip(m.predict_proba(df.loc[va,cols])[:,1],0.05,0.95)
            scores[y]=log_loss(df.loc[va,y].astype(int),p,labels=[0,1])
        rows.append({'model':name,'split':split_id,'mean':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS}})
    return pd.DataFrame(rows)

def main():
    ensure_dirs(); df=load_all(); res=[]
    for name,cfg in [('base',BASE_CFG),('bad_public_cfg',BAD_CFG),('followup_s4_only',FOLLOW_CFG)]: res.append(eval_cfg(df,cfg,name))
    out=pd.concat(res,ignore_index=True); out.to_csv(EXPERIMENT_DIR/'followup_alt_robustness_results.csv',index=False)
    print(out.groupby('model')['mean'].agg(['mean','std','min','max']).to_string())
    for split in out.split.unique():
        piv=out[out.split==split][['model','mean']].sort_values('mean')
        print('\n',split); print(piv.to_string(index=False))
if __name__=='__main__': main()
