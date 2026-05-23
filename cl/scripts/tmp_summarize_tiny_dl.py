import pandas as pd, numpy as np
base='/Users/kbsoo/Downloads/cl'
res=pd.read_csv(base+'/experiments/tiny_dl_golf_results.csv')
for group_name,mask in [('chrono',res.split.str.startswith('chrono')),('testpattern',res.split.str.startswith('testpattern')),('tail',res.split.eq('tail')),('all',res.split.notna())]:
    sub=res[mask]
    print('\n###',group_name)
    summ=sub.groupby(['target','model'])[['logloss','base_logloss','params']].mean().reset_index()
    rows=[]
    for y,g in summ.groupby('target'):
        b=g[g.model.eq('sk_logistic_sameK')].logloss.mean()
        for _,r in g.sort_values('logloss').head(4).iterrows():
            rows.append([y,r.model,r.logloss,b,r.logloss-b,r.params])
    print(pd.DataFrame(rows,columns='target model loss logistic delta params'.split()).to_string(index=False))
print('\n### selection json')
print(open(base+'/experiments/tiny_dl_golf_selected.json').read())
