import pandas as pd
s=pd.read_csv('experiments/human_hypothesis_q2s2_eval_summary.csv')
s['group']=s['split'].apply(lambda x: 'tail' if str(x).startswith('tail') else x)
for t in ['Q2','S2']:
    print('\nTARGET',t)
    agg=s[s.target.eq(t)].groupby(['subset','k','C','group'],dropna=False).agg(delta=('delta_vs_existing','mean'),loss=('logloss','mean'),auc=('auc','mean')).reset_index()
    mean=agg.groupby(['subset','k','C'],dropna=False).agg(mean_delta=('delta','mean'), worst_delta=('delta','max')).reset_index().sort_values(['mean_delta','worst_delta']).head(12)
    print(mean.to_string(index=False))
    print('\nDeltas pivot')
    rows=[]
    for _,r in mean.head(8).iterrows():
        sub=agg[(agg['subset']==r['subset'])]
        sub=sub[sub['k'].fillna(-999)==(-999 if pd.isna(r['k']) else r['k'])]
        sub=sub[sub['C'].fillna(-999)==(-999 if pd.isna(r['C']) else r['C'])]
        d={'subset':r['subset'],'k':r['k'],'C':r['C']}
        for _,rr in sub.iterrows(): d[rr['group']]=rr['delta']
        rows.append(d)
    print(pd.DataFrame(rows).round(4).to_string(index=False))
print('\nSelected sample features')
p='experiments/human_hypothesis_q2s2_selected_features_sample.csv'
df=pd.read_csv(p)
for key,g in df.groupby(['target','subset']):
    print('\n',key)
    print('\n'.join(g.feature.drop_duplicates().head(25).tolist()))
