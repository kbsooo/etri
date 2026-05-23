#!/usr/bin/env python3
"""High-upside / non-anchor meta diagnostics.

The previous S2 sparse meta candidates were anchor-exploitation: small S2-only
moves around the public-supported 0.631-ish temporal-smoothing anchor.  This
script instead constructs larger, mechanism-level candidates that can plausibly
move the score more if the interleaved/state-completion hypothesis is right.

These files are intentionally higher risk and are not automatic submission
recommendations.  They are meant to separate "small anchor polish" from "real
breakout attempt" candidates.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; EXP=ROOT/'experiments'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']; IDS=['subject_id','sleep_date','lifelog_date']

def read(name): return pd.read_csv(OUT/name)

def assert_same(a,b):
    if not a[IDS].astype(str).equals(b[IDS].astype(str)):
        raise ValueError('ID mismatch')

def shift(df, ref, prefix):
    rows=[]
    for y in LABELS:
        d=np.abs(df[y].to_numpy(float)-ref[y].to_numpy(float))
        rows.append({
            'target':y,
            f'{prefix}_changed_rows':int((d>1e-12).sum()),
            f'{prefix}_mean_abs_delta':float(d.mean()),
            f'{prefix}_p95_abs_delta':float(np.quantile(d,.95)),
            f'{prefix}_max_abs_delta':float(d.max()),
            f'{prefix}_corr':float(np.corrcoef(df[y],ref[y])[0,1]) if d.max()>0 else 1.0,
            f'{prefix}_mean_prob_shift':float(df[y].mean()-ref[y].mean()),
        })
    return pd.DataFrame(rows)

def write(name, df, base, anchor, notes):
    path=OUT/name; df.to_csv(path,index=False)
    s_base=shift(df,base,'vs_base'); s_anchor=shift(df,anchor,'vs_anchor')
    s=s_base.merge(s_anchor,on='target')
    stem=name.replace('.csv','')
    s.to_csv(EXP/f'{stem}_shift.csv',index=False)
    (EXP/f'{stem}_notes.json').write_text(json.dumps({'file':str(path),**notes},ensure_ascii=False,indent=2),encoding='utf-8')
    return s

def main():
    OUT.mkdir(exist_ok=True); EXP.mkdir(exist_ok=True)
    base=read('submission_base_v4_replicate_prob.csv')
    anchor=read('submission_meta_anchor_w02_noq3_prob.csv')
    w03=read('submission_lbdiag_w03_noq3_q2w02_prob.csv')
    w02=read('submission_temporal_state_smoothing_wcap02_prob.csv')
    learned30=read('submission_learned_calibrator_q1q2s4_blend30_prob.csv')
    learned50=read('submission_learned_calibrator_q1q2s4_blend50_prob.csv')
    tiny_q1s2_30=read('submission_tiny_dl_golf_q1s2_blend30_prob.csv')
    s2_sparse30=read('submission_meta_anchor_s2sparse_blend30_prob.csv')
    s2_sparse50=read('submission_meta_anchor_s2sparse_blend50_prob.csv')
    s2_sparse_replace=read('submission_meta_anchor_s2sparse_replace_prob.csv')
    for x in [anchor,w03,w02,learned30,learned50,tiny_q1s2_30,s2_sparse30,s2_sparse50,s2_sparse_replace]: assert_same(base,x)

    reports=[]
    def add(name, df, desc, rationale, risk):
        s=write(name,df,base,anchor,{'description':desc,'rationale':rationale,'risk':risk,'submission_status':'high-upside diagnostic; not automatic recommendation'})
        # compact row-level summary across changed targets
        changed=s[(s.vs_anchor_changed_rows>0) | (s.vs_base_changed_rows>0)].copy()
        reports.append({
            'file':name,
            'description':desc,
            'changed_targets':','.join(changed.target.tolist()),
            'mean_abs_vs_anchor_avg_changed':float(changed.vs_anchor_mean_abs_delta.mean()) if len(changed) else 0.0,
            'max_vs_anchor_max_changed':float(changed.vs_anchor_max_abs_delta.max()) if len(changed) else 0.0,
            'mean_abs_vs_base_avg_changed':float(changed.vs_base_mean_abs_delta.mean()) if len(changed) else 0.0,
            'risk':risk,
        })

    # C1: actual high-upside state-completion candidate: stronger temporal smoothing on every non-Q3 target, but Q2 capped at w02.
    c1=w03.copy()
    add('submission_breakout_state_w03_noq3_q2w02_prob.csv', c1,
        'High-upside state-completion candidate: w03 temporal smoothing for Q1/S1/S2/S3/S4, Q2 capped at w02, Q3 base.',
        'If public split is interleaved same-subject state completion, broad temporal smoothing must move multiple targets, not only S2.',
        'large distribution shift; may over-smooth if public/private is tail-like')

    # C2: remove Q2 risk entirely, keep aggressive non-Q2 state completion.
    c2=w03.copy(); c2['Q2']=base['Q2']
    add('submission_breakout_state_w03_noq2_noq3_prob.csv', c2,
        'Aggressive state-completion excluding risky Q2/Q3: Q1/S1/S2/S3/S4 use w03; Q2/Q3 base.',
        'Q2 repeatedly shows tail risk; this tests whether the big gain can come from broad non-Q2 state targets.',
        'still large shift; loses upside if Q2 smoothing was necessary')

    # C3: Q/S split strategy: S-targets are aggressive state-completion, Q-targets conservative except Q1 tiny-DL.
    c3=base.copy()
    for y in ['S1','S2','S3','S4']: c3[y]=w03[y]
    c3['Q1']=tiny_q1s2_30['Q1']; c3['Q2']=base['Q2']; c3['Q3']=base['Q3']
    add('submission_breakout_s_targets_plus_q1dl_prob.csv', c3,
        'S-target breakout: S1/S2/S3/S4 w03 temporal, Q1 tiny-DL30, Q2/Q3 base.',
        'If S labels are routine/state and Q2 is the dangerous subjective tail label, concentrate risk on S-family.',
        'ignores Q2; S4/Q1 may still be overfit')

    # C4: combine independent S2 sparse signal with aggressive state candidate.
    c4=w03.copy()
    c4['S2']=np.clip(0.5*w03['S2']+0.5*s2_sparse_replace['S2'],.02,.98)
    add('submission_breakout_state_w03_s2_sparse50_prob.csv', c4,
        'State w03 candidate with S2 averaged 50/50 with sparse raw32 replacement.',
        'S2 had independent sparse-head evidence; this gives S2 a bigger non-anchor correction while preserving broad state smoothing.',
        'S2 shift is materially larger than anchor polish')

    # C5: hard-target mechanism attempt: Q1/S4 learned calibrator blended into the state candidate; Q2 kept w02 not learned.
    c5=w03.copy()
    for y in ['Q1','S4']:
        c5[y]=np.clip(0.5*w03[y]+0.5*learned30[y],.02,.98)
    c5['Q2']=w02['Q2']; c5['Q3']=base['Q3']
    add('submission_breakout_state_plus_q1s4_calib15_prob.csv', c5,
        'State w03 plus Q1/S4 learned-calibrator influence; Q2 capped at w02 and Q3 base.',
        'Q1/S4 calibrator had plausible local gains; Q2 learned calibration was tail-risky, so exclude it.',
        'hard-target calibrator may overfit despite excluding Q2')

    # C6: aggressive but focused: Q1/S2/S4 only, no broad S1/S3 smoothing.
    c6=anchor.copy()
    c6['Q1']=np.clip(0.5*anchor['Q1']+0.5*learned50['Q1'],.02,.98)
    c6['S4']=np.clip(0.5*anchor['S4']+0.5*learned50['S4'],.02,.98)
    c6['S2']=np.clip(0.5*anchor['S2']+0.5*s2_sparse_replace['S2'],.02,.98)
    add('submission_breakout_focused_q1s2s4_prob.csv', c6,
        'Focused hard-target breakout: anchor plus larger Q1/S4 calibrator and S2 sparse replacement interpolation.',
        'Targets the labels with strongest side-track evidence without changing all seven outputs.',
        'less broad upside; Q1/S4 still may not generalize')

    rep=pd.DataFrame(reports).sort_values('mean_abs_vs_anchor_avg_changed',ascending=False)
    rep.to_csv(EXP/'breakout_high_upside_candidate_summary.csv',index=False)
    lines=['# High-upside / non-anchor meta diagnostics','','These candidates are designed for bigger movement than anchor-polish S2-only files. They are higher risk and not automatic submission recommendations.','','## Candidate summary',rep.to_string(index=False,float_format=lambda x:f'{x:.6f}'),'','## Suggested interpretation','If the goal is a real jump rather than a small anchor improvement, only C1/C2/C3-style candidates have enough target coverage to plausibly move the total score. S2-only sparse blends are exploitation. The cleanest high-upside diagnostic is C2 if Q2 risk is feared, or C1 if we trust temporal smoothing broadly.']
    out=EXP/'breakout_high_upside_candidate_report.md'; out.write_text('\n'.join(lines),encoding='utf-8')
    print('wrote',out)
    print(rep.to_string(index=False))
if __name__=='__main__': main()
