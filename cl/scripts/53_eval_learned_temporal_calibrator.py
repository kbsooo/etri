#!/usr/bin/env python3
"""Learned temporal-state calibrator for interleaved same-subject completion.

This is deliberately small/regularized: for each target, combine the base model
probability with label-neighborhood features (prev/next/local means, distances,
streak summaries). Evaluate under test-pattern masked validation and generate
conservative public-candidate submissions.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util, json, warnings
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
LABELS=ts.LABELS
EXP=ROOT/'experiments'; OUT=ROOT/'outputs'

def logit(p):
    p=np.clip(np.asarray(p,float),0.02,0.98)
    return np.log(p/(1-p))

def safe_mean(x, default):
    return float(np.mean(x)) if len(x) else float(default)

def temporal_feature_frame(anchor: pd.DataFrame, query: pd.DataFrame, target: str, base_p: np.ndarray, exclude_self: bool) -> pd.DataFrame:
    """Features for query rows using anchor labels. If exclude_self, remove same date row from anchor."""
    g=float(anchor[target].mean())
    rows=[]
    for i,r in enumerate(query.itertuples(index=False)):
        sid=getattr(r,'subject_id'); d=getattr(r,'sleep_date')
        k=anchor[anchor.subject_id.eq(sid)].sort_values('sleep_date')
        if exclude_self:
            k=k[~k.sleep_date.eq(d)]
        vals=k[target].astype(float).to_numpy()
        dates=k.sleep_date.to_numpy(dtype='datetime64[D]').astype(int)
        qd=np.datetime64(d,'D').astype(int)
        prev=k[k.sleep_date < d].tail(5)
        nxt=k[k.sleep_date > d].head(5)
        prev_vals=prev[target].astype(float).to_numpy(); next_vals=nxt[target].astype(float).to_numpy()
        prev_d=((d-prev.sleep_date).dt.days.to_numpy().astype(float)) if len(prev) else np.array([])
        next_d=((nxt.sleep_date-d).dt.days.to_numpy().astype(float)) if len(nxt) else np.array([])
        dist=np.abs(dates-qd).astype(float) if len(k) else np.array([])
        def ew_mean(ds, vs, tau):
            if len(vs)==0: return g
            w=np.exp(-ds/tau)
            return float((w@vs)/(w.sum()+1e-9))
        # local both-side exponential means
        loc={}
        for tau in [3,7,14,30]:
            if len(vals):
                w=np.exp(-dist/tau)
                loc[f'local_tau{tau}']=float((w@vals)/(w.sum()+1e-9))
                loc[f'local_mass_tau{tau}']=float(w.sum())
            else:
                loc[f'local_tau{tau}']=g; loc[f'local_mass_tau{tau}']=0.0
            loc[f'past_tau{tau}']=ew_mean(prev_d, prev_vals[::-1] if False else prev_vals, tau)
            loc[f'next_tau{tau}']=ew_mean(next_d, next_vals, tau)
        # streak: consecutive same labels immediately before/after
        prev_last=float(prev_vals[-1]) if len(prev_vals) else g
        next_first=float(next_vals[0]) if len(next_vals) else g
        prev_streak=0
        if len(prev_vals):
            last=prev_vals[-1]
            for v in prev_vals[::-1]:
                if v==last: prev_streak+=1
                else: break
        next_streak=0
        if len(next_vals):
            first=next_vals[0]
            for v in next_vals:
                if v==first: next_streak+=1
                else: break
        nearest_val=g; nearest_dist=99.0
        if len(vals):
            j=int(np.argmin(dist)); nearest_val=float(vals[j]); nearest_dist=float(dist[j])
        row={
            'base_logit':float(logit(base_p[i])),
            'base_p':float(np.clip(base_p[i],0.02,0.98)),
            'global_mean':g,
            'subject_mean':safe_mean(vals,g),
            'n_anchor':float(len(vals)),
            'prev1':prev_last,
            'next1':next_first,
            'prev_dist':float(prev_d[-1]) if len(prev_d) else 99.0,
            'next_dist':float(next_d[0]) if len(next_d) else 99.0,
            'has_prev':float(len(prev_d)>0),
            'has_next':float(len(next_d)>0),
            'nearest_val':nearest_val,
            'nearest_dist':nearest_dist,
            'prev3_mean':safe_mean(prev_vals[-3:],g),
            'next3_mean':safe_mean(next_vals[:3],g),
            'prev_streak':float(prev_streak),
            'next_streak':float(next_streak),
            'dow':float(pd.Timestamp(d).dayofweek),
        }
        row.update(loc)
        rows.append(row)
    return pd.DataFrame(rows)

def make_pipe(C: float):
    return Pipeline([
        ('imp',SimpleImputer(strategy='median')),
        ('scale',StandardScaler()),
        ('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))
    ])

def run_eval():
    df=ts.load_all()
    train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    masks=[]
    for seed in range(6): masks.append(('testpattern',seed,ts.make_testpattern_mask(train,sample,seed),True))
    masks.append(('tail',0,ts.make_tail_mask(train),False))
    rows=[]; pred_rows=[]
    Cs=[0.01,0.03,0.1,0.3]
    for split,seed,val_mask,use_future in masks:
        known_mask=~val_mask
        known=train.loc[known_mask].copy(); val=train.loc[val_mask].copy()
        # full df for base model training on known -> val and known itself
        for y in LABELS:
            p_val_base=ts.base_predict_for(train, known_mask, val_mask, y, None)
            p_known_base=ts.base_predict_for(train, known_mask, known_mask, y, None)
            Xtr=temporal_feature_frame(known, known, y, p_known_base, exclude_self=True)
            Xva=temporal_feature_frame(known, val, y, p_val_base, exclude_self=False)
            ytr=known[y].astype(int).to_numpy(); yva=val[y].astype(int).to_numpy()
            base_loss=log_loss(yva,p_val_base,labels=[0,1])
            # fixed blend references from best w=0.2/w=0.3 omitted; compare calibrator only here.
            for C in Cs:
                pipe=make_pipe(C)
                pipe.fit(Xtr,ytr)
                p=np.clip(pipe.predict_proba(Xva)[:,1],0.02,0.98)
                rows.append({'split':split,'seed':seed,'target':y,'method':'learned_calibrator','C':C,'logloss':log_loss(yva,p,labels=[0,1]),'base_logloss':base_loss})
            # Also evaluate residual-safe convex blends of learned calibrator with base.
            pipe=make_pipe(0.03); pipe.fit(Xtr,ytr)
            pc=np.clip(pipe.predict_proba(Xva)[:,1],0.02,0.98)
            for w in [0.15,0.25,0.35,0.50]:
                p=np.clip((1-w)*p_val_base+w*pc,0.02,0.98)
                rows.append({'split':split,'seed':seed,'target':y,'method':f'base_plus_calib_w{w}','C':0.03,'logloss':log_loss(yva,p,labels=[0,1]),'base_logloss':base_loss})
    res=pd.DataFrame(rows)
    res.to_csv(EXP/'learned_temporal_calibrator_results.csv',index=False)
    print('wrote',EXP/'learned_temporal_calibrator_results.csv')
    for split in ['testpattern','tail']:
        print('\n###',split)
        sub=res[res.split.eq(split)]
        summ=sub.groupby(['target','method','C'])[['logloss','base_logloss']].mean().reset_index()
        out=[]
        for y,g in summ.groupby('target'):
            b=g.base_logloss.mean()
            best=g.sort_values('logloss').iloc[0]
            out.append({'target':y,'method':best.method,'C':best.C,'logloss':best.logloss,'base':b,'delta':best.logloss-b})
        print(pd.DataFrame(out).to_string(index=False))
    return df, train, sample, res

def make_submission(train, sample, full, res, name: str, allowed_targets: list[str]|None, max_w_method=True):
    known_mask=np.r_[np.ones(len(train),bool),np.zeros(len(sample),bool)]
    query_mask=np.r_[np.zeros(len(train),bool),np.ones(len(sample),bool)]
    sub=sample[ts.ID_COLS].copy().reset_index(drop=True)
    used={}; shifts=[]
    for y in LABELS:
        pbase=ts.base_predict_for(full,known_mask,query_mask,y,None)
        pknown=ts.base_predict_for(train,np.ones(len(train),bool),np.ones(len(train),bool),y,None)
        Xtr=temporal_feature_frame(train,train,y,pknown,exclude_self=True)
        Xte=temporal_feature_frame(train,sample,y,pbase,exclude_self=False)
        tp=res[res.split.eq('testpattern') & res.target.eq(y)]
        summ=tp.groupby(['method','C'])[['logloss','base_logloss']].mean().reset_index().sort_values('logloss')
        best=summ.iloc[0]
        base=summ.base_logloss.mean(); delta=float(best.logloss-base)
        # tail sanity same method
        tail=res[res.split.eq('tail') & res.target.eq(y) & res.method.eq(best.method) & res.C.eq(best.C)]
        tail_delta=float(tail.logloss.mean()-tail.base_logloss.mean()) if len(tail) else 0.0
        apply=(allowed_targets is None or y in allowed_targets) and delta < -0.003 and tail_delta <= 0.001
        p=pbase
        if apply:
            # Parse method.
            if best.method=='learned_calibrator':
                pipe=make_pipe(float(best.C)); pipe.fit(Xtr,train[y].astype(int).to_numpy())
                p=np.clip(pipe.predict_proba(Xte)[:,1],0.02,0.98)
            else:
                w=float(best.method.split('w')[-1])
                pipe=make_pipe(float(best.C)); pipe.fit(Xtr,train[y].astype(int).to_numpy())
                pc=np.clip(pipe.predict_proba(Xte)[:,1],0.02,0.98)
                p=np.clip((1-w)*pbase+w*pc,0.02,0.98)
        sub[y]=p
        d=np.abs(p-pbase)
        shifts.append({'target':y,'apply':bool(apply),'method':str(best.method),'C':float(best.C),'tp_delta':delta,'tail_delta':tail_delta,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(p,pbase)[0,1]) if d.max()>0 else 1.0})
        used[y]=shifts[-1].copy()
    sub.to_csv(OUT/f'{name}.csv',index=False)
    pd.DataFrame(shifts).to_csv(EXP/f'{name}_shift.csv',index=False)
    (EXP/f'{name}_used.json').write_text(json.dumps(used,indent=2),encoding='utf-8')
    print('\n### wrote',OUT/f'{name}.csv')
    print(pd.DataFrame(shifts).to_string(index=False))

def main():
    EXP.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    df, train, sample, res=run_eval()
    full=pd.concat([train,sample],ignore_index=True)
    # Conservative: only apply targets that pass local + tail sanity.
    make_submission(train,sample,full,res,'submission_learned_temporal_calibrator_conservative_prob',allowed_targets=None)
    # Hard-target only: avoid touching auxiliary targets unless they are proven by public diagnostics later.
    make_submission(train,sample,full,res,'submission_learned_temporal_calibrator_q1q2s4_prob',allowed_targets=['Q1','Q2','S4'])

if __name__=='__main__': main()
