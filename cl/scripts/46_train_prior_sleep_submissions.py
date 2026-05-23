#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')
KEYS=['subject_id','lifelog_date']
ID_COLS=['subject_id','sleep_date','lifelog_date']
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

def valid_cols(df, cols):
    out=[]
    train=df['is_train'].eq(1)
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df.loc[train,c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1:
            out.append(c)
    return out

def base_subset(all_cols, subset):
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    if subset=='psw_all': return [c for c in all_cols if c.startswith('psw_')]
    if subset=='psw_sleep': return [c for c in all_cols if c.startswith('psw_sw_overnight') or c.startswith('psw_sw_presleep') or c.startswith('psw_sw_fullctx')]
    if subset=='pswp_proxy': return [c for c in all_cols if c.startswith('pswp_')]
    if subset.endswith('+psw_all'):
        return base_subset(all_cols, subset[:-8]) + base_subset(all_cols, 'psw_all')
    if subset.endswith('+psw_sleep'):
        return base_subset(all_cols, subset[:-10]) + base_subset(all_cols, 'psw_sleep')
    if subset.endswith('+pswp_proxy'):
        return base_subset(all_cols, subset[:-11]) + base_subset(all_cols, 'pswp_proxy')
    raise ValueError(subset)

def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def load_all():
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv').assign(is_train=1)
    sample=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv').assign(is_train=0)
    for y in LABELS: sample[y]=np.nan
    df=pd.concat([train,sample],ignore_index=True)
    paths=[FEATURE_DIR/'model_features_v0.parquet',FEATURE_DIR/'ssl_semantic_cluster_features.parquet',FEATURE_DIR/'prior_sleep_window_features_v1.parquet',FEATURE_DIR/'prior_sleep_proxy_features_v1.parquet']
    for p in paths:
        if p.exists():
            feat=con.execute(f"select * from read_parquet('{p}')").df()
            dup=[c for c in feat.columns if c in df.columns and c not in KEYS]
            if dup: feat=feat.rename(columns={c:f'{c}__{p.stem}' for c in dup})
            df=df.merge(feat,on=KEYS,how='left')
    return df

def predict_submission(df,cfg,name):
    all_cols=[c for c in df.columns if c not in DROP]
    train=df['is_train'].eq(1); test=~train
    sub=df.loc[test,ID_COLS].copy().reset_index(drop=True)
    used={}
    for y,(subset,k,C) in cfg.items():
        cols=valid_cols(df,base_subset(all_cols,subset)); used[y]={'subset':subset,'k':k,'C':C,'ncols':len(cols)}
        pipe=make_pipe(k,C,len(cols))
        pipe.fit(df.loc[train,cols], df.loc[train,y].astype(int).to_numpy())
        sub[y]=np.clip(pipe.predict_proba(df.loc[test,cols])[:,1],0.05,0.95)
    out=OUT_DIR/f'{name}.csv'; sub.to_csv(out,index=False)
    (EXPERIMENT_DIR/f'{name}_used_features.json').write_text(json.dumps(used,indent=2),encoding='utf-8')
    print(f'wrote {out} shape={sub.shape}')
    print(sub[LABELS].describe().to_string())

def main():
    ensure_dirs(); df=load_all()
    oracle=json.loads((EXPERIMENT_DIR/'probe_prior_sleep_targetwise_best_config.json').read_text())
    # JSON lists -> tuples
    oracle={y:tuple(v) for y,v in oracle.items()}
    predict_submission(df, BASE_CFG, 'submission_base_v4_replicate_prob')
    predict_submission(df, oracle, 'submission_prior_sleep_targetwise_cv0593_prob')
    # Conservative version: only targets with clear CV gain from sleep-window sweep.
    conservative=dict(BASE_CFG)
    for y in ['Q1','Q2','S4']:
        conservative[y]=oracle[y]
    predict_submission(df, conservative, 'submission_prior_sleep_conservative_q1q2s4_prob')

if __name__=='__main__': main()
