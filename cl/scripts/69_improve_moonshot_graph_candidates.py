#!/usr/bin/env python3
"""Improve the 0.5-or-bust raw graph candidate.

Uses the moonshot masked-validation finding:
- raw graph helps Q2/S1/S2/S3 strongly
- raw graph hurts Q1 and slightly hurts S4
- sharpening helped S2/S3 and overall in validation, but can be calibration-risky

Creates target-routed candidates around `submission_moonshot_graph_raw_all_noq3_prob.csv`.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; EXP=ROOT/'experiments'; DATA=ROOT/'data'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']; IDS=['subject_id','sleep_date','lifelog_date']

def clip(x): return np.clip(np.asarray(x,float),.02,.98)
def logit(p):
    p=clip(p); return np.log(p/(1-p))
def sig(x): return 1/(1+np.exp(-np.asarray(x)))
def sharpen(p, center, temp=.70): return clip(sig(logit(center)+(logit(p)-logit(center))/temp))
def read(name): return pd.read_csv(OUT/name)
def save(name, df, refs, note):
    df.to_csv(OUT/name,index=False)
    rows=[]
    for refname,ref in refs.items():
        if not df[IDS].astype(str).equals(ref[IDS].astype(str)): raise ValueError(f'id mismatch {refname}')
        for y in LABELS:
            d=np.abs(df[y].to_numpy(float)-ref[y].to_numpy(float))
            rows.append({'file':name,'ref':refname,'target':y,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'p95_abs_delta':float(np.quantile(d,.95)),'max_abs_delta':float(d.max()),'mean_prob_shift':float(df[y].mean()-ref[y].mean()),'corr':float(np.corrcoef(df[y],ref[y])[0,1]) if d.max()>0 else 1.0})
    pd.DataFrame(rows).to_csv(EXP/f'{name[:-4]}_shift.csv',index=False)
    (EXP/f'{name[:-4]}_notes.json').write_text(json.dumps(note|{'file':str(OUT/name)},ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    train=pd.read_csv(DATA/'ch2026_metrics_train.csv')
    prev={y:float(train[y].mean()) for y in LABELS}
    base=read('submission_base_v4_replicate_prob.csv')
    anchor=read('submission_meta_anchor_w02_noq3_prob.csv')
    w03=read('submission_lbdiag_w03_noq3_q2w02_prob.csv')
    raw=read('submission_moonshot_graph_raw_all_noq3_prob.csv')
    q2half=read('submission_moonshot_graph_raw_noq3_q2half_prob.csv')
    sharp=read('submission_moonshot_graph_raw_sharpened_prob.csv')
    graph=pd.read_csv(EXP/'big_swing_graph_raw_predictions.csv')
    refs={'base':base,'anchor':anchor,'w03':w03,'raw_all_noq3':raw,'sharp':sharp}

    # A: validation-targetwise winner from masked validation:
    # Q1=w03, Q2=raw graph, Q3=base, S1=raw graph, S2=sharpened graph, S3=sharpened graph, S4=w03.
    c=anchor.copy()
    c['Q1']=w03['Q1']
    c['Q2']=raw['Q2']
    c['Q3']=base['Q3']
    c['S1']=raw['S1']
    c['S2']=sharp['S2']
    c['S3']=sharp['S3']
    c['S4']=w03['S4']
    save('submission_moonshot_optimized_targetwise_prob.csv', c, refs, {
        'family':'improved_0.5_or_bust_graph',
        'description':'Targetwise masked-validation winner: Q1/S4 w03, Q2/S1 raw graph, S2/S3 sharpened graph, Q3 base.',
        'rationale':'Removes raw graph from validation-negative Q1/S4 while keeping high-upside graph on Q2/S targets.'
    })

    # B: more aggressive version: keep S4 raw graph despite validation slight harm, because S4 may matter on public; Q1 still w03.
    c=anchor.copy()
    c['Q1']=w03['Q1']; c['Q2']=raw['Q2']; c['Q3']=base['Q3']
    c['S1']=raw['S1']; c['S2']=sharp['S2']; c['S3']=sharp['S3']; c['S4']=raw['S4']
    save('submission_moonshot_optimized_keep_s4raw_prob.csv', c, refs, {
        'family':'improved_0.5_or_bust_graph',
        'description':'Targetwise winner but keeps S4 raw graph for larger moonshot movement.',
        'rationale':'S4 validation harm was small; preserving raw S4 gives more upside if public S4 follows graph state.'
    })

    # C: pure strong validated block: only Q2/S1/S2/S3 move to graph/sharp; Q1/S4/Q3 frozen near conservative sources.
    c=anchor.copy()
    c['Q1']=anchor['Q1']; c['Q2']=raw['Q2']; c['Q3']=base['Q3']
    c['S1']=raw['S1']; c['S2']=sharp['S2']; c['S3']=sharp['S3']; c['S4']=anchor['S4']
    save('submission_moonshot_validated_block_prob.csv', c, refs, {
        'family':'improved_0.5_or_bust_graph',
        'description':'Only validation-positive block Q2/S1/S2/S3 uses raw/sharpened graph; Q1/S4/Q3 conservative.',
        'rationale':'Best risk-adjusted form, but less likely to reach 0.5 than broader moonshot.'
    })

    # D: all-noq3 plus targeted anti-fix: raw graph for all non-Q3, but pull Q1 and S4 halfway back to w03.
    c=raw.copy()
    c['Q1']=clip(.50*raw['Q1']+.50*w03['Q1'])
    c['S4']=clip(.50*raw['S4']+.50*w03['S4'])
    c['S2']=sharp['S2']; c['S3']=sharp['S3']
    c['Q3']=base['Q3']
    save('submission_moonshot_raw_all_antifix_q1s4_prob.csv', c, refs, {
        'family':'improved_0.5_or_bust_graph',
        'description':'Raw all-noQ3, but Q1/S4 halfway back to w03 and S2/S3 sharpened.',
        'rationale':'Keeps most moonshot movement while addressing the two validation-negative targets.'
    })

    # E: prevalence-shifted moonshot for 0.5 attempt: validated block plus mild sharpening on Q2/S1/S2/S3.
    c=anchor.copy()
    c['Q1']=w03['Q1']; c['Q3']=base['Q3']; c['S4']=w03['S4']
    for y,temp in [('Q2',.85),('S1',.80),('S2',.65),('S3',.65)]:
        c[y]=sharpen(raw[y] if y not in ['S2','S3'] else sharp[y], prev[y], temp=temp)
    save('submission_moonshot_validated_block_sharp_prob.csv', c, refs, {
        'family':'improved_0.5_or_bust_graph',
        'description':'Validated Q2/S1/S2/S3 block with extra sharpening; Q1/S4 w03, Q3 base.',
        'rationale':'Closest to validation-best sharpening pattern but restricted to targets where graph helped.'
    })

    # Summary.
    rows=[]
    for p in sorted(OUT.glob('submission_moonshot_*prob.csv')):
        if 'optimized' not in p.name and 'validated_block' not in p.name and 'antifix' not in p.name and 'graph_raw' not in p.name:
            continue
        df=pd.read_csv(p); row={'file':p.name}
        for refname,ref in [('anchor',anchor),('raw_all_noq3',raw),('w03',w03)]:
            ds=[np.abs(df[y].to_numpy(float)-ref[y].to_numpy(float)).mean() for y in LABELS]
            row[f'mean_abs_vs_{refname}']=float(np.mean(ds)); row[f'max_target_mean_abs_vs_{refname}']=float(np.max(ds))
        rows.append(row)
    summ=pd.DataFrame(rows).sort_values('mean_abs_vs_anchor',ascending=False)
    summ.to_csv(EXP/'moonshot_improved_candidate_summary.csv',index=False)
    lines=['# Improved moonshot graph candidates','','These refine raw-all-noQ3 by removing graph from validation-negative targets Q1/S4 and/or sharpening validation-positive S2/S3.','','## Movement summary',summ.to_string(index=False,float_format=lambda x:f'{x:.6f}'),'','## Recommendation logic','- If pure 0.5-or-bust: raw_all_noq3 or optimized_keep_s4raw.','- If using masked validation literally: optimized_targetwise.','- If risk-adjusted: validated_block_sharp or validated_block.']
    (EXP/'moonshot_improved_candidate_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print(summ.to_string(index=False))

if __name__=='__main__': main()
