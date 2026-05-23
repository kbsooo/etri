#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')

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

def base_subset(all_cols, subset):
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    raise ValueError(subset)

def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    cl=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_semantic_cluster_features.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left').merge(cl,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in df.columns if c not in {'subject_id','sleep_date','lifelog_date','Q1','Q2','Q3','S1','S2','S3','S4'}]
    subset_names=['semantic_only','no_flat_hourly','sleep_plus_s4x','day_flat','dino_k4_cluster']
    col_cache={s:valid_cols(df,base_subset(all_cols,s)) for s in subset_names}
    cfg={
        'Q1':('semantic_only',50,0.03),
        'Q2':('day_flat',20,0.01),
        'Q3':('dino_k4_cluster',10,0.30),
        'S1':('no_flat_hourly',20,0.10),
        'S2':('no_flat_hourly',20,0.001),
        'S3':('semantic_only',20,0.01),
        'S4':('sleep_plus_s4x',200,0.003),
    }
    rows=[]; pred_rows=[]
    for fold in folds():
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()
        scores={}; aucs={}; accs={}
        tmp=df.loc[mask,['subject_id','lifelog_date']+LABELS].copy()
        for y,(subset,k,C) in cfg.items():
            cols=col_cache[subset]
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            pipe=make_pipe(k,C,len(cols)); pipe.fit(df.loc[~mask,cols],ytr)
            p=np.clip(pipe.predict_proba(df.loc[mask,cols])[:,1],0.05,0.95)
            scores[y]=log_loss(yva,p,labels=[0,1]); tmp[f'pred_{y}']=p
            try: aucs[y]=roc_auc_score(yva,p)
            except Exception: aucs[y]=np.nan
            accs[y]=accuracy_score(yva,p>=0.5)
        rows.append({'model':'target_specific_subjective_q_v4_dino_q3_cluster','fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS},**{f'auc_{y}':aucs[y] for y in LABELS},**{f'acc_{y}':accs[y] for y in LABELS}})
        pred_rows.append(tmp)
    res=pd.DataFrame(rows)
    res.to_csv(EXPERIMENT_DIR/'probe_target_specific_subjective_q_v4_dino_q3_cluster_results.csv',index=False)
    pd.concat(pred_rows).to_csv(EXPERIMENT_DIR/'probe_target_specific_subjective_q_v4_dino_q3_cluster_oof.csv',index=False)
    (EXPERIMENT_DIR/'probe_target_specific_subjective_q_v4_dino_q3_cluster_config.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    print(res.to_string(index=False))
    print('\navg mean',res.mean(numeric_only=True)['mean_logloss'])
    print('target avg')
    print(res[[f'logloss_{y}' for y in LABELS]].mean().to_string())
    print('cfg',cfg)

if __name__=='__main__': main()
