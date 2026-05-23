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
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, OUT_DIR, ensure_dirs
TARGETS=['Q2','S4','Q3']

def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']
def valid_cols(df, cols):
 out=[]
 for c in cols:
  s=pd.to_numeric(df[c], errors='coerce')
  if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
 return out

def subset_cols(all_cols, name):
 if name=='s4x_only': return [c for c in all_cols if c.startswith('s4x_')]
 if name=='q2x_only': return [c for c in all_cols if c.startswith('q2x_')]
 if name=='mechanism_only': return [c for c in all_cols if c.startswith(('s4x_','q2x_'))]
 if name=='sleep_plus_s4x': return [c for c in all_cols if c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))]
 if name=='q2_load_plus_semantic': return [c for c in all_cols if c.startswith('q2x_') or (any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith('h') and not c.startswith(('topapp_','topamb_')))]
 if name=='noflat_no_routine_mech': return [c for c in all_cols if not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c and not c.startswith(('topapp_','topamb_'))]
 if name=='crossnight_flat': return [c for c in all_cols if c.startswith('cn_h')]
 if name=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
 if name=='crossnight_mech': return [c for c in all_cols if c.startswith(('cn_h','s4x_','q2x_'))]
 if name=='semantic_only': return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith('h') and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c and not c.startswith(('topapp_','topamb_'))]
 if name=='sleep_only': return [c for c in all_cols if any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_')) and '__dev_' not in c and '__prev_' not in c]
 raise ValueError(name)

def main():
 ensure_dirs(); con=duckdb.connect()
 train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
 feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
 df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
 all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
 subsets=['sleep_plus_s4x','crossnight_flat','day_flat','crossnight_mech','q2_load_plus_semantic','sleep_only']
 rows=[]
 for subset in subsets:
  cols=valid_cols(df, subset_cols(all_cols, subset))
  print('subset',subset,'cols',len(cols), flush=True)
  for y in TARGETS:
   for k in [5,10,20,50,100,200]:
    if k>len(cols): continue
    for C in [0.001,0.003,0.01,0.03,0.1]:
     fold_scores=[]
     for fold in folds():
      valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
      mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid,axis=1).to_numpy()
      Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
      ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
      pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,len(cols)))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))])
      try:
       pipe.fit(Xtr,ytr); p=pipe.predict_proba(Xva)[:,1]
      except Exception:
       p=np.full(len(yva),ytr.mean())
      p=np.clip(p,0.05,0.95)
      fold_scores.append(log_loss(yva,p,labels=[0,1]))
     rows.append({'target':y,'subset':subset,'n_features':len(cols),'k':k,'C':C,'mean_logloss':float(np.mean(fold_scores)), 'std_logloss':float(np.std(fold_scores))})
 res=pd.DataFrame(rows).sort_values(['target','mean_logloss'])
 out=EXPERIMENT_DIR/'probe_mechanism_target_ablation.csv'; res.to_csv(out,index=False)
 for y in TARGETS:
  print('\n',y); print(res[res.target==y].head(10).to_string(index=False))
 print('wrote',out)
if __name__=='__main__': main()
