#!/usr/bin/env python3
"""Rebuild competition dissection: split forensics, label semantics, validation scheme credibility.

This script intentionally prioritizes data-science structure over model tuning.
"""
from __future__ import annotations
import json, warnings, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

warnings.filterwarnings('ignore')
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; EXP=ROOT/'experiments'; OUT=ROOT/'outputs'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']; IDS=['subject_id','sleep_date','lifelog_date']
EXP.mkdir(exist_ok=True)

# Import graph utilities from existing moonshot script.
sys.path.insert(0, str(ROOT/'scripts'))
import importlib.util
spec=importlib.util.spec_from_file_location('big67', ROOT/'scripts'/'67_big_swing_all_experiments.py')
big67=importlib.util.module_from_spec(spec); spec.loader.exec_module(big67)


def clip(p): return np.clip(np.asarray(p,float),.02,.98)

def ll(y,p): return log_loss(np.asarray(y,int), clip(p), labels=[0,1])

def temporal_smooth(known, query, target, tau=14, alpha=5, future=True):
    y=known[target].astype(float).to_numpy(); g=float(np.mean(y))
    out=np.zeros(len(query),float)
    for sid,qsub in query.groupby('subject_id'):
        k=known[known.subject_id.astype(str).eq(str(sid))]
        if len(k)==0:
            out[query.index.get_indexer(qsub.index)] = g; continue
        kd=k.sleep_date.values.astype('datetime64[D]').astype(int)
        qd=qsub.sleep_date.values.astype('datetime64[D]').astype(int)
        dist=np.abs(qd[:,None]-kd[None,:]).astype(float)
        if not future:
            dist=np.where(kd[None,:] < qd[:,None], dist, np.inf)
        w=np.exp(-dist/tau); w[~np.isfinite(w)]=0
        p=(w @ k[target].astype(float).to_numpy() + alpha*g)/(w.sum(axis=1)+alpha)
        out[query.index.get_indexer(qsub.index)] = clip(p)
    return out


def make_masks(train, sample):
    # Multiple schemes to test public-likeness.
    masks=[]
    n=len(train)
    # Existing public-like masks from script 67.
    for name,mask,future in big67.make_testpattern_masks(train, sample, seeds=range(8)):
        masks.append((name,mask,future,'testpattern'))
    # Interleaved holes: choose train rows closest in within-subject rank to actual test ranks, allowing holes.
    for seed in range(4):
        rng=np.random.default_rng(100+seed); mask=np.zeros(n,bool)
        for sid,sub in train.groupby('subject_id'):
            sub=sub.sort_values('sleep_date'); tst=sample[sample.subject_id==sid].sort_values('sleep_date')
            if len(sub)<5: continue
            all_dates=pd.concat([sub[['sleep_date']].assign(kind='train'), tst[['sleep_date']].assign(kind='test')]).sort_values('sleep_date').reset_index(drop=True)
            test_fracs=all_dates.index[all_dates.kind.eq('test')].to_numpy()/max(1,len(all_dates)-1)
            ranks=np.linspace(0,1,len(sub))
            prob=np.ones(len(sub))*0.05
            if len(test_fracs):
                for f in test_fracs: prob += np.exp(-0.5*((ranks-f)/0.10)**2)
            prob=prob/prob.sum(); size=min(len(sub)-2, max(3,len(tst)))
            chosen=rng.choice(sub.index.to_numpy(), size=size, replace=False, p=prob)
            mask[train.index.get_indexer(chosen)] = True
        masks.append((f'interleaved_rank{seed}',mask,True,'interleaved_rank'))
    # Tail-only future forecasting.
    for frac in [0.25,0.36,0.45]:
        mask=np.zeros(n,bool)
        for sid,sub in train.groupby('subject_id'):
            chosen=sub.sort_values('sleep_date').tail(max(3,int(round(len(sub)*frac)))).index
            mask[train.index.get_indexer(chosen)] = True
        masks.append((f'tail{frac}',mask,False,'tail'))
    # Calendar/weekday: hold out dates with same weekday distribution as test.
    test_dow=sample.sleep_date.dt.dayofweek.value_counts(normalize=True).to_dict()
    for seed in range(3):
        rng=np.random.default_rng(200+seed); mask=np.zeros(n,bool)
        for sid,sub in train.groupby('subject_id'):
            sub=sub.sort_values('sleep_date'); tst=sample[sample.subject_id==sid]
            size=min(len(sub)-2, max(3,len(tst)))
            prob=sub.sleep_date.dt.dayofweek.map(test_dow).fillna(0.01).to_numpy(float)+0.02
            prob=prob/prob.sum(); chosen=rng.choice(sub.index.to_numpy(), size=size, replace=False, p=prob)
            mask[train.index.get_indexer(chosen)] = True
        masks.append((f'weekday{seed}',mask,True,'weekday'))
    return masks


def split_forensics(train, sample, df):
    rows=[]
    for sid, tr in train.groupby('subject_id'):
        tr=tr.sort_values('sleep_date'); te=sample[sample.subject_id==sid].sort_values('sleep_date')
        all_dates=pd.concat([tr[['sleep_date']].assign(kind='train'), te[['sleep_date']].assign(kind='test')]).sort_values('sleep_date').reset_index(drop=True)
        train_dates=tr.sleep_date.values.astype('datetime64[D]').astype(int)
        for _,r in te.iterrows():
            q=int(np.datetime64(r.sleep_date,'D').astype(int))
            before=train_dates[train_dates<q]; after=train_dates[train_dates>q]
            prev_gap=float(q-before.max()) if len(before) else np.nan
            next_gap=float(after.min()-q) if len(after) else np.nan
            any_gap=float(np.nanmin([prev_gap,next_gap])) if (len(before) or len(after)) else np.nan
            pos=int(all_dates.index[(all_dates.sleep_date==r.sleep_date)&(all_dates.kind=='test')][0])
            rows.append({'subject_id':sid,'sleep_date':r.sleep_date,'lifelog_date':r.lifelog_date,'test_pos_all':pos,'timeline_len':len(all_dates),'test_frac':pos/max(1,len(all_dates)-1),'prev_train_gap_d':prev_gap,'next_train_gap_d':next_gap,'nearest_train_gap_d':any_gap,'has_prev_train':bool(len(before)),'has_next_train':bool(len(after)),'is_beyond_train_max':bool(q>train_dates.max()),'is_before_train_min':bool(q<train_dates.min()),'weekday':r.sleep_date.dayofweek})
    det=pd.DataFrame(rows)
    det.to_csv(EXP/'rebuild_split_forensics_subject_timeline.csv',index=False)
    subj=det.groupby('subject_id').agg(test_rows=('sleep_date','count'),median_frac=('test_frac','median'),min_frac=('test_frac','min'),max_frac=('test_frac','max'),median_nearest_gap=('nearest_train_gap_d','median'),share_has_both_neighbors=('has_next_train','mean'),share_beyond_tail=('is_beyond_train_max','mean')).reset_index()
    subj.to_csv(EXP/'rebuild_split_forensics_subject_summary.csv',index=False)
    global_summary={
        'n_train':int(len(train)), 'n_test':int(len(sample)), 'n_subjects_train':int(train.subject_id.nunique()), 'n_subjects_test':int(sample.subject_id.nunique()),
        'test_rows_with_prev_train_share':float(det.has_prev_train.mean()),
        'test_rows_with_next_train_share':float(det.has_next_train.mean()),
        'test_rows_with_both_neighbors_share':float((det.has_prev_train & det.has_next_train).mean()),
        'test_rows_beyond_train_max_share':float(det.is_beyond_train_max.mean()),
        'median_test_frac':float(det.test_frac.median()),
        'median_nearest_train_gap_d':float(det.nearest_train_gap_d.median()),
        'p90_nearest_train_gap_d':float(det.nearest_train_gap_d.quantile(.9)),
        'median_prev_gap_d':float(det.prev_train_gap_d.median()),
        'median_next_gap_d':float(det.next_train_gap_d.median()),
        'weekday_dist':{str(k):float(v) for k,v in det.weekday.value_counts(normalize=True).sort_index().items()},
    }
    return det, subj, global_summary


def label_semantics(train):
    rows=[]; corr=train[LABELS].corr()
    corr.to_csv(EXP/'rebuild_label_correlation.csv')
    cond=[]
    for y in LABELS:
        vals=[]; acs=[]; flips=[]; runlens=[]; subjprev=[]
        for sid,sub in train.groupby('subject_id'):
            sub=sub.sort_values('sleep_date'); arr=sub[y].astype(int).to_numpy()
            subjprev.append(arr.mean())
            if len(arr)>1:
                flips.append(float(np.mean(np.abs(np.diff(arr)))))
                if np.std(arr[:-1])>0 and np.std(arr[1:])>0:
                    acs.append(float(np.corrcoef(arr[:-1],arr[1:])[0,1]))
                # run lengths
                cur=arr[0]; l=1
                for a in arr[1:]:
                    if a==cur: l+=1
                    else: runlens.append(l); cur=a; l=1
                runlens.append(l)
        for dow,g in train.groupby(train.sleep_date.dt.dayofweek):
            pass
        rows.append({'target':y,'global_prev':float(train[y].mean()),'subject_prev_std':float(np.std(subjprev)),'mean_flip_rate':float(np.nanmean(flips)),'mean_lag1_autocorr':float(np.nanmean(acs)) if acs else np.nan,'median_run_len':float(np.median(runlens)) if runlens else np.nan,'p90_run_len':float(np.quantile(runlens,.9)) if runlens else np.nan,'weekday_prev_std':float(train.groupby(train.sleep_date.dt.dayofweek)[y].mean().std()),'month_prev_std':float(train.groupby(train.sleep_date.dt.month)[y].mean().std())})
    sem=pd.DataFrame(rows)
    sem.to_csv(EXP/'rebuild_label_semantics_summary.csv',index=False)
    # Cross-target conditional lift.
    for a in LABELS:
        for b in LABELS:
            if a==b: continue
            pa=train[a].mean(); pb=train[b].mean(); pab=train.loc[train[a].eq(1),b].mean() if train[a].sum() else np.nan
            cond.append({'given':a,'target':b,'p_target':float(pb),'p_target_given_given1':float(pab),'lift':float(pab/pb) if pb and not np.isnan(pab) else np.nan})
    cond=pd.DataFrame(cond); cond.to_csv(EXP/'rebuild_label_conditional_lift.csv',index=False)
    # Family map heuristic.
    fam={}
    for _,r in sem.iterrows():
        if r.target=='Q3': fam[r.target]='freeze/noisy_candidate'
        elif r.mean_flip_rate<0.42 or (not np.isnan(r.mean_lag1_autocorr) and r.mean_lag1_autocorr>0.10): fam[r.target]='state_temporal_candidate'
        elif r.target in ['Q1','S4']: fam[r.target]='mechanism_alignment_candidate'
        else: fam[r.target]='feature_or_mixed_candidate'
    (EXP/'rebuild_target_family_map.json').write_text(json.dumps(fam,ensure_ascii=False,indent=2),encoding='utf-8')
    return sem,corr,cond,fam


def validation_scheme_selection(train, sample, graph_cols, feature_cols):
    masks=make_masks(train,sample)
    rows=[]
    # Evaluate primitive candidates: base, w01, w02, w03_noq3_q2w02-ish, raw graph, targetwise block.
    for name,mask,future,scheme in masks:
        if mask.sum()==0 or (~mask).sum()<50: continue
        known_mask=~mask; val_mask=mask
        known=train.loc[known_mask].copy().reset_index(drop=True)
        val=train.loc[val_mask].copy().reset_index(drop=True)
        preds={cand:val[['subject_id','sleep_date','lifelog_date']].copy().reset_index(drop=True) for cand in ['base','w01','w02','w03_noq3_q2w02','raw_graph_noq3','validated_block']}
        for y in LABELS:
            try: base=big67.fit_predict_logreg(train, feature_cols, y, known_mask, val_mask, k=80, C=.03)
            except Exception: base=np.repeat(float(known[y].mean()), len(val))
            ts=temporal_smooth(known,val,y,tau=14,alpha=5,future=future)
            try: gp=big67.graph_predict(train, known_mask, val_mask, y, graph_cols, k_same=12, k_global=45, tau=14, same_w=.75, feat_w=.25, alpha=2.5, future=future)
            except Exception: gp=ts
            preds['base'][y]=base
            preds['w01'][y]=clip(.90*base+.10*ts)
            preds['w02'][y]=clip(.80*base+.20*ts)
            preds['w03_noq3_q2w02'][y]=clip(.70*base+.30*ts)
            preds['raw_graph_noq3'][y]=gp
            preds['validated_block'][y]=base
            if y=='Q3':
                preds['w03_noq3_q2w02'][y]=base; preds['raw_graph_noq3'][y]=base; preds['validated_block'][y]=base
            if y=='Q2': preds['w03_noq3_q2w02'][y]=clip(.80*base+.20*ts)
            if y in ['Q2','S1','S2','S3']: preds['validated_block'][y]=gp
            if y in ['Q1','S4','Q3']: preds['validated_block'][y]=base
        for cand,pr in preds.items():
            losses=[]
            for y in LABELS:
                losses.append(ll(val[y],pr[y]))
                rows.append({'mask':name,'scheme':scheme,'candidate':cand,'target':y,'logloss':losses[-1],'n':int(mask.sum())})
            rows.append({'mask':name,'scheme':scheme,'candidate':cand,'target':'ALL','logloss':float(np.mean(losses)),'n':int(mask.sum())})
    res=pd.DataFrame(rows); res.to_csv(EXP/'rebuild_validation_scheme_results.csv',index=False)
    allres=res[res.target.eq('ALL')]
    summary=[]
    for (scheme,mask),g in allres.groupby(['scheme','mask']):
        pivot=g.set_index('candidate')['logloss']
        if not {'w01','w02','base','w03_noq3_q2w02','raw_graph_noq3','validated_block'}.issubset(pivot.index): continue
        public_match=int(pivot['w02'] < pivot['w01']) + int(pivot['w03_noq3_q2w02'] < pivot['w02'])
        summary.append({'scheme':scheme,'mask':mask,'n':int(g.n.iloc[0]),'base':float(pivot['base']),'w01':float(pivot['w01']),'w02':float(pivot['w02']),'w03_noq3_q2w02':float(pivot['w03_noq3_q2w02']),'raw_graph_noq3':float(pivot['raw_graph_noq3']),'validated_block':float(pivot['validated_block']),'w02_minus_w01':float(pivot['w02']-pivot['w01']),'w03_minus_w02':float(pivot['w03_noq3_q2w02']-pivot['w02']),'graph_minus_w02':float(pivot['raw_graph_noq3']-pivot['w02']),'block_minus_w02':float(pivot['validated_block']-pivot['w02']),'public_match_score':public_match})
    summ=pd.DataFrame(summary).sort_values(['public_match_score','block_minus_w02'],ascending=[False,True])
    summ.to_csv(EXP/'rebuild_validation_scheme_ranking.csv',index=False)
    byscheme=summ.groupby('scheme').agg(masks=('mask','count'),public_match_mean=('public_match_score','mean'),w02_minus_w01_mean=('w02_minus_w01','mean'),w03_minus_w02_mean=('w03_minus_w02','mean'),graph_minus_w02_mean=('graph_minus_w02','mean'),block_minus_w02_mean=('block_minus_w02','mean')).reset_index().sort_values(['public_match_mean','block_minus_w02_mean'],ascending=[False,True])
    byscheme.to_csv(EXP/'rebuild_validation_scheme_by_type.csv',index=False)
    return res,summ,byscheme


def main():
    train=pd.read_csv(DATA/'ch2026_metrics_train.csv',parse_dates=['sleep_date','lifelog_date']).assign(is_train=1)
    sample=pd.read_csv(DATA/'ch2026_submission_sample.csv',parse_dates=['sleep_date','lifelog_date']).assign(is_train=0)
    df=big67.load_base_table()
    train_full=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample_full=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    det,subj,split_summary=split_forensics(train,sample,df)
    sem,corr,cond,fam=label_semantics(train)
    graph_cols=big67.numeric_cols(train_full, contains=("sleep", "quiet", "screen", "steps", "activity", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "sslcl", "dyncl"), max_cols=500)
    feature_cols=big67.numeric_cols(train_full, contains=("sleep", "quiet", "screen", "steps", "activity", "hr_", "gps_", "app_", "wifi_", "ble_", "amb_", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "sslcl", "dyncl"), max_cols=650)
    valres,valsumm,byscheme=validation_scheme_selection(train_full,sample_full,graph_cols,feature_cols)

    # Synthesize.
    lines=[]
    lines += ['# Rebuild competition dissection report','']
    lines += ['## 1. Split forensics','',json.dumps(split_summary,ensure_ascii=False,indent=2),'']
    lines += ['### Subject split summary top/bottom','',subj.sort_values('median_frac').head(10).to_string(index=False), '', subj.sort_values('median_frac').tail(10).to_string(index=False),'']
    lines += ['## 2. Label semantics','',sem.to_string(index=False,float_format=lambda x:f'{x:.4f}'),'']
    lines += ['### Target family heuristic','',json.dumps(fam,ensure_ascii=False,indent=2),'']
    lines += ['### Label correlation','',corr.to_string(float_format=lambda x:f'{x:.3f}'),'']
    lines += ['## 3. Validation scheme credibility by type','',byscheme.to_string(index=False,float_format=lambda x:f'{x:.6f}'),'']
    lines += ['## 4. Top validation masks','',valsumm.head(20).to_string(index=False,float_format=lambda x:f'{x:.6f}'),'']
    # Targetwise component score over best schemes: use schemes with public_match_score 2 if available.
    good_masks=set(valsumm[valsumm.public_match_score.eq(valsumm.public_match_score.max())].head(10)['mask'])
    tv=valres[(valres['mask'].isin(good_masks)) & (~valres.target.eq('ALL'))].groupby(['candidate','target'])['logloss'].mean().reset_index()
    lines += ['## 5. Targetwise score on most public-like masks','',tv.pivot(index='target',columns='candidate',values='logloss').to_string(float_format=lambda x:f'{x:.6f}'),'']
    lines += ['## 6. Initial conclusions','','- Test rows are evaluated through the split forensic summary above; inspect neighbor shares and tail share before trusting graph.','- A validation scheme is credible only if it reproduces public fact w02 < w01.','- Component choice must be targetwise: graph/block should not be applied uniformly to every target.','- New submissions should be built from the targets where graph/block wins under public-like schemes, not from global blend search.']
    (EXP/'rebuild_competition_dissection_report.md').write_text('\n'.join(lines),encoding='utf-8')
    print('\n'.join(lines[:80]))
    print('\n### validation by scheme')
    print(byscheme.to_string(index=False))
    print('\n### target semantics')
    print(sem.to_string(index=False))

if __name__=='__main__': main()
