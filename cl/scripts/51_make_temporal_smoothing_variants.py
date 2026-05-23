#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
res=pd.read_csv(ROOT/'experiments/temporal_state_smoothing_masked_results.csv')
df=ts.load_all()
train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
full=pd.concat([train,sample],ignore_index=True)
known_mask=np.r_[np.ones(len(train),dtype=bool), np.zeros(len(sample),dtype=bool)]
query_mask=np.r_[np.zeros(len(train),dtype=bool), np.ones(len(sample),dtype=bool)]
base_pred={y: ts.base_predict_for(full,known_mask,query_mask,y,None) for y in ts.LABELS}
for cap in [0.1,0.2,0.3]:
    sub=sample[ts.ID_COLS].copy().reset_index(drop=True)
    used={}; shifts=[]
    for y in ts.LABELS:
        tp=res[res.split.eq('testpattern')]
        tp=tp[tp.target.eq(y)]
        tp=tp[tp.w<=cap]
        summ=tp.groupby(['tau','alpha','w'])[['logloss','base_logloss']].mean().reset_index().sort_values('logloss')
        best=summ.iloc[0]
        base=summ[summ.w.eq(0)].logloss.mean()
        tail=res[res.split.eq('tail')]
        tail=tail[tail.target.eq(y)]
        tail=tail[tail.tau.eq(best.tau)]
        tail=tail[tail.alpha.eq(best.alpha)]
        tail=tail[tail.w.eq(best.w)]
        tail_delta=float(tail.logloss.mean()-tail.base_logloss.mean()) if len(tail) else 0.0
        # Conservative rule: apply if test-pattern win; for Q2 allow tiny tail harm only at cap<=0.2.
        apply=(best.logloss-base < -0.003) and (tail_delta <= (0.0015 if y=='Q2' and cap<=0.2 else 0.0)) and best.w>0
        p=base_pred[y]
        if apply:
            ps=ts.temporal_label_smooth(train,sample,y,float(best.tau),float(best.alpha),use_future=True)
            p=np.clip((1-float(best.w))*base_pred[y]+float(best.w)*ps,0.02,0.98)
        sub[y]=p
        d=np.abs(p-base_pred[y])
        shifts.append({'target':y,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(p,base_pred[y])[0,1]) if d.max()>0 else 1.0})
        used[y]={'apply_smoothing':bool(apply),'tau':float(best.tau),'alpha':float(best.alpha),'w':float(best.w),'tp_delta':float(best.logloss-base),'tail_delta':tail_delta}
    name=f'submission_temporal_state_smoothing_wcap{str(cap).replace(".","")}_prob'
    sub.to_csv(ROOT/'outputs'/f'{name}.csv',index=False)
    (ROOT/'experiments'/f'{name}_used.json').write_text(json.dumps(used,indent=2),encoding='utf-8')
    pd.DataFrame(shifts).to_csv(ROOT/'experiments'/f'{name}_shift.csv',index=False)
    print('\n###',name)
    print(json.dumps(used,indent=2))
    print(pd.DataFrame(shifts).to_string(index=False))
