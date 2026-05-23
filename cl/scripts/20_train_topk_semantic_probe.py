#!/usr/bin/env python3
from __future__ import annotations
import json, sys
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

def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']
def valid_cols(df, cols):
 out=[]
 for c in cols:
  s=pd.to_numeric(df[c], errors='coerce')
  if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
 return out

def main():
 ensure_dirs(); con=duckdb.connect()
 train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
 feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
 df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
 all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
 subsets={
  'topapp_only':[c for c in all_cols if c.startswith('topapp_')],
  'topamb_only':[c for c in all_cols if c.startswith('topamb_')],
  'top_semantic':[c for c in all_cols if c.startswith(('topapp_','topamb_','ble_deviceclass_','app_hourly_','app_active_'))],
  'semantic_plus_top':[c for c in all_cols if (any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) or c.startswith(('topapp_','topamb_','ble_deviceclass_'))) and not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c],
  'no_flat_no_routine_top':[c for c in all_cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c],
 }
 rows=[]
 for subset, raw in subsets.items():
  cols=valid_cols(df,raw)
  for k in [10,20,50,100,200]:
   if k>len(cols): continue
   for C in [0.001,0.003,0.01,0.03]:
    for fold in folds():
     valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
     mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1).to_numpy()
     Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
     scores={}
     for y in LABELS:
      ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
      pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,len(cols)))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))])
      try:
       pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xva)[:,1]
      except Exception: p=np.full(len(yva),ytr.mean())
      p=np.clip(p,0.05,0.95); scores[y]=log_loss(yva,p,labels=[0,1])
     rows.append({'model':'topk_semantic_selectk_logistic','subset':subset,'n_features':len(cols),'k':k,'C':C,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{a}':b for a,b in scores.items()}})
 res=pd.DataFrame(rows).sort_values('mean_logloss')
 out=EXPERIMENT_DIR/'probe_topk_semantic_results.csv'; res.to_csv(out,index=False)
 print(res.head(12).to_string(index=False))
 print('avg'); print(res.groupby(['subset','k','C'])['mean_logloss'].mean().reset_index().sort_values('mean_logloss').head(12).to_string(index=False))
 print('wrote',out)
if __name__=='__main__': main()
