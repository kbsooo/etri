import pandas as pd, numpy as np
base='/Users/kbsoo/Downloads/cl'
res=pd.read_csv(base+'/experiments/learned_temporal_calibrator_results.csv')
for split in ['testpattern','tail']:
    print('\n###',split)
    sub=res[res.split==split]
    summ=sub.groupby(['target','method','C'])[['logloss','base_logloss']].mean().reset_index()
    rows=[]
    for y,g in summ.groupby('target'):
        base_loss=g.base_logloss.mean()
        best=g.sort_values('logloss').iloc[0]
        rows.append([y,best.method,best.C,best.logloss,base_loss,best.logloss-base_loss])
    print(pd.DataFrame(rows,columns='target method C loss base delta'.split()).to_string(index=False))
# compare smoothing wcap02 vs learned (testpattern avg)
sm=pd.read_csv(base+'/experiments/temporal_state_smoothing_masked_results.csv')
print('\n### simple smoothing best w<=0.2 testpattern')
rows=[]
for y in ['Q1','Q2','Q3','S1','S2','S3','S4']:
    g=sm[(sm.split=='testpattern')&(sm.target==y)&(sm.w<=0.2)].groupby(['tau','alpha','w'])[['logloss','base_logloss']].mean().reset_index().sort_values('logloss')
    b=g[g.w==0].logloss.mean(); row=g.iloc[0]
    rows.append([y,row.tau,row.alpha,row.w,row.logloss,b,row.logloss-b])
print(pd.DataFrame(rows,columns='target tau alpha w loss base delta'.split()).to_string(index=False))
