#!/usr/bin/env python3
"""Further no-submit experiments:

1) Q2: separate tail-safe fatigue features from interleaved-only features.
2) S2: compress hourly behavior into interpretable routine-state axes.

No submission files are written.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util, warnings, json
import numpy as np
import pandas as pd
import duckdb
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; FEAT=ROOT/'features'; EXP=ROOT/'experiments'
spec=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
LABELS=ts.LABELS; ID=['subject_id','lifelog_date']; ID_COLS=ts.ID_COLS


def pq(p):
    return duckdb.connect().execute(f"select * from read_parquet('{p}')").df()


def load_df():
    base=ts.load_all(); base['lifelog_date']=pd.to_datetime(base['lifelog_date'])
    human=pq(FEAT/'human_hypothesis_q2s2_features_v1.parquet'); human['lifelog_date']=pd.to_datetime(human['lifelog_date'])
    flat=pq(FEAT/'timebin_1h_flat_features.parquet'); flat['lifelog_date']=pd.to_datetime(flat['lifelog_date'])
    df=base.merge(human,on=ID,how='left').merge(flat,on=ID,how='left',suffixes=('','__flat'))
    return df.sort_values(['subject_id','lifelog_date']).reset_index(drop=True)


def valid_cols(df, mask, cols):
    out=[]
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df.loc[mask,c],errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
    return out


def make_masks(train, sample):
    masks=[]
    for seed in range(10): masks.append(('testpattern',seed,ts.make_testpattern_mask(train,sample,seed)))
    for seed in range(10):
        rng=np.random.default_rng(seed+610); mask=np.zeros(len(train),bool)
        for _,g in train.groupby('subject_id'):
            idx=g.sort_values('sleep_date').index.to_numpy(); n=max(3,int(round(len(idx)*0.28)))
            ranks=np.linspace(0,1,len(idx)); prob=0.15+0.7*ranks+np.exp(-0.5*((ranks-.55)/.22)**2); prob=prob/prob.sum()
            chosen=rng.choice(idx,size=min(n,len(idx)-2),replace=False,p=prob)
            mask[train.index.get_indexer(chosen)]=True
        masks.append(('random_gap',seed,mask))
    for frac in [0.20,0.30,0.40,0.50]:
        mask=np.zeros(len(train),bool)
        for _,g in train.groupby('subject_id'):
            idx=g.sort_values('sleep_date').tail(max(3,int(round(len(g)*frac)))).index
            mask[train.index.get_indexer(idx)]=True
        masks.append((f'tail{frac:.2f}',int(frac*100),mask))
    return masks


def pipe(kind,k,C,ncols):
    if kind=='ridge':
        return Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler()),('clf',RidgeClassifier(alpha=1/max(C,1e-6)))])
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])


def predict_proba_like(model, X):
    clf=model.named_steps['clf']
    if hasattr(clf,'predict_proba'):
        return model.predict_proba(X)[:,1]
    # RidgeClassifier decision_function -> sigmoid with conservative scale
    z=model.decision_function(X)
    z=(z-np.nanmean(z))/(np.nanstd(z)+1e-9)
    return 1/(1+np.exp(-z))


def build_s2_axes(df):
    # Interpretable axes from 24h flat table. Keep simple and low-dimensional.
    rows=[]
    for r in df.to_dict('records'):
        row={'subject_id':r['subject_id'],'lifelog_date':r['lifelog_date']}
        def s(metric, hrs):
            vals=[r.get(f'h{h:02d}_{metric}_h',np.nan) for h in hrs]
            vals=[0 if pd.isna(v) else float(v) for v in vals]
            return sum(vals)
        def m(metric, hrs):
            vals=[r.get(f'h{h:02d}_{metric}_h',np.nan) for h in hrs]
            vals=[float(v) for v in vals if not pd.isna(v)]
            return float(np.mean(vals)) if vals else np.nan
        day=range(6,18); eve=range(18,24); late=list(range(21,24))+list(range(0,3)); night=range(0,6); morning=range(6,10)
        row['axis_late_phone']=np.log1p(s('screen_use_sum',late))
        row['axis_night_movement']=np.log1p(s('steps_sum',night)+s('activity_mean',night))
        row['axis_day_load']=np.log1p(s('steps_sum',day)+s('distance_sum',day))
        row['axis_evening_arousal']=np.log1p(s('screen_use_sum',eve)+1)*np.log1p(max(m('mlight_mean',eve),0)+max(m('wlight_mean',eve),0)+1)
        row['axis_quiet_recovery']=-(np.log1p(s('screen_use_sum',night)+s('steps_sum',night)+1))
        row['axis_morning_activation']=np.log1p(s('steps_sum',morning)+s('screen_use_sum',morning)+1)
        row['axis_day_night_reversal']=row['axis_late_phone']+row['axis_night_movement']-0.3*row['axis_day_load']
        rows.append(row)
    ax=pd.DataFrame(rows).sort_values(['subject_id','lifelog_date']).reset_index(drop=True)
    base_cols=[c for c in ax.columns if c.startswith('axis_')]
    out=[]
    for sid,g in ax.groupby('subject_id',sort=False):
        g=g.sort_values('lifelog_date').copy()
        for c in base_cols:
            s0=pd.to_numeric(g[c],errors='coerce')
            med=s0.shift(1).expanding(min_periods=5).median()
            mu=s0.shift(1).expanding(min_periods=5).mean()
            sd=s0.shift(1).expanding(min_periods=5).std().replace(0,np.nan)
            g[f'{c}_person_z']=(s0-mu)/sd
            for w in [3,7,14,30]:
                g[f'{c}_prev{w}_mean']=s0.shift(1).rolling(w,min_periods=2).mean()
                if w in [7,30]: g[f'{c}_vs_prev{w}']=s0-s0.shift(1).rolling(w,min_periods=2).mean()
            g[f'{c}_above_median_prev7']=(s0>med).astype(float).shift(1).rolling(7,min_periods=1).sum()
        g['axis_routine_instability']=g[[f'{c}_person_z' for c in base_cols]].abs().mean(axis=1)
        g['axis_chronic_late_irregular']=g['axis_late_phone_prev30_mean']+g['axis_night_movement_prev30_mean']+g['axis_routine_instability']
        g['axis_recovery_deficit_week']=-(g['axis_quiet_recovery_prev7_mean'])+g['axis_evening_arousal_prev7_mean']
        out.append(g)
    ax=pd.concat(out,ignore_index=True)
    path=FEAT/'s2_routine_axes_v1.parquet'; ax.to_parquet(path,index=False)
    print('wrote',path,ax.shape)
    return ax


def run_eval():
    df=load_df()
    axes=build_s2_axes(df[['subject_id','lifelog_date']+[c for c in df.columns if c.startswith('h')]].copy())
    df=df.merge(axes,on=ID,how='left')
    train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    all_cols=[c for c in train.columns if c not in set(ID_COLS+LABELS+['is_train'])]
    human=[c for c in all_cols if c.startswith('human_')]
    q2_tail_safe=[c for c in human if any(tok in c for tok in ['prev14','prev30','subj_z_all_prev14','subj_z_all_prev30','physical_load','light_screen_arousal','tired_but_wired']) and not any(tok in c for tok in ['vs_prev','day_change','sudden'])]
    q2_interleaved=[c for c in human if any(tok in c for tok in ['vs_prev','prev3','day_change','sudden','late_after_busy','evening_no_recovery'])]
    q2_compact=[c for c in human if c.startswith('human_hyp_q2_') or c in ['human_q2_physical_load','human_q2_evening_no_recovery','human_q2_tired_but_wired','human_q2_light_screen_arousal']]
    s2_axes=[c for c in all_cols if c.startswith('axis_')]
    s2_existing=ts.base_subset(all_cols,'no_flat_hourly')
    subsets={
        'q2_tail_safe_longterm':q2_tail_safe,
        'q2_interleaved_shortterm':q2_interleaved,
        'q2_compact_hypotheses':q2_compact,
        'q2_existing_day_flat':ts.base_subset(all_cols,'day_flat'),
        'q2_day_flat_plus_tail_safe':list(dict.fromkeys(ts.base_subset(all_cols,'day_flat')+q2_tail_safe)),
        's2_axes_only':s2_axes,
        's2_existing_no_flat_hourly':s2_existing,
        's2_existing_plus_axes':list(dict.fromkeys(s2_existing+s2_axes)),
    }
    masks=make_masks(train,sample)
    rows=[]; selected=[]
    for split,seed,val_mask in masks:
        tr=~val_mask; va=val_mask
        for target in ['Q2','S2']:
            pbase=ts.base_predict_for(train,tr,va,target,None)
            y=train.loc[va,target].astype(int).to_numpy()
            rows.append({'split':split,'seed':seed,'target':target,'subset':'existing_base_cfg','model':'basecfg','k':np.nan,'C':np.nan,'logloss':log_loss(y,pbase,labels=[0,1]),'auc':roc_auc_score(y,pbase) if len(set(y))==2 else np.nan,'ncols':np.nan})
            for subset,cols0 in subsets.items():
                if target=='Q2' and not subset.startswith('q2_'): continue
                if target=='S2' and not subset.startswith('s2_'): continue
                cols=valid_cols(train,tr,cols0)
                if not cols: continue
                for kind in ['logreg']:
                    for k in [5,8,15,30,60]:
                        for C in [0.003,0.01,0.03,0.1]:
                            if k>len(cols)*2: continue
                            model=pipe(kind,k,C,len(cols)); model.fit(train.loc[tr,cols],train.loc[tr,target].astype(int))
                            p=np.clip(predict_proba_like(model,train.loc[va,cols]),0.02,0.98)
                            rows.append({'split':split,'seed':seed,'target':target,'subset':subset,'model':kind,'k':k,'C':C,'logloss':log_loss(y,p,labels=[0,1]),'auc':roc_auc_score(y,p) if len(set(y))==2 else np.nan,'ncols':len(cols)})
                            if split=='testpattern' and seed==0 and k in [8,15] and C in [0.01,0.03]:
                                try:
                                    names=np.array(cols)[model.named_steps['sel'].get_support()]
                                    for nm in names: selected.append({'target':target,'subset':subset,'k':k,'C':C,'feature':nm})
                                except Exception: pass
    res=pd.DataFrame(rows); res.to_csv(EXP/'q2_tail_safe_s2_axes_eval_results.csv',index=False)
    if selected: pd.DataFrame(selected).drop_duplicates().to_csv(EXP/'q2_tail_safe_s2_axes_selected_features.csv',index=False)
    summ=res.groupby(['target','split','subset','model','k','C'],dropna=False).agg(logloss=('logloss','mean'),auc=('auc','mean'),ncols=('ncols','mean')).reset_index()
    base=summ[summ.subset.eq('existing_base_cfg')][['target','split','logloss']].rename(columns={'logloss':'base_loss'})
    summ=summ.merge(base,on=['target','split'],how='left'); summ['delta_vs_existing']=summ.logloss-summ.base_loss
    summ.to_csv(EXP/'q2_tail_safe_s2_axes_eval_summary.csv',index=False)
    report(summ)


def report(summ):
    summ['group']=summ['split'].map(lambda x:'tail' if str(x).startswith('tail') else x)
    lines=['# Q2 tail-safe / S2 routine-axes further experiments','', 'No submission files were created.', '']
    for target in ['Q2','S2']:
        lines.append(f'## {target}')
        for group in ['testpattern','random_gap','tail']:
            sub=summ[(summ.target.eq(target)) & (summ.group.eq(group))]
            agg=sub.groupby(['subset','model','k','C'],dropna=False).agg(logloss=('logloss','mean'),delta=('delta_vs_existing','mean'),auc=('auc','mean')).reset_index().sort_values('logloss').head(8)
            lines.append(f'### {group}')
            lines.append(agg.to_string(index=False,float_format=lambda x:f'{x:.4f}'))
            lines.append('')
        # robust view
        sub=summ[summ.target.eq(target)]
        agg=sub.groupby(['subset','model','k','C','group'],dropna=False).agg(delta=('delta_vs_existing','mean')).reset_index()
        mean=agg.groupby(['subset','model','k','C'],dropna=False).agg(mean_delta=('delta','mean'),worst_delta=('delta','max')).reset_index().sort_values(['mean_delta','worst_delta']).head(12)
        lines.append('### robust coarse ranking across split groups')
        lines.append(mean.to_string(index=False,float_format=lambda x:f'{x:.4f}'))
        lines.append('')
    out=EXP/'q2_tail_safe_s2_axes_report.md'; out.write_text('\n'.join(lines),encoding='utf-8')
    print('wrote',out)
    print('\n'.join(lines[:120]))

if __name__=='__main__':
    EXP.mkdir(exist_ok=True); run_eval()
