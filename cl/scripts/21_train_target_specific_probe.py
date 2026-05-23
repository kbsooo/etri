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
  keys=('hr_','gps_','app_','wifi_','ble_','amb_')
  return [c for c in all_cols if any(k in c for k in keys) and not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c and not c.startswith(('topapp_','topamb_'))]
 if subset=='sleep_only':
  keys=('sleep','quiet_','screenoff_','late_','dark_','bright_')
  return [c for c in all_cols if any(k in c for k in keys) and '__dev_' not in c and '__prev_' not in c]
 if subset=='daily_windows_only':
  keys=('screen_','steps_','distance_','light_','activity_','charge_','mlight_','wlight_')
  return [c for c in all_cols if (not c.startswith('h')) and any(k in c for k in keys) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
 if subset=='no_flat_hourly':
  return [c for c in all_cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c and not c.startswith(('topapp_','topamb_'))]
 raise ValueError(subset)

def logit(p):
 p=np.clip(p,1e-6,1-1e-6); return np.log(p/(1-p))
def sigmoid(z): return 1/(1+np.exp(-z))

def main():
 ensure_dirs(); con=duckdb.connect()
 train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
 feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
 df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
 all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
 # configs from per-target search before/after routine; conservative hand-picked
 cfg={
  'Q1':('semantic_only',50,0.03),
  'Q2':('sleep_only',10,0.01),
  'Q3':('sleep_only',10,0.10),
  'S1':('no_flat_hourly',20,0.10),
  'S2':('semantic_only',20,0.001),
  'S3':('no_flat_hourly',50,0.01),
  'S4':('sleep_only',120,0.03),
 }
 rows=[]; pred_rows=[]
 for fold in folds():
  valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
  mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1).to_numpy()
  fold_scores={}; fold_auc={}; fold_acc={}
  tmp=df.loc[mask,['subject_id','lifelog_date']+LABELS].copy();
  for y,(subset,k,C) in cfg.items():
   cols=valid_cols(df,get_cols(all_cols,subset))
   Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
   ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
   pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,len(cols)))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))])
   pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xva)[:,1]
   # tune temperature on training OOF unavailable; evaluate simple temperatures on valid as diagnostic upper bound
   best_ll=99; best_t=None; best_clip=None; bestp=None
   for T in [0.5,0.75,1,1.25,1.5,2,3]:
    pp=sigmoid(logit(p)/T)
    for cl in [0.01,0.03,0.05,0.08,0.1,0.15]:
     ppp=np.clip(pp,cl,1-cl); ll=log_loss(yva,ppp,labels=[0,1])
     if ll<best_ll: best_ll=ll; best_t=T; best_clip=cl; bestp=ppp
   p=np.clip(p,0.05,0.95)
   fold_scores[y]=log_loss(yva,p,labels=[0,1])
   try: fold_auc[y]=roc_auc_score(yva,p)
   except Exception: fold_auc[y]=np.nan
   fold_acc[y]=accuracy_score(yva,p>=0.5)
   tmp[f'pred_{y}']=p; tmp[f'pred_calib_ub_{y}']=bestp
   tmp[f'calib_t_{y}']=best_t; tmp[f'calib_clip_{y}']=best_clip
  rows.append({'model':'target_specific_feature_only','fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(fold_scores.values()))),**{f'logloss_{y}':fold_scores[y] for y in LABELS},**{f'auc_{y}':fold_auc[y] for y in LABELS},**{f'acc_{y}':fold_acc[y] for y in LABELS}})
  pred_rows.append(tmp)
 res=pd.DataFrame(rows); out=EXPERIMENT_DIR/'probe_target_specific_results.csv'; res.to_csv(out,index=False)
 pd.concat(pred_rows).to_csv(EXPERIMENT_DIR/'probe_target_specific_oof.csv',index=False)
 print(res.to_string(index=False))
 print('avg mean',res.mean(numeric_only=True)['mean_logloss'])
 print('wrote',out)
if __name__=='__main__': main()
