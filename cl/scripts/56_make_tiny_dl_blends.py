#!/usr/bin/env python3
from pathlib import Path
import pandas as pd, numpy as np, json
ROOT=Path('/Users/kbsoo/Downloads/cl'); OUT=ROOT/'outputs'; EXP=ROOT/'experiments'
labels=['Q1','Q2','Q3','S1','S2','S3','S4']
base=pd.read_csv(OUT/'submission_base_v4_replicate_prob.csv')
pure=pd.read_csv(OUT/'submission_tiny_dl_golf_selected_prob.csv')

def make(name, weights):
    sub=base.copy()
    for y,w in weights.items():
        sub[y]=np.clip((1-w)*base[y]+w*pure[y],0.02,0.98)
    sub.to_csv(OUT/f'{name}.csv',index=False)
    rows=[]
    for y in labels:
        d=(sub[y]-base[y]).abs()
        rows.append({'target':y,'blend_w':weights.get(y,0.0),'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(sub[y],base[y])[0,1]) if d.max()>0 else 1.0})
    pd.DataFrame(rows).to_csv(EXP/f'{name}_shift.csv',index=False)
    print('\n###',name); print(pd.DataFrame(rows).to_string(index=False))

make('submission_tiny_dl_golf_s2_blend30_prob', {'S2':0.30})
make('submission_tiny_dl_golf_q1s2_blend20_prob', {'Q1':0.20,'S2':0.20})
make('submission_tiny_dl_golf_q1s2_blend30_prob', {'Q1':0.30,'S2':0.30})
