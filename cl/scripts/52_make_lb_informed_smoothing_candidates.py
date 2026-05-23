#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; EXP=ROOT/'experiments'
labels=['Q1','Q2','Q3','S1','S2','S3','S4']
base=pd.read_csv(OUT/'submission_base_v4_replicate_prob.csv')
w01=pd.read_csv(OUT/'submission_temporal_state_smoothing_wcap01_prob.csv')
w02=pd.read_csv(OUT/'submission_temporal_state_smoothing_wcap02_prob.csv')
w03=pd.read_csv(OUT/'submission_temporal_state_smoothing_wcap03_prob.csv')
w04=pd.read_csv(OUT/'submission_temporal_state_smoothing_prob.csv')

def save(name, source_by_target):
    sub=base.copy()
    sources={}
    for y,src in source_by_target.items():
        sub[y]=src[y]
        sources[y]=('custom' if src is not base and src is not w01 and src is not w02 and src is not w03 and src is not w04 else 
                    'base' if src is base else 'w01' if src is w01 else 'w02' if src is w02 else 'w03' if src is w03 else 'w04')
    sub.to_csv(OUT/f'{name}.csv',index=False)
    shifts=[]
    for y in labels:
        d=(sub[y]-base[y]).abs()
        shifts.append({'target':y,'source':sources.get(y,'base'),'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(sub[y],base[y])[0,1]) if d.max()>0 else 1.0})
    pd.DataFrame(shifts).to_csv(EXP/f'{name}_shift.csv',index=False)
    return shifts

# 1) Target-isolation diagnostic: keep only subjective Q1/Q2 and S4 from w02.
save('submission_lbdiag_w02_q1q2s4_only_prob', {y:(w02 if y in ['Q1','Q2','S4'] else base) for y in labels})
# 2) Remove Q3 from w02 because Q3 smoothing has the largest correlation drop among w02 targets.
save('submission_lbdiag_w02_all_except_q3_prob', {y:(base if y=='Q3' else w02) for y in labels})
# 3) Slightly stronger but avoid Q3 and keep Q2 at w02 because w03 script disabled Q2 due tail gate.
save('submission_lbdiag_w03_noq3_q2w02_prob', {y:(base if y=='Q3' else w02 if y=='Q2' else w03) for y in labels})
# 4) Interpolate halfway between w02 and w03 for targets where w03 is defined; keep Q2 from w02, Q3 base.
mid=base.copy()
for y in labels:
    if y=='Q3': mid[y]=base[y]
    elif y=='Q2': mid[y]=w02[y]
    else: mid[y]=0.5*w02[y]+0.5*w03[y]
save('submission_lbdiag_mid_w025_noq3_q2w02_prob', {y:mid for y in labels})

print('created LB diagnostic candidates')
for name in ['submission_lbdiag_w02_q1q2s4_only_prob','submission_lbdiag_w02_all_except_q3_prob','submission_lbdiag_w03_noq3_q2w02_prob','submission_lbdiag_mid_w025_noq3_q2w02_prob']:
    print('\n###',name)
    print(pd.read_csv(EXP/f'{name}_shift.csv').to_string(index=False))
