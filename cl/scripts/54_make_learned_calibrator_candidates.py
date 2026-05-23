#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json
import numpy as np, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
# import scripts as modules
spec_ts=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec_ts); spec_ts.loader.exec_module(ts)
spec_lc=importlib.util.spec_from_file_location('lc', ROOT/'scripts/53_eval_learned_temporal_calibrator.py')
lc=importlib.util.module_from_spec(spec_lc); spec_lc.loader.exec_module(lc)
labels=ts.LABELS; hard=['Q1','Q2','S4']
df=ts.load_all(); train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True); sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True); full=pd.concat([train,sample],ignore_index=True)
known_mask=np.r_[np.ones(len(train),bool),np.zeros(len(sample),bool)]; query_mask=np.r_[np.zeros(len(train),bool),np.ones(len(sample),bool)]
base_sub=pd.read_csv(ROOT/'outputs/submission_base_v4_replicate_prob.csv')
base_pred={}
for y in labels:
    base_pred[y]=base_sub[y].to_numpy() if y not in hard else ts.base_predict_for(full,known_mask,query_mask,y,None)

def learned_pred(y, C=0.01):
    pbase=base_pred[y]
    pknown=ts.base_predict_for(train,np.ones(len(train),bool),np.ones(len(train),bool),y,None)
    Xtr=lc.temporal_feature_frame(train,train,y,pknown,exclude_self=True)
    Xte=lc.temporal_feature_frame(train,sample,y,pbase,exclude_self=False)
    pipe=lc.make_pipe(C); pipe.fit(Xtr,train[y].astype(int).to_numpy())
    return np.clip(pipe.predict_proba(Xte)[:,1],0.02,0.98)
learned={y:learned_pred(y,0.01) for y in hard}

def save(name, mode):
    sub=base_sub.copy(); used={}; shifts=[]
    for y in hard:
        if mode=='pure': p=learned[y]
        elif mode=='blend50': p=np.clip(0.5*base_pred[y]+0.5*learned[y],0.02,0.98)
        elif mode=='blend30': p=np.clip(0.7*base_pred[y]+0.3*learned[y],0.02,0.98)
        else: raise ValueError(mode)
        sub[y]=p
    sub.to_csv(ROOT/'outputs'/f'{name}.csv',index=False)
    for y in labels:
        d=np.abs(sub[y].to_numpy()-base_sub[y].to_numpy())
        shifts.append({'target':y,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(sub[y],base_sub[y])[0,1]) if d.max()>0 else 1.0})
    pd.DataFrame(shifts).to_csv(ROOT/'experiments'/f'{name}_shift.csv',index=False)
    print('\n###',name); print(pd.DataFrame(shifts).to_string(index=False))

save('submission_learned_calibrator_q1q2s4_blend30_prob','blend30')
save('submission_learned_calibrator_q1q2s4_blend50_prob','blend50')
save('submission_learned_calibrator_q1q2s4_pure_prob','pure')
