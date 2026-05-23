#!/usr/bin/env python3
"""Masked validation for 0.5-or-bust moonshot graph candidates.

Recreates candidate logic inside train-only masked splits, so we can compare:
- base feature model
- crude temporal anchors w02/w03
- raw graph moonshots

This is not a public-LB oracle, but it tells whether the moonshot is merely large
or actually beats the anchor-like smoother on held-out train rows.
"""
from __future__ import annotations
import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'experiments'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']

# Reuse the heavy utilities from script 67.
import sys
sys.path.insert(0, str(ROOT/'scripts'))
import importlib.util
spec=importlib.util.spec_from_file_location('big67', ROOT/'scripts'/'67_big_swing_all_experiments.py')
big67=importlib.util.module_from_spec(spec); spec.loader.exec_module(big67)


def temporal_label_smooth(known, query, target, tau=14, alpha=5, future=True):
    y=known[target].astype(float).to_numpy()
    g=float(np.mean(y))
    out=np.zeros(len(query),float)
    for sid, qsub in query.groupby('subject_id'):
        k=known[known.subject_id.astype(str).eq(str(sid))]
        if len(k)==0:
            out[query.index.get_indexer(qsub.index)]=g; continue
        kd=k.sleep_date.values.astype('datetime64[D]').astype(int)
        qd=qsub.sleep_date.values.astype('datetime64[D]').astype(int)
        dist=np.abs(qd[:,None]-kd[None,:]).astype(float)
        if not future:
            dist=np.where(kd[None,:] < qd[:,None], dist, np.inf)
        w=np.exp(-dist/tau); w[~np.isfinite(w)]=0
        p=(w @ k[target].astype(float).to_numpy() + alpha*g)/(w.sum(axis=1)+alpha)
        out[query.index.get_indexer(qsub.index)] = np.clip(p,.02,.98)
    return out


def clip(p):
    return np.clip(np.asarray(p,float),.02,.98)
def logit(p):
    p=clip(p)
    return np.log(p/(1-p))
def sig(x): return 1/(1+np.exp(-np.asarray(x)))
def sharpen(p, center, temp=.70):
    return clip(sig(logit(center)+(logit(p)-logit(center))/temp))


def make_candidate(name, base, anchor, graph, yprev):
    c=anchor.copy()
    if name=='anchor_w02_noq3':
        return c
    if name=='w03_noq3_q2w02':
        c2=anchor.copy()
        for y in ['Q1','S1','S2','S3','S4']:
            c2[y]=np.clip(.70*base[y]+.30*graph[f'temporal_{y}'],.02,.98)  # temporal proxy, not graph
        c2['Q2']=anchor['Q2']; c2['Q3']=base['Q3']
        return c2
    if name=='moon_graph_raw_noq3_q2half':
        for y in ['Q1','S1','S2','S3','S4']:
            c[y]=graph[y]
        c['Q2']=np.clip(.50*anchor['Q2']+.50*graph['Q2'],.02,.98); c['Q3']=base['Q3']
        return c
    if name=='moon_graph_raw_all_noq3':
        for y in ['Q1','Q2','S1','S2','S3','S4']:
            c[y]=graph[y]
        c['Q3']=base['Q3']
        return c
    if name=='moon_family_best_only':
        for y in ['Q1','S1','S4']:
            c[y]=graph[y]
        # validation version has no episode/ssl heads here; use raw graph for S2/S3 as proxy.
        c['S2']=graph['S2']; c['S3']=graph['S3']
        c['Q2']=base['Q2']; c['Q3']=base['Q3']
        return c
    if name=='moon_graph_raw_sharpened':
        for y in ['Q1','S1','S2','S3','S4']:
            c[y]=sharpen(graph[y], yprev[y], temp=.70)
        c['Q2']=sharpen(np.clip(.50*anchor['Q2']+.50*graph['Q2'],.02,.98), yprev['Q2'], temp=.85)
        c['Q3']=base['Q3']
        return c
    if name=='moon_optimized_targetwise':
        c['Q1']=base['Q1']  # validation proxy for w03-like conservative Q1
        c['Q2']=graph['Q2']; c['Q3']=base['Q3']
        c['S1']=graph['S1']; c['S2']=sharpen(graph['S2'], yprev['S2'], temp=.70); c['S3']=sharpen(graph['S3'], yprev['S3'], temp=.70); c['S4']=base['S4']
        return c
    if name=='moon_optimized_keep_s4raw':
        c['Q1']=base['Q1']; c['Q2']=graph['Q2']; c['Q3']=base['Q3']
        c['S1']=graph['S1']; c['S2']=sharpen(graph['S2'], yprev['S2'], temp=.70); c['S3']=sharpen(graph['S3'], yprev['S3'], temp=.70); c['S4']=graph['S4']
        return c
    if name=='moon_validated_block':
        c['Q1']=anchor['Q1']; c['Q2']=graph['Q2']; c['Q3']=base['Q3']
        c['S1']=graph['S1']; c['S2']=sharpen(graph['S2'], yprev['S2'], temp=.70); c['S3']=sharpen(graph['S3'], yprev['S3'], temp=.70); c['S4']=anchor['S4']
        return c
    if name=='moon_raw_all_antifix_q1s4':
        for y in ['Q1','Q2','S1','S2','S3','S4']:
            c[y]=graph[y]
        c['Q1']=clip(.50*graph['Q1']+.50*base['Q1'])
        c['S4']=clip(.50*graph['S4']+.50*base['S4'])
        c['S2']=sharpen(graph['S2'], yprev['S2'], temp=.70); c['S3']=sharpen(graph['S3'], yprev['S3'], temp=.70)
        c['Q3']=base['Q3']
        return c
    if name=='moon_validated_block_sharp':
        c['Q1']=base['Q1']; c['Q3']=base['Q3']; c['S4']=base['S4']
        for y,temp in [('Q2',.85),('S1',.80),('S2',.65),('S3',.65)]:
            c[y]=sharpen(graph[y], yprev[y], temp=temp)
        return c
    raise ValueError(name)


def main():
    df=big67.load_base_table()
    train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    graph_cols=big67.numeric_cols(train, contains=("sleep", "quiet", "screen", "steps", "activity", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "sslcl", "dyncl"), max_cols=500)
    all_feature_cols=big67.numeric_cols(train, contains=("sleep", "quiet", "screen", "steps", "activity", "hr_", "gps_", "app_", "wifi_", "ble_", "amb_", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "sslcl", "dyncl"), max_cols=650)
    masks=big67.make_testpattern_masks(train, sample, seeds=range(10))
    cand_names=['anchor_w02_noq3','w03_noq3_q2w02','moon_graph_raw_noq3_q2half','moon_graph_raw_all_noq3','moon_family_best_only','moon_graph_raw_sharpened','moon_optimized_targetwise','moon_optimized_keep_s4raw','moon_validated_block','moon_raw_all_antifix_q1s4','moon_validated_block_sharp']
    rows=[]
    pred_summ=[]
    for split, val_mask, future in masks:
        known_mask=~val_mask
        known=train.loc[known_mask].copy().reset_index(drop=True)
        val=train.loc[val_mask].copy().reset_index(drop=True)
        yprev={y:float(known[y].mean()) for y in LABELS}
        base=val[['subject_id','sleep_date','lifelog_date']].copy().reset_index(drop=True)
        graph=base.copy()
        anchor=base.copy()
        # targetwise predictions
        for y in LABELS:
            # Feature base: compact generic logreg, sufficient for relative moonshot validation.
            try:
                base[y]=big67.fit_predict_logreg(train, all_feature_cols, y, known_mask, val_mask, k=80, C=0.03)
            except Exception:
                base[y]=yprev[y]
            # Temporal anchor w02 proxy.
            ts=temporal_label_smooth(known, val, y, tau=14, alpha=5, future=future)
            anchor[y]=np.clip(.80*base[y]+.20*ts,.02,.98)
            if y=='Q3':
                anchor[y]=base[y]
            graph[y]=big67.graph_predict(train, known_mask, val_mask, y, graph_cols, k_same=12, k_global=45, tau=14, same_w=.75, feat_w=.25, alpha=2.5, future=future)
            graph[f'temporal_{y}']=ts
        for name in cand_names:
            pred=make_candidate(name, base, anchor, graph, yprev)
            losses=[]
            for y in LABELS:
                loss=log_loss(val[y].astype(int), pred[y], labels=[0,1])
                losses.append(loss)
                rows.append({'split':split,'candidate':name,'target':y,'logloss':loss,'n':len(val),'mean_pred':float(pred[y].mean()),'true_rate':float(val[y].mean())})
            rows.append({'split':split,'candidate':name,'target':'ALL','logloss':float(np.mean(losses)),'n':len(val),'mean_pred':np.nan,'true_rate':np.nan})
        # movement summaries on val vs anchor
        for name in cand_names:
            pred=make_candidate(name, base, anchor, graph, yprev)
            if name=='anchor_w02_noq3': continue
            for y in LABELS:
                d=np.abs(pred[y].to_numpy(float)-anchor[y].to_numpy(float))
                pred_summ.append({'split':split,'candidate':name,'target':y,'mean_abs_vs_anchor':float(d.mean()),'max_abs_vs_anchor':float(d.max())})
    res=pd.DataFrame(rows)
    mov=pd.DataFrame(pred_summ)
    res.to_csv(EXP/'moonshot_masked_validation_results.csv', index=False)
    mov.to_csv(EXP/'moonshot_masked_validation_movement.csv', index=False)
    allsum=res[res.target.eq('ALL')].groupby('candidate')['logloss'].agg(['mean','std','count']).reset_index().sort_values('mean')
    bytarget=res[~res.target.eq('ALL')].groupby(['candidate','target'])['logloss'].mean().reset_index()
    # delta against anchor and w03 proxy
    anchor_mean=float(allsum.loc[allsum.candidate.eq('anchor_w02_noq3'),'mean'].iloc[0])
    w03_mean=float(allsum.loc[allsum.candidate.eq('w03_noq3_q2w02'),'mean'].iloc[0])
    allsum['delta_vs_anchor']=allsum['mean']-anchor_mean
    allsum['delta_vs_w03proxy']=allsum['mean']-w03_mean
    allsum.to_csv(EXP/'moonshot_masked_validation_summary.csv', index=False)
    lines=['# Moonshot masked validation report','','## Overall mean logloss',allsum.to_string(index=False,float_format=lambda x:f'{x:.6f}'),'','## By target mean logloss',bytarget.pivot(index='target',columns='candidate',values='logloss').to_string(float_format=lambda x:f'{x:.6f}'),'','## Mean movement vs anchor',mov.groupby(['candidate','target'])['mean_abs_vs_anchor'].mean().reset_index().to_string(index=False,float_format=lambda x:f'{x:.6f}')]
    (EXP/'moonshot_masked_validation_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('\n'.join(lines[:8]))
    print(allsum.to_string(index=False))

if __name__=='__main__': main()
