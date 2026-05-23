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
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')
TARGETS=['Q1','Q3']

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
    if subset=='sleep_only':
        return [c for c in all_cols if any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_')) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_')) and '__dev_' not in c and '__prev_' not in c]
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='q3x_only':
        return [c for c in all_cols if c.startswith(('q3x_','qpatch_','qcarry_prev_q3x_','qcarry_prev_qpatch_'))]
    if subset=='q1x_only':
        return [c for c in all_cols if c.startswith(('q1x_','qpatch_','qcarry_prev_q1x_','qcarry_prev_qpatch_'))]
    if subset=='dino_k4_cluster':
        return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    raise ValueError(subset)

def eval_target(df, fold_defs, target, cols, k, C):
    losses=[]; aucs=[]; accs=[]
    for fold in fold_defs:
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid, axis=1).to_numpy()
        Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
        ytr=df.loc[~mask,target].astype(int).to_numpy(); yva=df.loc[mask,target].astype(int).to_numpy()
        pipe=Pipeline([
            ('imp',SimpleImputer(strategy='median')),
            ('sel',SelectKBest(f_classif,k=min(k,len(cols)))),
            ('scale',RobustScaler()),
            ('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42)),
        ])
        pipe.fit(Xtr,ytr)
        p=np.clip(pipe.predict_proba(Xva)[:,1],0.05,0.95)
        losses.append(log_loss(yva,p,labels=[0,1]))
        try: aucs.append(roc_auc_score(yva,p))
        except Exception: aucs.append(np.nan)
        accs.append(accuracy_score(yva,p>=0.5))
    return float(np.mean(losses)), losses, float(np.nanmean(aucs)), float(np.mean(accs))

def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    cl=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_semantic_cluster_features.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left').merge(cl,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in df.columns if c not in {'subject_id','sleep_date','lifelog_date','Q1','Q2','Q3','S1','S2','S3','S4'}]
    sleep=valid_cols(df,base_subset(all_cols,'sleep_only'))
    sem=valid_cols(df,base_subset(all_cols,'semantic_only'))
    q3x=valid_cols(df,base_subset(all_cols,'q3x_only'))
    q1x=valid_cols(df,base_subset(all_cols,'q1x_only'))
    d4=valid_cols(df,base_subset(all_cols,'dino_k4_cluster'))
    subsets={
        'dino_k4_cluster':d4,
        'sleep_only':sleep,
        'sleep_plus_dino_k4':sleep+d4,
        'semantic_only':sem,
        'semantic_plus_dino_k4':sem+d4,
        'q3x_plus_dino_k4':q3x+d4,
        'sleep_q3x_plus_dino_k4':sleep+q3x+d4,
        'q1x_plus_dino_k4':q1x+d4,
    }
    rows=[]; fold_defs=folds()
    grid_k=[10,20,30,50,80,120,200,400]
    grid_C=[0.0005,0.001,0.003,0.01,0.03,0.1,0.3]
    target_subsets={
        'Q1':['dino_k4_cluster','semantic_only','semantic_plus_dino_k4','q1x_plus_dino_k4'],
        'Q3':['dino_k4_cluster','sleep_only','sleep_plus_dino_k4','q3x_plus_dino_k4','sleep_q3x_plus_dino_k4','semantic_plus_dino_k4'],
    }
    for target, names in target_subsets.items():
        for name in names:
            cols=subsets[name]
            if not cols: continue
            for k in grid_k:
                if k > len(cols)*2: continue
                for C in grid_C:
                    avg, per, auc, acc=eval_target(df,fold_defs,target,cols,k,C)
                    rows.append({'target':target,'subset':name,'k':k,'C':C,'avg_logloss':avg,'avg_auc':auc,'avg_acc':acc,'n_cols':len(cols),**{fold_defs[i]['fold_id']:per[i] for i in range(len(per))}})
    res=pd.DataFrame(rows).sort_values(['target','avg_logloss'])
    out=EXPERIMENT_DIR/'probe_q_ssl_cluster_fusion_results.csv'
    res.to_csv(out,index=False)
    print('cols', {k:len(v) for k,v in subsets.items()})
    print('wrote',out)
    for target in TARGETS:
        print('\nBEST',target)
        print(res[res.target==target].head(15).to_string(index=False))

if __name__=='__main__': main()
