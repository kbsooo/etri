import pandas as pd, numpy as np
base='/Users/kbsoo/Downloads/cl'
res=pd.read_csv(base+'/experiments/temporal_state_smoothing_masked_results.csv')
for cap in [0.1,0.2,0.3,0.4]:
    print('\n## w cap',cap)
    tp=res[(res.split=='testpattern')]
    tp=tp[tp.w<=cap]
    summ=tp.groupby(['target','tau','alpha','w'])[['logloss','base_logloss','smooth_only_logloss']].mean().reset_index()
    rows=[]
    for y,g in summ.groupby('target'):
        best=g.sort_values('logloss').iloc[0]
        base_loss=g[g.w.eq(0)]['logloss'].mean()
        tail=res[res.split=='tail']
        tail=tail[tail.target==y]
        tail=tail[tail.tau==best.tau]
        tail=tail[tail.alpha==best.alpha]
        tail=tail[tail.w==best.w]
        tail_loss=tail.logloss.mean() if len(tail) else np.nan
        tail_base=tail.base_logloss.mean() if len(tail) else np.nan
        rows.append([y,best.tau,best.alpha,best.w,best.logloss,base_loss,best.logloss-base_loss,tail_loss,tail_base,tail_loss-tail_base])
    print(pd.DataFrame(rows,columns='target tau alpha w tp_loss tp_base tp_delta tail_loss tail_base tail_delta'.split()).to_string(index=False))
print('\n## selected overall averages')
for cap in [0,0.1,0.2,0.3,0.4]:
    vals=[]
    for y in ['Q1','Q2','Q3','S1','S2','S3','S4']:
        tp=res[res.split=='testpattern']
        tp=tp[tp.target==y]
        tp=tp[tp.w<=cap]
        if cap==0:
            loss=tp[tp.w.eq(0)].groupby(['tau','alpha','w'])['logloss'].mean().iloc[0]
        else:
            loss=tp.groupby(['tau','alpha','w'])['logloss'].mean().reset_index().sort_values('logloss').iloc[0].logloss
        vals.append(float(loss))
    print(cap, float(np.mean(vals)), vals)
