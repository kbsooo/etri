#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from itertools import product
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')

KEYS=['subject_id','lifelog_date']
DROP=set(['subject_id','sleep_date','lifelog_date']+LABELS)
BASE_CFG={
    'Q1':('semantic_only',50,0.03),
    'Q2':('day_flat',20,0.01),
    'Q3':('dino_k4_cluster',10,0.30),
    'S1':('no_flat_hourly',20,0.10),
    'S2':('no_flat_hourly',20,0.001),
    'S3':('semantic_only',20,0.01),
    'S4':('sleep_plus_s4x',200,0.003),
}

def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

def valid_cols(df, cols):
    out=[]
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1:
            out.append(c)
    return out

def base_subset(all_cols, subset):
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    if subset=='ext_context': return [c for c in all_cols if c.startswith('ext_cal_') or c.startswith('ext_solar_') or c.startswith('ext_weather_')]
    if subset=='ext_appsem': return [c for c in all_cols if c.startswith('ext_appsem_')]
    if subset=='ext_tsfm': return [c for c in all_cols if c.startswith('ext_tsfm_')]
    if subset=='ext_chronos': return [c for c in all_cols if c.startswith('ext_chronos_')]
    if subset=='ext_hfapp': return [c for c in all_cols if c.startswith('ext_hfapp_')]
    if subset=='ext_all': return [c for c in all_cols if c.startswith('ext_')]
    if subset.endswith('+ext_context'):
        return base_subset(all_cols, subset[:-12]) + base_subset(all_cols, 'ext_context')
    if subset.endswith('+ext_appsem'):
        return base_subset(all_cols, subset[:-11]) + base_subset(all_cols, 'ext_appsem')
    if subset.endswith('+ext_tsfm'):
        return base_subset(all_cols, subset[:-9]) + base_subset(all_cols, 'ext_tsfm')
    if subset.endswith('+ext_chronos'):
        return base_subset(all_cols, subset[:-12]) + base_subset(all_cols, 'ext_chronos')
    if subset.endswith('+ext_hfapp'):
        return base_subset(all_cols, subset[:-10]) + base_subset(all_cols, 'ext_hfapp')
    if subset.endswith('+ext_all'):
        return base_subset(all_cols, subset[:-8]) + base_subset(all_cols, 'ext_all')
    raise ValueError(subset)

def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def load_df():
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    df=train.copy()
    paths=[
        FEATURE_DIR/'model_features_v0.parquet',
        FEATURE_DIR/'ssl_semantic_cluster_features.parquet',
        FEATURE_DIR/'external_context_features_v1.parquet',
        FEATURE_DIR/'external_app_semantic_features_v1.parquet',
        FEATURE_DIR/'external_tsfm_proxy_features_v1.parquet',
        FEATURE_DIR/'external_chronos_bolt_features_v1.parquet',
        FEATURE_DIR/'external_hf_app_embedding_features_v1.parquet',
    ]
    for p in paths:
        if p.exists():
            feat=con.execute(f"select * from read_parquet('{p}')").df()
            # avoid duplicate non-key columns by suffixing with file stem if needed
            dup=[c for c in feat.columns if c in df.columns and c not in KEYS]
            if dup:
                feat=feat.rename(columns={c:f'{c}__{p.stem}' for c in dup})
            df=df.merge(feat,on=KEYS,how='left')
    return df

def eval_config(df, cfg, model_name):
    all_cols=[c for c in df.columns if c not in DROP]
    needed=sorted(set(v[0] for v in cfg.values()))
    col_cache={s:valid_cols(df,base_subset(all_cols,s)) for s in needed}
    rows=[]
    for fold in folds():
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()
        scores={}
        for y,(subset,k,C) in cfg.items():
            cols=col_cache[subset]
            if not cols:
                scores[y]=np.nan; continue
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            pipe=make_pipe(k,C,len(cols)); pipe.fit(df.loc[~mask,cols],ytr)
            p=np.clip(pipe.predict_proba(df.loc[mask,cols])[:,1],0.05,0.95)
            scores[y]=log_loss(yva,p,labels=[0,1])
        rows.append({'model':model_name,'fold_id':fold['fold_id'],'mean_logloss':float(np.nanmean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS}})
    return pd.DataFrame(rows)

def main():
    ensure_dirs(); df=load_df()
    candidates=[]
    candidates.append(('base_v4_replicate', BASE_CFG))
    for mode in ['ext_context','ext_appsem','ext_hfapp','ext_tsfm','ext_chronos','ext_all']:
        for k in [5,10,20,50,100,200]:
            for C in [0.001,0.003,0.01,0.03,0.1,0.3]:
                candidates.append((f'{mode}_only_k{k}_C{C}', {y:(mode,k,C) for y in LABELS}))
    # Add external families to the previous best per-target subset, with moderate k/C grids.
    for add in ['ext_context','ext_appsem','ext_hfapp','ext_tsfm','ext_chronos','ext_all']:
        suffix='+'+add
        for k_scale in [1,2,4]:
            for Cmul in [0.3,1,3]:
                cfg={}
                for y,(subset,k,C) in BASE_CFG.items():
                    cfg[y]=(subset+suffix, max(k, min(400,k*k_scale)), max(0.0003, min(1.0,C*Cmul)))
                candidates.append((f'base_v4_plus_{add}_ks{k_scale}_cm{Cmul}', cfg))
    rows=[]
    best_by_target={y:[] for y in LABELS}
    for name,cfg in candidates:
        res=eval_config(df,cfg,name)
        rows.append(res)
        avg=res.mean(numeric_only=True)
        for y in LABELS:
            best_by_target[y].append((float(avg[f'logloss_{y}']), name, cfg[y]))
        print(name, 'mean', float(avg['mean_logloss']))
    allres=pd.concat(rows, ignore_index=True)
    allres.to_csv(EXPERIMENT_DIR/'probe_external_feature_sweep_results.csv',index=False)
    # Assemble target-wise oracle from sweep (CV target averages only; not LB-safe unless frozen after inspection).
    oracle_cfg={}
    for y,lst in best_by_target.items():
        lst=sorted(lst, key=lambda x:x[0])
        oracle_cfg[y]=lst[0][2]
    oracle=eval_config(df, oracle_cfg, 'external_targetwise_best_from_sweep')
    oracle.to_csv(EXPERIMENT_DIR/'probe_external_targetwise_best_results.csv',index=False)
    (EXPERIMENT_DIR/'probe_external_targetwise_best_config.json').write_text(json.dumps(oracle_cfg,indent=2),encoding='utf-8')
    print('\nTOP MODELS')
    summary=allres.groupby('model').mean(numeric_only=True).sort_values('mean_logloss')
    print(summary.head(20).to_string())
    print('\nORACLE targetwise cfg', oracle_cfg)
    print(oracle.to_string(index=False))
    print('oracle avg', float(oracle.mean(numeric_only=True)['mean_logloss']))

if __name__=='__main__': main()
