#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import QuantileTransformer
from tabpfn import TabPFNClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')
KEYS=['subject_id','lifelog_date']
DROP=set(['subject_id','sleep_date','lifelog_date']+LABELS)
BASE_CFG={
    'Q1':('semantic_only',50), 'Q2':('day_flat',20), 'Q3':('dino_k4_cluster',10),
    'S1':('no_flat_hourly',20), 'S2':('no_flat_hourly',20), 'S3':('semantic_only',20), 'S4':('sleep_plus_s4x',200),
}
EXT_CFG={
    'Q1':('semantic_only',50), 'Q2':('day_flat+ext_appsem',80), 'Q3':('dino_k4_cluster',10),
    'S1':('no_flat_hourly',20), 'S2':('no_flat_hourly',20), 'S3':('semantic_only',20), 'S4':('sleep_plus_s4x+ext_context',200),
}

def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

def valid_cols(df, cols):
    out=[]
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
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
    if subset=='ext_context': return [c for c in all_cols if c.startswith(('ext_cal_','ext_solar_','ext_weather_'))]
    if subset=='ext_appsem': return [c for c in all_cols if c.startswith('ext_appsem_')]
    if subset.endswith('+ext_context'): return base_subset(all_cols, subset[:-12]) + base_subset(all_cols,'ext_context')
    if subset.endswith('+ext_appsem'): return base_subset(all_cols, subset[:-11]) + base_subset(all_cols,'ext_appsem')
    raise ValueError(subset)

def load_df():
    con=duckdb.connect(); train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv'); df=train.copy()
    for p in [FEATURE_DIR/'model_features_v0.parquet', FEATURE_DIR/'ssl_semantic_cluster_features.parquet', FEATURE_DIR/'external_context_features_v1.parquet', FEATURE_DIR/'external_app_semantic_features_v1.parquet']:
        if p.exists(): df=df.merge(con.execute(f"select * from read_parquet('{p}')").df(),on=KEYS,how='left')
    return df

def eval_cfg(df,cfg,name,n_estimators=4):
    all_cols=[c for c in df.columns if c not in DROP]
    cache={s:valid_cols(df,base_subset(all_cols,s)) for s,_ in cfg.values()}
    rows=[]
    for fold in folds():
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()
        scores={}
        for y,(subset,k) in cfg.items():
            cols=cache[subset]
            Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            pipe=Pipeline([
                ('imp',SimpleImputer(strategy='median')),
                ('sel',SelectKBest(f_classif,k=min(k,len(cols)))) ,
                ('qt',QuantileTransformer(n_quantiles=min(50, max(10, len(ytr)//4)), output_distribution='normal', random_state=42)),
                ('clf',TabPFNClassifier(n_estimators=n_estimators, device='cpu', random_state=42, ignore_pretraining_limits=True, n_preprocessing_jobs=1))
            ])
            pipe.fit(Xtr,ytr)
            p=np.clip(pipe.predict_proba(Xva)[:,1],0.05,0.95)
            scores[y]=log_loss(yva,p,labels=[0,1])
        rows.append({'model':name,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS}})
        print(name, fold['fold_id'], rows[-1]['mean_logloss'])
    return pd.DataFrame(rows)

def main():
    ensure_dirs(); df=load_df()
    outs=[]
    for name,cfg in [('tabpfn_base_v4_subsets',BASE_CFG),('tabpfn_external_targetwise_subsets',EXT_CFG)]:
        res=eval_cfg(df,cfg,name,n_estimators=4); outs.append(res)
        res.to_csv(EXPERIMENT_DIR/f'probe_{name}_results.csv',index=False)
    allres=pd.concat(outs,ignore_index=True)
    allres.to_csv(EXPERIMENT_DIR/'probe_tabpfn_external_results.csv',index=False)
    print('\nsummary')
    print(allres.groupby('model').mean(numeric_only=True).to_string())

if __name__=='__main__': main()
