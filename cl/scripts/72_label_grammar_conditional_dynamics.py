#!/usr/bin/env python3
"""Advanced label grammar / conditional dynamics analysis.

No submission files. This tests whether target relations are direct mechanisms,
latent common-cause artifacts, or temporal interpolation rules.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
EXP = ROOT / 'experiments'
LABELS = ['Q1','Q2','Q3','S1','S2','S3','S4']
IDS = ['subject_id','sleep_date','lifelog_date']
EXP.mkdir(exist_ok=True)


def entropy(vals):
    vals = np.asarray(vals, int)
    if len(vals)==0: return 0.0
    ps = np.bincount(vals, minlength=int(vals.max())+1) / len(vals)
    ps = ps[ps>0]
    return float(-(ps*np.log2(ps)).sum())


def mi_binary(a,b):
    a=np.asarray(a,int); b=np.asarray(b,int)
    return entropy(a)+entropy(b)-entropy(a*2+b)


def cmi_binary(a,b,z):
    a=np.asarray(a,int); b=np.asarray(b,int); z=np.asarray(z)
    out=0.0
    for val in pd.unique(z):
        m=(z==val)
        if m.sum()==0: continue
        out += (m.mean())*mi_binary(a[m], b[m])
    return float(out)


def main():
    train = pd.read_csv(DATA/'ch2026_metrics_train.csv', parse_dates=['sleep_date','lifelog_date']).sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    states = pd.read_csv(EXP/'advanced_ds_row_latent_states.csv', parse_dates=['sleep_date','lifelog_date'])
    train = train.merge(states[IDS+['latent_state','state_confidence']], on=IDS, how='left')

    # 1. Exact label grammar: which 7-bit patterns dominate?
    pat = train[LABELS].astype(int).astype(str).agg(''.join, axis=1)
    pat_df = train[IDS+LABELS+['latent_state']].copy()
    pat_df['pattern'] = pat
    pattern_summary = pat_df.groupby('pattern').agg(
        n=('pattern','count'),
        share=('pattern', lambda s: len(s)/len(pat_df)),
        dominant_state=('latent_state', lambda s: int(pd.Series(s).mode().iloc[0])),
        state_purity=('latent_state', lambda s: float(pd.Series(s).value_counts(normalize=True).iloc[0])),
        subjects=('subject_id','nunique'),
    ).reset_index().sort_values(['n','subjects'], ascending=[False,False])
    pattern_summary.to_csv(EXP/'advanced_ds_label_pattern_grammar.csv', index=False)

    # 2. Pairwise MI: raw vs condition on latent state and S2.
    rows=[]
    for a,b in combinations(LABELS,2):
        raw=mi_binary(train[a], train[b])
        c_state=cmi_binary(train[a],train[b],train['latent_state'])
        c_s2=cmi_binary(train[a],train[b],train['S2']) if a!='S2' and b!='S2' else np.nan
        rows.append({
            'a':a,'b':b,
            'raw_mi_bits':raw,
            'cmi_given_latent_state_bits':c_state,
            'fraction_remaining_after_state':c_state/raw if raw>1e-9 else np.nan,
            'cmi_given_S2_bits':c_s2,
            'fraction_remaining_after_S2':c_s2/raw if raw>1e-9 and not np.isnan(c_s2) else np.nan,
        })
    mi = pd.DataFrame(rows).sort_values('raw_mi_bits', ascending=False)
    mi.to_csv(EXP/'advanced_ds_label_conditional_mi.csv', index=False)

    # 3. Interpolation grammar: current y given immediate previous/next train labels.
    dyn=[]
    for y in LABELS:
        for sid, sub in train.sort_values(['subject_id','sleep_date']).groupby('subject_id'):
            sub = sub.reset_index(drop=True)
            dates = sub.sleep_date.values.astype('datetime64[D]').astype(int)
            arr = sub[y].astype(int).to_numpy()
            states_arr = sub.latent_state.astype(int).to_numpy()
            for i in range(1,len(sub)-1):
                prev_gap = int(dates[i]-dates[i-1]); next_gap=int(dates[i+1]-dates[i])
                dyn.append({
                    'target': y, 'subject_id': sid, 'sleep_date': sub.loc[i,'sleep_date'],
                    'y': int(arr[i]), 'prev_y': int(arr[i-1]), 'next_y': int(arr[i+1]),
                    'prev_next_code': f'{arr[i-1]}{arr[i+1]}',
                    'prev_gap_d': prev_gap, 'next_gap_d': next_gap,
                    'latent_state': int(states_arr[i]),
                    'prev_state': int(states_arr[i-1]), 'next_state': int(states_arr[i+1]),
                    'state_stable_neighbors': bool(states_arr[i-1]==states_arr[i+1]),
                })
    dyn = pd.DataFrame(dyn)
    dyn.to_csv(EXP/'advanced_ds_neighbor_dynamics_rows.csv', index=False)
    interp = dyn.groupby(['target','prev_next_code']).agg(
        n=('y','count'),
        p_y1=('y','mean'),
        mean_prev_gap=('prev_gap_d','mean'),
        mean_next_gap=('next_gap_d','mean'),
    ).reset_index()
    # Add log-odds separation between agreeing neighbors.
    sep=[]
    for y,g in interp.groupby('target'):
        d = {r.prev_next_code: r for _,r in g.iterrows()}
        p00 = float(d['00'].p_y1) if '00' in d else np.nan
        p11 = float(d['11'].p_y1) if '11' in d else np.nan
        p01 = float(d['01'].p_y1) if '01' in d else np.nan
        p10 = float(d['10'].p_y1) if '10' in d else np.nan
        sep.append({
            'target':y,
            'p_y1_given_00':p00,
            'p_y1_given_11':p11,
            'p_y1_given_conflict_avg':np.nanmean([p01,p10]),
            'agree_neighbor_spread':p11-p00,
            'conflict_midpoint_bias':np.nanmean([p01,p10]) - 0.5*(p00+p11),
        })
    interp.to_csv(EXP/'advanced_ds_neighbor_interpolation_table.csv', index=False)
    sep = pd.DataFrame(sep).sort_values('agree_neighbor_spread', ascending=False)
    sep.to_csv(EXP/'advanced_ds_neighbor_interpolation_strength.csv', index=False)

    # 4. State persistence vs label persistence.
    pers=[]
    for sid, sub in train.sort_values(['subject_id','sleep_date']).groupby('subject_id'):
        sub=sub.reset_index(drop=True)
        if len(sub)<2: continue
        pers.append({'subject_id':sid,'variable':'latent_state','same_next_rate':float((sub.latent_state.to_numpy()[1:]==sub.latent_state.to_numpy()[:-1]).mean())})
        for y in LABELS:
            arr=sub[y].astype(int).to_numpy()
            pers.append({'subject_id':sid,'variable':y,'same_next_rate':float((arr[1:]==arr[:-1]).mean())})
    pers=pd.DataFrame(pers)
    pers_sum=pers.groupby('variable').agg(mean_same_next_rate=('same_next_rate','mean'),std=('same_next_rate','std')).reset_index().sort_values('mean_same_next_rate', ascending=False)
    pers.to_csv(EXP/'advanced_ds_persistence_by_subject.csv', index=False)
    pers_sum.to_csv(EXP/'advanced_ds_persistence_summary.csv', index=False)

    # 5. Report.
    top_patterns = pattern_summary.head(16)
    top_mi = mi.head(14)
    lines=[]
    lines += ['# Advanced Label Grammar & Conditional Dynamics', '']
    lines += ['## 1. Exact 7-bit label grammar', '', top_patterns.to_string(index=False, float_format=lambda x:f'{x:.3f}'), '']
    lines += ['## 2. Pairwise label dependence: raw vs conditioned', '', top_mi.to_string(index=False, float_format=lambda x:f'{x:.4f}'), '']
    lines += ['Interpretation: if raw MI is high but CMI given latent_state collapses, the relation is mostly common latent-state, not necessarily direct target-target causality. If CMI remains high, there is residual pair-specific structure.', '']
    lines += ['## 3. Neighbor interpolation grammar', '', sep.to_string(index=False, float_format=lambda x:f'{x:.3f}'), '']
    lines += ['## 4. Persistence summary', '', pers_sum.to_string(index=False, float_format=lambda x:f'{x:.3f}'), '']
    lines += ['## 5. Output files', '']
    for name in ['advanced_ds_label_pattern_grammar.csv','advanced_ds_label_conditional_mi.csv','advanced_ds_neighbor_dynamics_rows.csv','advanced_ds_neighbor_interpolation_table.csv','advanced_ds_neighbor_interpolation_strength.csv','advanced_ds_persistence_by_subject.csv','advanced_ds_persistence_summary.csv']:
        lines.append(f'- `experiments/{name}`')
    report='\n'.join(lines)+'\n'
    (EXP/'advanced_ds_label_grammar_report.md').write_text(report, encoding='utf-8')
    print(report[:5000])
    print('\n[written]', EXP/'advanced_ds_label_grammar_report.md')

if __name__ == '__main__':
    main()
