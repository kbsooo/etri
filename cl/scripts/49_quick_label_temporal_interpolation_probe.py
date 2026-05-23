#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ['Q1','Q2','Q3','S1','S2','S3','S4']

def clip(p): return np.clip(p, 0.02, 0.98)

def make_interleaved_mask(df, rng, frac=0.36):
    mask = np.zeros(len(df), dtype=bool)
    for sid, idx in df.groupby('subject_id').groups.items():
        order = df.loc[list(idx)].sort_values('sleep_date').index.to_numpy()
        n = max(3, int(round(len(order)*frac)))
        ranks = np.arange(len(order)); prob = (0.5 + ranks/max(1,len(order)-1)); prob/=prob.sum()
        chosen = rng.choice(order, size=min(n, len(order)-2), replace=False, p=prob)
        mask[df.index.get_indexer(chosen)] = True
    return mask

def make_tail_mask(df, frac=0.36):
    mask = np.zeros(len(df), dtype=bool)
    for sid, sub in df.groupby('subject_id'):
        chosen = sub.sort_values('sleep_date').tail(max(3, int(round(len(sub)*frac)))).index
        mask[df.index.get_indexer(chosen)] = True
    return mask

def eval_one(df, mask, use_future, tau, alpha):
    known=df.loc[~mask].copy(); val=df.loc[mask].copy()
    preds={t:np.zeros(len(val),float) for t in TARGETS}
    for t in TARGETS:
        gmean=known[t].mean()
        for sid, qsub in val.groupby('subject_id'):
            k=known[known.subject_id==sid]
            if len(k)==0:
                preds[t][val.index.get_indexer(qsub.index)] = gmean; continue
            kd=k.sleep_date.values.astype('datetime64[D]').astype(int)
            qd=qsub.sleep_date.values.astype('datetime64[D]').astype(int)
            dist=np.abs(qd[:,None]-kd[None,:]).astype(float)
            if not use_future:
                dist=np.where(kd[None,:] < qd[:,None], dist, np.inf)
            w=np.exp(-dist/tau)
            w[~np.isfinite(w)] = 0
            denom=w.sum(axis=1)+alpha
            p=(w @ k[t].values + alpha*gmean)/denom
            preds[t][val.index.get_indexer(qsub.index)] = clip(p)
    losses=[log_loss(val[t], preds[t], labels=[0,1]) for t in TARGETS]
    return float(np.mean(losses)), losses

def main():
    df=pd.read_csv(ROOT/'data/ch2026_metrics_train.csv', parse_dates=['sleep_date','lifelog_date']).sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    rows=[]
    taus=[3,7,14,30]; alphas=[1,5,10]
    masks=[]
    for seed in range(8): masks.append(('interleaved',seed,make_interleaved_mask(df,np.random.default_rng(seed))))
    masks.append(('tail',0,make_tail_mask(df)))
    for split,seed,mask in masks:
        for use_future in ([True,False] if split=='interleaved' else [False,True]):
            for tau in taus:
                for alpha in alphas:
                    mean,losses=eval_one(df,mask,use_future,tau,alpha)
                    rows.append({'split':split,'seed':seed,'use_future':use_future,'tau':tau,'alpha':alpha,'mean':mean, **{f'logloss_{t}':losses[i] for i,t in enumerate(TARGETS)}})
    res=pd.DataFrame(rows)
    out=ROOT/'experiments/quick_label_temporal_interpolation_probe.csv'; res.to_csv(out,index=False)
    print('wrote',out)
    for name,cond in [('interleaved future allowed',(res.split=='interleaved')&(res.use_future)),('interleaved past only',(res.split=='interleaved')&(~res.use_future)),('tail',(res.split=='tail'))]:
        print('\n###',name)
        g=res[cond].groupby(['tau','alpha'])[['mean']+[f'logloss_{t}' for t in TARGETS]].mean().reset_index().sort_values('mean')
        print(g.head(8).to_string(index=False))
if __name__=='__main__': main()
