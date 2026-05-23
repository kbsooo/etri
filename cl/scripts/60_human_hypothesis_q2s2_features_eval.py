#!/usr/bin/env python3
"""Human-behavior hypothesis features for Q2/S2 + no-submit evaluation.

Focus:
- Q2: physical/mental fatigue before sleep = accumulated daytime load + failure to
  recover in evening/night + social/audio overstimulation.
- S2: broader sleep/routine state = multi-day regularity, sleep debt, rhythm drift,
  stable-vs-disrupted lifestyle.

This script creates features from existing sensor-derived feature tables only and
evaluates them under masked validation. It does NOT write submission files.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util, json, warnings
import numpy as np
import pandas as pd
import duckdb
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; FEAT=ROOT/'features'; EXP=ROOT/'experiments'
spec=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
LABELS=ts.LABELS; ID=['subject_id','lifelog_date']


def read_parquet(path: Path) -> pd.DataFrame:
    con=duckdb.connect()
    return con.execute(f"select * from read_parquet('{path}')").df()


def zscore_by_subject(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out=df.copy()
    for c in cols:
        g=out.groupby('subject_id')[c]
        mu=g.transform('mean')
        sd=g.transform('std').replace(0,np.nan)
        out[f'{c}_subj_z_all']=((out[c]-mu)/sd).replace([np.inf,-np.inf],np.nan)
    return out


def safe_sum(row, cols):
    vals=[row.get(c, np.nan) for c in cols]
    vals=[0 if pd.isna(v) else float(v) for v in vals]
    return sum(vals)


def build_features() -> pd.DataFrame:
    keys_train=pd.read_csv(DATA/'ch2026_metrics_train.csv', parse_dates=['lifelog_date'])[['subject_id','lifelog_date']]
    keys_test=pd.read_csv(DATA/'ch2026_submission_sample.csv', parse_dates=['lifelog_date'])[['subject_id','lifelog_date']]
    keys=pd.concat([keys_train,keys_test],ignore_index=True).drop_duplicates()
    keys['lifelog_date']=pd.to_datetime(keys['lifelog_date'])

    flat=read_parquet(FEAT/'timebin_1h_flat_features.parquet')
    flat['lifelog_date']=pd.to_datetime(flat['lifelog_date'])
    pub=read_parquet(FEAT/'public_failure_followup_features_v1.parquet')
    pub['lifelog_date']=pd.to_datetime(pub['lifelog_date'])
    # Existing broad daily table has useful raw daily aggregates.
    model=read_parquet(FEAT/'model_features_v0.parquet')
    model['lifelog_date']=pd.to_datetime(model['lifelog_date'])
    raw_cols=[c for c in model.columns if c in [
        'screen_use_sum','screen_use_21_03','screen_use_00_06','screen_use_18_24',
        'steps_sum','distance_sum','calories_sum','steps_21_03','steps_00_06','steps_18_24',
        'mlight_mean','mlight_max','wlight_mean','wlight_max','activity_mean','activity_n',
        'charging_mean','charging_00_06','last_screen_hour_any','first_screen_hour_any',
        'sleep_screen_sum','sleep_steps_sum','sleep_light_mean','sleep_light_max','quiet_hours','sleep_active_hours',
        'state_entropy','transition_count','night_entropy','night_transition_count'
    ]]
    df=keys.merge(flat,on=ID,how='left').merge(pub,on=ID,how='left').merge(model[ID+raw_cols],on=ID,how='left')
    df=df.sort_values(['subject_id','lifelog_date']).reset_index(drop=True)

    rows=[]
    for r in df.to_dict('records'):
        row={'subject_id':r['subject_id'], 'lifelog_date':r['lifelog_date']}
        # Human hypothesis daily constructs from hourly table.
        day_hours=range(6,18); eve_hours=range(18,24); late_hours=list(range(21,24))+list(range(0,3)); night_hours=range(0,6)
        def hour_cols(metric, hours): return [f'h{h:02d}_{metric}_h' for h in hours]
        for prefix,hours in [('day',day_hours),('eve',eve_hours),('late',late_hours),('night',night_hours)]:
            row[f'human_{prefix}_steps']=safe_sum(r,hour_cols('steps_sum',hours))
            row[f'human_{prefix}_screen']=safe_sum(r,hour_cols('screen_use_sum',hours))
            row[f'human_{prefix}_dist']=safe_sum(r,hour_cols('distance_sum',hours))
            row[f'human_{prefix}_activity']=safe_sum(r,hour_cols('activity_mean',hours))
            row[f'human_{prefix}_light']=np.nanmean([r.get(c,np.nan) for c in hour_cols('mlight_mean',hours)+hour_cols('wlight_mean',hours)])
        # Existing q2lr rich features as high-level signals.
        for c in ['q2lr_load_score','q2lr_recovery_failure','q2lr_late_screen_after_load',
                  'q2lr_late_hr_minus_day','q2lr_evening_hr_minus_day','q2lr_activity_drop_18_to_evening']:
            row[f'human_{c}']=r.get(c,np.nan)
        # People-level hypotheses.
        row['human_q2_physical_load']=np.log1p(row['human_day_steps']) + 0.5*np.log1p(row['human_day_dist']) + 0.2*np.log1p(max(r.get('calories_sum',0) or 0,0))
        row['human_q2_evening_no_recovery']=np.log1p(row['human_eve_screen']+row['human_late_screen']) + 0.001*row['human_late_steps'] + 0.2*np.nan_to_num(row.get('human_q2lr_late_hr_minus_day',0))
        row['human_q2_tired_but_wired']=row['human_q2_physical_load']*np.log1p(row['human_late_screen']+1) + 0.5*np.nan_to_num(row.get('human_q2lr_recovery_failure',0))
        row['human_q2_late_after_busy_day']=np.log1p(row['human_day_steps']+row['human_day_screen'])*np.log1p(row['human_late_screen']+row['human_late_activity']+1)
        row['human_q2_light_screen_arousal']=np.log1p(row['human_late_screen']+1)*np.log1p(max(row['human_late_light'],0)+1)
        # Sleep/routine daily proxies for S2.
        row['human_s2_sleep_debt_day']=np.log1p(row['human_night_screen']+row['human_night_steps']+1) - 0.2*(r.get('quiet_hours',0) if pd.notna(r.get('quiet_hours',np.nan)) else 0)
        row['human_s2_rhythm_late']=np.log1p(row['human_late_screen']+1)+0.5*np.log1p(row['human_late_steps']+1)+0.1*(r.get('last_screen_hour_any',0) if pd.notna(r.get('last_screen_hour_any',np.nan)) else 0)
        row['human_s2_quiet_efficiency_proxy']=(r.get('quiet_hours',np.nan) if pd.notna(r.get('quiet_hours',np.nan)) else np.nan) - 0.1*np.log1p(row['human_night_screen']+1)
        row['human_s2_fragmentation_proxy']=np.nan_to_num(r.get('night_transition_count',0))+np.nan_to_num(r.get('transition_count',0))*0.2+np.log1p(row['human_night_screen']+row['human_night_steps']+1)
        rows.append(row)
    feat=pd.DataFrame(rows).sort_values(['subject_id','lifelog_date']).reset_index(drop=True)

    base_num=[c for c in feat.columns if c.startswith('human_')]
    feat=zscore_by_subject(feat,base_num)

    # Rolling/history features: previous days only, per subject. This is the main human part.
    roll_base=[c for c in feat.columns if c.startswith('human_q2_') or c.startswith('human_s2_') or c in [
        'human_day_steps','human_day_screen','human_eve_screen','human_late_screen','human_night_screen','human_night_steps','human_late_steps'
    ]]
    out=[]
    for sid,g in feat.groupby('subject_id', sort=False):
        g=g.sort_values('lifelog_date').copy()
        for c in roll_base:
            s=pd.to_numeric(g[c],errors='coerce')
            for w in [3,7,14,30]:
                prev=s.shift(1).rolling(w,min_periods=2)
                g[f'{c}_prev{w}_mean']=prev.mean()
                if w in [7,30]:
                    g[f'{c}_prev{w}_std']=prev.std()
                    g[f'{c}_vs_prev{w}']=s-prev.mean()
            # streak-like: last 3 days above subject median from previous history
            exp_med=s.shift(1).expanding(min_periods=5).median()
            above=(s>exp_med).astype(float)
            g[f'{c}_above_personal_median_prev3']=above.shift(1).rolling(3,min_periods=1).sum()
        # Routine break: day-to-day absolute changes.
        for c in ['human_q2_physical_load','human_q2_evening_no_recovery','human_s2_rhythm_late','human_s2_fragmentation_proxy']:
            s=pd.to_numeric(g[c],errors='coerce')
            g[f'{c}_day_change_abs']=s.diff().abs()
            g[f'{c}_prev3_change_abs_mean']=s.diff().abs().shift(1).rolling(3,min_periods=1).mean()
        out.append(g)
    feat=pd.concat(out,ignore_index=True)

    # Compact composite features that encode actual hypotheses.
    def nz(c): return pd.to_numeric(feat[c], errors='coerce').fillna(0)
    feat['human_hyp_q2_accumulated_load_no_recovery']=nz('human_q2_physical_load_prev7_mean')+nz('human_q2_evening_no_recovery_prev3_mean')+nz('human_q2_tired_but_wired')
    feat['human_hyp_q2_overdrawn_week']=nz('human_q2_physical_load_prev14_mean')+nz('human_q2_late_after_busy_day_prev7_mean')-nz('human_s2_quiet_efficiency_proxy_prev7_mean')
    feat['human_hyp_q2_sudden_load_spike']=nz('human_q2_physical_load_vs_prev7')+nz('human_q2_evening_no_recovery_vs_prev7')
    feat['human_hyp_s2_chronic_irregular_sleep']=nz('human_s2_rhythm_late_prev30_mean')+nz('human_s2_fragmentation_proxy_prev14_mean')-nz('human_s2_quiet_efficiency_proxy_prev14_mean')
    feat['human_hyp_s2_recent_rhythm_break']=nz('human_s2_rhythm_late_vs_prev30')+nz('human_s2_fragmentation_proxy_vs_prev30')+nz('human_s2_rhythm_late_prev3_change_abs_mean')
    feat['human_hyp_s2_broad_bad_state']=nz('human_s2_sleep_debt_day_prev30_mean')+nz('human_s2_fragmentation_proxy_prev30_mean')+nz('human_s2_rhythm_late_prev30_mean')

    path=FEAT/'human_hypothesis_q2s2_features_v1.parquet'
    feat.to_parquet(path,index=False)
    print('wrote',path,feat.shape)
    return feat


def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])


def eval_features(feat: pd.DataFrame):
    base=ts.load_all()
    base['lifelog_date']=pd.to_datetime(base['lifelog_date'])
    df=base.merge(feat,on=ID,how='left')
    train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    human_cols=[c for c in train.columns if c.startswith('human_')]
    q2_cols=[c for c in human_cols if 'q2' in c or 'day_' in c or 'late_' in c or 'eve_' in c or 'accumulated' in c or 'overdrawn' in c or 'load' in c]
    s2_cols=[c for c in human_cols if 's2' in c or 'rhythm' in c or 'fragment' in c or 'quiet' in c or 'broad' in c or 'night_' in c]
    subsets={
        'human_all':human_cols,
        'human_q2':q2_cols,
        'human_s2':s2_cols,
    }
    # Add existing base feature subsets for comparison/augmentation.
    all_cols=[c for c in train.columns if c not in set(ts.ID_COLS+LABELS+['is_train'])]
    subsets['q2_existing_day_flat']=ts.base_subset(all_cols,'day_flat')
    subsets['s2_existing_no_flat_hourly']=ts.base_subset(all_cols,'no_flat_hourly')
    subsets['q2_existing_plus_human']=list(dict.fromkeys(subsets['q2_existing_day_flat']+q2_cols))
    subsets['s2_existing_plus_human']=list(dict.fromkeys(subsets['s2_existing_no_flat_hourly']+s2_cols))

    masks=[]
    for seed in range(8): masks.append(('testpattern',seed,ts.make_testpattern_mask(train,sample,seed)))
    # random-ish gap by reusing previous script if present not needed: perturb testpattern enough? create simple middle-late random
    rng=np.random.default_rng(100)
    for seed in range(8):
        rng=np.random.default_rng(seed+200); mask=np.zeros(len(train),bool)
        for sid,g in train.groupby('subject_id'):
            idx=g.sort_values('sleep_date').index.to_numpy(); n=max(3,int(round(len(idx)*0.28)))
            ranks=np.linspace(0,1,len(idx)); p=0.2+0.6*ranks+np.exp(-0.5*((ranks-0.55)/0.25)**2); p=p/p.sum()
            chosen=rng.choice(idx,size=min(n,len(idx)-2),replace=False,p=p)
            mask[train.index.get_indexer(chosen)]=True
        masks.append(('random_gap',seed,mask))
    for frac in [0.25,0.36,0.45]:
        mask=np.zeros(len(train),bool)
        for sid,g in train.groupby('subject_id'):
            idx=g.sort_values('sleep_date').tail(max(3,int(round(len(g)*frac)))).index
            mask[train.index.get_indexer(idx)]=True
        masks.append((f'tail{frac}',int(frac*100),mask))

    rows=[]; feat_rows=[]
    for split,seed,val_mask in masks:
        tr=~val_mask; va=val_mask
        for target in ['Q2','S2']:
            # compare against existing ts base config predictor
            pbase=ts.base_predict_for(train,tr,va,target,None)
            ytrue=train.loc[va,target].astype(int).to_numpy()
            rows.append({'split':split,'seed':seed,'target':target,'subset':'existing_base_cfg','k':np.nan,'C':np.nan,'logloss':log_loss(ytrue,pbase,labels=[0,1]),'auc':roc_auc_score(ytrue,pbase) if len(set(ytrue))==2 else np.nan,'ncols':np.nan})
            for subset,cols0 in subsets.items():
                if target=='Q2' and subset.startswith('s2_'): continue
                if target=='S2' and subset.startswith('q2_'): continue
                cols=[]
                for c in cols0:
                    if c in train.columns:
                        s=pd.to_numeric(train.loc[tr,c],errors='coerce')
                        if s.notna().sum()>20 and s.nunique(dropna=True)>1: cols.append(c)
                if not cols: continue
                for k in [8,15,30,60,120]:
                    for C in [0.003,0.01,0.03,0.1]:
                        pipe=make_pipe(k,C,len(cols))
                        pipe.fit(train.loc[tr,cols], train.loc[tr,target].astype(int).to_numpy())
                        p=np.clip(pipe.predict_proba(train.loc[va,cols])[:,1],0.02,0.98)
                        rows.append({'split':split,'seed':seed,'target':target,'subset':subset,'k':k,'C':C,'logloss':log_loss(ytrue,p,labels=[0,1]),'auc':roc_auc_score(ytrue,p) if len(set(ytrue))==2 else np.nan,'ncols':len(cols)})
                        if split=='testpattern' and seed==0 and subset.startswith('human') and k in [15,30] and C in [0.01,0.03]:
                            try:
                                names=np.array(cols)[pipe.named_steps['sel'].get_support()]
                                for nm in names[:30]: feat_rows.append({'target':target,'subset':subset,'k':k,'C':C,'feature':nm})
                            except Exception: pass
    res=pd.DataFrame(rows)
    res.to_csv(EXP/'human_hypothesis_q2s2_eval_results.csv',index=False)
    if feat_rows: pd.DataFrame(feat_rows).drop_duplicates().to_csv(EXP/'human_hypothesis_q2s2_selected_features_sample.csv',index=False)

    # Summary: coarse groups, ignore 3rd-decimal, report only structural wins.
    summ=res.groupby(['target','split','subset','k','C'],dropna=False).agg(logloss=('logloss','mean'), auc=('auc','mean'), ncols=('ncols','mean')).reset_index()
    base=summ[summ.subset.eq('existing_base_cfg')][['target','split','logloss']].rename(columns={'logloss':'base_loss'})
    summ=summ.merge(base,on=['target','split'],how='left')
    summ['delta_vs_existing']=summ.logloss-summ.base_loss
    summ.to_csv(EXP/'human_hypothesis_q2s2_eval_summary.csv',index=False)
    print('\n### Best by target/split')
    for target in ['Q2','S2']:
        for group,pred in [('testpattern',lambda x:x=='testpattern'),('random_gap',lambda x:x=='random_gap'),('tail',lambda x:str(x).startswith('tail'))]:
            sub=summ[(summ.target.eq(target)) & (summ.split.map(pred))]
            agg=sub.groupby(['subset','k','C'],dropna=False).agg(logloss=('logloss','mean'), delta=('delta_vs_existing','mean'), auc=('auc','mean')).reset_index().sort_values('logloss').head(8)
            print('\n',target,group)
            print(agg.to_string(index=False))
    # Human-readable report.
    lines=['# Human-hypothesis Q2/S2 features, no submission','', 'Generated feature table: `features/human_hypothesis_q2s2_features_v1.parquet`','', 'Evaluation files:', '- `experiments/human_hypothesis_q2s2_eval_results.csv`','- `experiments/human_hypothesis_q2s2_eval_summary.csv`','']
    lines.append('## Coarse takeaway')
    lines.append('This experiment tests human-behavior hypotheses, not a submission. Treat only split-consistent, mechanism-consistent effects as real; ignore tiny third-decimal differences.')
    lines.append('')
    for target in ['Q2','S2']:
        lines.append(f'## {target}')
        for group,pred in [('testpattern',lambda x:x=='testpattern'),('random_gap',lambda x:x=='random_gap'),('tail',lambda x:str(x).startswith('tail'))]:
            sub=summ[(summ.target.eq(target)) & (summ.split.map(pred))]
            agg=sub.groupby(['subset','k','C'],dropna=False).agg(logloss=('logloss','mean'), delta=('delta_vs_existing','mean'), auc=('auc','mean')).reset_index().sort_values('logloss').head(5)
            lines.append(f'### {group}')
            lines.append(agg.to_string(index=False, float_format=lambda x:f'{x:.4f}'))
            lines.append('')
    (EXP/'human_hypothesis_q2s2_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('\nwrote report', EXP/'human_hypothesis_q2s2_report.md')


def main():
    EXP.mkdir(exist_ok=True)
    feat=build_features()
    eval_features(feat)

if __name__=='__main__': main()
