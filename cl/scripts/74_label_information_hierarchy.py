#!/usr/bin/env python3
"""Information hierarchy decomposition for lifelog labels.

Question: for each target, which source explains the label most?
- subject identity / subject prevalence
- latent label state
- temporal neighbor labels
- other labels in the same row
- raw modality family signals

This is diagnostic only; some sources are oracle-like and not submission-safe.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; EXP=ROOT/'experiments'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']; IDS=['subject_id','sleep_date','lifelog_date']
EXP.mkdir(exist_ok=True)


def h_binary(p):
    p=np.clip(float(p),1e-12,1-1e-12)
    return float(-(p*np.log2(p)+(1-p)*np.log2(1-p)))


def cond_entropy(df, y, zcols, min_count=1, alpha=0.5):
    # Smoothed empirical H(Y|Z) to avoid zero entropy for tiny groups.
    base=float(df[y].mean())
    total=len(df); out=0.0; eff_groups=0
    for _,g in df.groupby(zcols, dropna=False):
        n=len(g)
        if n < min_count: continue
        p=(g[y].sum()+alpha*base)/(n+alpha)
        out += (n/total)*h_binary(p)
        eff_groups += 1
    return float(out), int(eff_groups)


def make_neighbor_codes(train):
    out=train[IDS+LABELS+['latent_state']].copy()
    for y in LABELS:
        out[f'{y}_prev']='NA'; out[f'{y}_next']='NA'; out[f'{y}_prevnext']='NA'; out[f'{y}_gapbucket']='NA'
    for sid,sub in train.sort_values(['subject_id','sleep_date']).groupby('subject_id'):
        idx=sub.index.to_numpy(); dates=sub.sleep_date.values.astype('datetime64[D]').astype(int)
        for y in LABELS:
            arr=sub[y].astype(int).to_numpy()
            for pos,i in enumerate(idx):
                if pos>0:
                    out.loc[i,f'{y}_prev']=str(arr[pos-1])
                    pg=dates[pos]-dates[pos-1]
                else: pg=np.nan
                if pos<len(idx)-1:
                    out.loc[i,f'{y}_next']=str(arr[pos+1])
                    ng=dates[pos+1]-dates[pos]
                else: ng=np.nan
                out.loc[i,f'{y}_prevnext']=str(out.loc[i,f'{y}_prev'])+str(out.loc[i,f'{y}_next'])
                nearest=np.nanmin([pg,ng]) if not (np.isnan(pg) and np.isnan(ng)) else np.nan
                if np.isnan(nearest): b='edge'
                elif nearest<=1: b='1d'
                elif nearest<=3: b='2-3d'
                elif nearest<=7: b='4-7d'
                else: b='8+d'
                out.loc[i,f'{y}_gapbucket']=b
    return out


def main():
    train=pd.read_csv(DATA/'ch2026_metrics_train.csv',parse_dates=['sleep_date','lifelog_date']).sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    states=pd.read_csv(EXP/'advanced_ds_row_latent_states.csv',parse_dates=['sleep_date','lifelog_date'])
    train=train.merge(states[IDS+['latent_state','state_confidence']],on=IDS,how='left')
    work=make_neighbor_codes(train)
    # Same-row label pattern without target.
    for y in LABELS:
        others=[x for x in LABELS if x!=y]
        work[f'{y}_other_pattern']=work[others].astype(int).astype(str).agg(''.join,axis=1)
        if y in ['Q2','Q3']:
            other='Q3' if y=='Q2' else 'Q2'
            work[f'{y}_pair_axis']=work[[other,f'{y}_prev',f'{y}_next']].astype(str).agg('_'.join,axis=1)
        else:
            work[f'{y}_pair_axis']='NA'

    rows=[]
    for y in LABELS:
        Hy=h_binary(work[y].mean())
        specs={
            'subject_id':['subject_id'],
            'latent_state':['latent_state'],
            'subject+state':['subject_id','latent_state'],
            'prev_only':[f'{y}_prev'],
            'next_only':[f'{y}_next'],
            'prevnext':[f'{y}_prevnext'],
            'prevnext+gap':[f'{y}_prevnext',f'{y}_gapbucket'],
            'subject+prevnext':['subject_id',f'{y}_prevnext'],
            'same_row_other_labels':[f'{y}_other_pattern'],
        }
        if y in ['Q2','Q3']:
            specs['Q2Q3_pair_axis']=[f'{y}_pair_axis']
        for name,zcols in specs.items():
            H,g=cond_entropy(work,y,zcols,alpha=1.0)
            rows.append({'target':y,'source':name,'H_y_bits':Hy,'H_y_given_source_bits':H,'info_gain_bits':Hy-H,'explained_entropy_share':(Hy-H)/Hy if Hy else np.nan,'n_groups':g})
    decomp=pd.DataFrame(rows).sort_values(['target','info_gain_bits'],ascending=[True,False])
    decomp.to_csv(EXP/'deeper_label_information_hierarchy.csv',index=False)

    # Synergy/redundancy pairs between selected sources: I(Y;A,B)-max(I(Y;A),I(Y;B)).
    sy=[]
    for y in LABELS:
        base=decomp[decomp.target.eq(y)].set_index('source')
        source_cols={
            'subject':['subject_id'],
            'state':['latent_state'],
            'prevnext':[f'{y}_prevnext'],
            'other_labels':[f'{y}_other_pattern'],
        }
        for a,b in combinations(source_cols,2):
            H,g=cond_entropy(work,y,source_cols[a]+source_cols[b],alpha=1.0)
            keymap={'subject':'subject_id','state':'latent_state','prevnext':'prevnext','other_labels':'same_row_other_labels'}
            joint=base['H_y_bits'].iloc[0]-H
            ia=base.loc[keymap[a],'info_gain_bits']
            ib=base.loc[keymap[b],'info_gain_bits']
            sy.append({'target':y,'source_a':a,'source_b':b,'joint_info_bits':joint,'max_single_info_bits':max(ia,ib),'extra_over_best_single_bits':joint-max(ia,ib),'n_groups':g})
    syn=pd.DataFrame(sy).sort_values(['target','extra_over_best_single_bits'],ascending=[True,False])
    syn.to_csv(EXP/'deeper_label_information_synergy.csv',index=False)

    top=decomp.groupby('target').head(6)
    syntop=syn.groupby('target').head(4)
    lines=[]
    lines+=['# Deeper Label Information Hierarchy','']
    lines+=['## 1. Per-target information sources','', 'Higher info_gain_bits means that source reduces more uncertainty about the target. Some sources are oracle-like diagnostics, not submission-safe.', '', top.to_string(index=False,float_format=lambda x:f'{x:.3f}'),'']
    lines+=['## 2. Source synergy','', 'extra_over_best_single_bits > 0 means the pair adds structure beyond the stronger single source.', '', syntop.to_string(index=False,float_format=lambda x:f'{x:.3f}'),'']
    lines+=['## 3. Interpretation guide','', '- `same_row_other_labels` high: target is mostly part of a multi-label grammar/common state.', '- `prevnext` high: interpolation target.', '- `subject_id` high: stable person-specific prevalence dominates.', '- `state` high but feature state-pred weak: labels have grammar but current sensors do not recover it well.', '- `extra_over_best_single` high for subject+prevnext: temporal behavior is personalized, not globally shared.', '']
    lines+=['## 4. Output files','','- `experiments/deeper_label_information_hierarchy.csv`','- `experiments/deeper_label_information_synergy.csv`']
    report='\n'.join(lines)+'\n'
    (EXP/'deeper_label_information_hierarchy_report.md').write_text(report,encoding='utf-8')
    print(report)
    print('[written]',EXP/'deeper_label_information_hierarchy_report.md')

if __name__=='__main__':
    main()
