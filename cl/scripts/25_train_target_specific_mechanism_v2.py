#!/usr/bin/env python3
from __future__ import annotations
import json, sys
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

def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']
def valid_cols(df, cols):
 out=[]
 for c in cols:
  s=pd.to_numeric(df[c], errors='coerce')
  if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
 return out

def get_cols(all_cols, subset):
 if subset=='semantic_only':
  return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
 if subset=='sleep_only':
  return [c for c in all_cols if any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_')) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c]
 if subset=='no_flat_hourly':
  return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
 if subset=='sleep_plus_s4x':
  return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_'))]
 if subset=='q2x_only': return [c for c in all_cols if c.startswith('q2x_')]
 if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
 raise ValueError(subset)

def main():
 ensure_dirs(); con=duckdb.connect()
 train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
 feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
 df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
 all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
 cfg={
  'Q1':('semantic_only',50,0.03),
  'Q2':('day_flat',20,0.01),
  'Q3':('sleep_only',20,0.03),
  'S1':('no_flat_hourly',20,0.10),
  'S2':('no_flat_hourly',20,0.001),
  'S3':('semantic_only',20,0.01),
  'S4':('sleep_plus_s4x',200,0.003),
 }
 col_cache={s:valid_cols(df,get_cols(all_cols,s)) for s,_,_ in cfg.values()}
 rows=[]; pred_rows=[]
 for fold in folds():
  valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
  mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1).to_numpy()
  scores={}; aucs={}; accs={}
  tmp=df.loc[mask,['subject_id','lifelog_date']+LABELS].copy()
  for y,(subset,k,C) in cfg.items():
   cols=col_cache[subset]
   Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
   ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
   pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,len(cols)))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))])
   pipe.fit(Xtr,ytr); p=np.clip(pipe.predict_proba(Xva)[:,1],0.05,0.95)
   scores[y]=log_loss(yva,p,labels=[0,1])
   try: aucs[y]=roc_auc_score(yva,p)
   except Exception: aucs[y]=np.nan
   accs[y]=accuracy_score(yva,p>=0.5)
   tmp[f'pred_{y}']=p
  rows.append({'model':'target_specific_mechanism_v2','fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS},**{f'auc_{y}':aucs[y] for y in LABELS},**{f'acc_{y}':accs[y] for y in LABELS}})
  pred_rows.append(tmp)
 res=pd.DataFrame(rows)
 out=EXPERIMENT_DIR/'probe_target_specific_mechanism_v2_results.csv'; res.to_csv(out,index=False)
 pd.concat(pred_rows).to_csv(EXPERIMENT_DIR/'probe_target_specific_mechanism_v2_oof.csv',index=False)
 print(res.to_string(index=False))
 print('avg mean',res.mean(numeric_only=True)['mean_logloss'])
 print('target avg')
 print(res[[f'logloss_{y}' for y in LABELS]].mean().to_string())
 print('wrote',out)
if __name__=='__main__': main()
