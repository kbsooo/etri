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

TARGETS=["Q1","Q3"]
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

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

def semantic_cols(cols):
    return [c for c in cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]

def qstate_cols(cols):
    return [c for c in cols if c.startswith(('q3x_','q1x_','qpatch_','qcarry_'))]

def eval_subset(df, fold_defs, target, cols, k, C):
    losses=[]; aucs=[]; accs=[]
    for fold in fold_defs:
        valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid, axis=1).to_numpy()
        ytr=df.loc[~mask,target].astype(int).to_numpy(); yva=df.loc[mask,target].astype(int).to_numpy()
        pipe=Pipeline([
            ('imp',SimpleImputer(strategy='median')),
            ('sel',SelectKBest(f_classif,k=min(k,len(cols)))),
            ('scale',RobustScaler()),
            ('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42)),
        ])
        pipe.fit(df.loc[~mask,cols],ytr)
        p=np.clip(pipe.predict_proba(df.loc[mask,cols])[:,1],0.05,0.95)
        losses.append(log_loss(yva,p,labels=[0,1]))
        try: aucs.append(roc_auc_score(yva,p))
        except Exception: aucs.append(np.nan)
        accs.append(accuracy_score(yva,p>=0.5))
    return float(np.mean(losses)), losses, float(np.nanmean(aucs)), float(np.mean(accs))

def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    base=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    ae=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_hourly_masked_ae_embeddings.parquet'}')").df()
    di=con.execute(f"select * from read_parquet('{FEATURE_DIR/'ssl_hourly_dino_temporal_embeddings.parquet'}')").df()
    df=train.merge(base,on=['subject_id','lifelog_date'],how='left')\
            .merge(ae,on=['subject_id','lifelog_date'],how='left')\
            .merge(di,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in df.columns if c not in {'subject_id','sleep_date','lifelog_date','Q1','Q2','Q3','S1','S2','S3','S4'}]
    sem=semantic_cols(all_cols); qs=qstate_cols(all_cols)
    ae_cols=[c for c in all_cols if c.startswith('ssl_masked_ae_')]
    di_cols=[c for c in all_cols if c.startswith('ssl_dino_temporal_')]
    subsets={
        'ssl_masked_ae_only': ae_cols,
        'ssl_dino_temporal_only': di_cols,
        'ssl_both': ae_cols+di_cols,
        'semantic_only': sem,
        'semantic_plus_ssl_both': sem+ae_cols+di_cols,
        'qstate_plus_semantic': sorted(set(qs+sem)),
        'qstate_semantic_plus_ssl_both': sorted(set(qs+sem+ae_cols+di_cols)),
    }
    subsets={k:valid_cols(df,v) for k,v in subsets.items()}
    rows=[]; fold_defs=folds()
    for target in TARGETS:
        for name, cols in subsets.items():
            if not cols: continue
            for k in [20,50,80,120,200]:
                if k>len(cols)*2: continue
                for C in [0.001,0.003,0.01,0.03,0.1]:
                    avg, per, auc, acc=eval_subset(df,fold_defs,target,cols,k,C)
                    rows.append({'target':target,'subset':name,'k':k,'C':C,'avg_logloss':avg,'avg_auc':auc,'avg_acc':acc,'n_cols':len(cols),**{fold_defs[i]['fold_id']:per[i] for i in range(len(per))}})
    res=pd.DataFrame(rows).sort_values(['target','avg_logloss'])
    out=EXPERIMENT_DIR/'probe_ssl_feature_fusion_q_results.csv'
    res.to_csv(out,index=False)
    print('wrote',out)
    for target in TARGETS:
        print('\nBEST',target)
        print(res[res.target==target].head(12).to_string(index=False))

if __name__=='__main__': main()
