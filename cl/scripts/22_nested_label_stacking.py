#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
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
 if subset=='no_flat_hourly':
  return [c for c in all_cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c and not c.startswith(('topapp_','topamb_'))]
 raise ValueError(subset)

def make_pipe(k,C,ncols):
 return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))])

def main():
 ensure_dirs(); con=duckdb.connect()
 train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
 feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
 df=train.merge(feat,on=['subject_id','lifelog_date'],how='left').reset_index(drop=True)
 all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
 cfg={
  'Q1':('semantic_only',50,0.03), 'Q2':('sleep_only',10,0.01), 'Q3':('sleep_only',10,0.10),
  'S1':('no_flat_hourly',20,0.10), 'S2':('semantic_only',20,0.001), 'S3':('no_flat_hourly',50,0.01), 'S4':('sleep_only',120,0.03),
 }
 col_cache={s:valid_cols(df,get_cols(all_cols,s)) for s in set(v[0] for v in cfg.values())}
 rows=[]; pred_all=[]
 for fold in folds():
  valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
  outer_va=np.array([i for i,r in df.iterrows() if (r.subject_id,r.lifelog_date) in valid])
  outer_tr=np.array([i for i in range(len(df)) if i not in set(outer_va)])
  # inner OOF base predictions for training meta
  inner_oof=np.zeros((len(outer_tr),len(LABELS)))
  kf=KFold(n_splits=3,shuffle=True,random_state=42)
  for itr, iva in kf.split(outer_tr):
   tr_idx=outer_tr[itr]; va_idx=outer_tr[iva]
   for j,y in enumerate(LABELS):
    subset,k,C=cfg[y]; cols=col_cache[subset]
    pipe=make_pipe(k,C,len(cols))
    pipe.fit(df.loc[tr_idx,cols], df.loc[tr_idx,y].astype(int))
    inner_oof[iva,j]=pipe.predict_proba(df.loc[va_idx,cols])[:,1]
  # base predictions for outer valid
  outer_base=np.zeros((len(outer_va),len(LABELS)))
  for j,y in enumerate(LABELS):
   subset,k,C=cfg[y]; cols=col_cache[subset]
   pipe=make_pipe(k,C,len(cols))
   pipe.fit(df.loc[outer_tr,cols], df.loc[outer_tr,y].astype(int))
   outer_base[:,j]=pipe.predict_proba(df.loc[outer_va,cols])[:,1]
  # meta features: base probs + logits
  def metaX(P):
   P=np.clip(P,1e-5,1-1e-5); return np.hstack([P, np.log(P/(1-P))])
  Xmeta_tr=metaX(inner_oof); Xmeta_va=metaX(outer_base)
  scores_base={}; scores_stack={}
  outdf=df.loc[outer_va,['subject_id','lifelog_date']+LABELS].copy()
  for j,y in enumerate(LABELS):
   ytr=df.loc[outer_tr,y].astype(int).to_numpy(); yva=df.loc[outer_va,y].astype(int).to_numpy()
   basep=np.clip(outer_base[:,j],0.05,0.95)
   scores_base[y]=log_loss(yva,basep,labels=[0,1])
   meta=Pipeline([('scale',StandardScaler()),('clf',LogisticRegression(C=0.1,solver='liblinear',max_iter=1000))])
   meta.fit(Xmeta_tr,ytr)
   sp=np.clip(meta.predict_proba(Xmeta_va)[:,1],0.05,0.95)
   scores_stack[y]=log_loss(yva,sp,labels=[0,1])
   outdf[f'base_{y}']=basep; outdf[f'stack_{y}']=sp
  rows.append({'fold_id':fold['fold_id'],'base_mean':float(np.mean(list(scores_base.values()))),'stack_mean':float(np.mean(list(scores_stack.values()))),**{f'base_{y}':scores_base[y] for y in LABELS},**{f'stack_{y}':scores_stack[y] for y in LABELS}})
  pred_all.append(outdf)
 res=pd.DataFrame(rows)
 res.to_csv(EXPERIMENT_DIR/'probe_nested_stacking_results.csv',index=False)
 pd.concat(pred_all).to_csv(EXPERIMENT_DIR/'probe_nested_stacking_oof.csv',index=False)
 print(res.to_string(index=False))
 print('avg base',res.base_mean.mean(),'avg stack',res.stack_mean.mean())
if __name__=='__main__': main()
