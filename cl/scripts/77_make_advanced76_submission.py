#!/usr/bin/env python3
"""Create a submission candidate based on advanced76 DS findings.

Strategy:
- Start from rebuild_publiclike_router (current public-like router).
- Add a small subject-controlled temporal grammar model for Q2/Q3 (and tiny Q1).
- Add subject-debiased identity/context token model mainly for S4, lightly for Q2/Q3/Q1.
- Keep S2/S3 mostly unchanged because advanced diagnostics say they are mostly subject/static artifact.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'; OUT = ROOT / 'outputs'; EXP = ROOT / 'experiments'; FEAT = ROOT / 'features'
LABELS = ['Q1','Q2','Q3','S1','S2','S3','S4']; IDS=['subject_id','sleep_date','lifelog_date']
OUT.mkdir(exist_ok=True); EXP.mkdir(exist_ok=True)

def clip(x): return np.clip(np.asarray(x, float), .02, .98)
def logit(p):
    p=clip(p); return np.log(p/(1-p))
def sig(x): return 1/(1+np.exp(-np.asarray(x)))
def blend_logit(a,b,w): return clip(sig((1-w)*logit(a)+w*logit(b)))

def load():
    train=pd.read_csv(DATA/'ch2026_metrics_train.csv', parse_dates=['sleep_date','lifelog_date']).sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=pd.read_csv(DATA/'ch2026_submission_sample.csv', parse_dates=['sleep_date','lifelog_date']).sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    for y in LABELS: sample[y]=np.nan
    train['date']=train.lifelog_date.dt.date.astype(str); sample['date']=sample.lifelog_date.dt.date.astype(str)
    return train, sample

def temporal_features(train, sample, tau=14, alpha=5):
    """For each row, smoothed known labels by subject. Train rows use leave-one-out; test uses all train."""
    def compute(query, is_train_query):
        out=query[['subject_id','sleep_date','lifelog_date','date']].copy()
        for y in LABELS:
            vals=[]
            global_p=float(train[y].mean())
            for idx,r in query.iterrows():
                k=train[train.subject_id.astype(str).eq(str(r.subject_id))]
                if is_train_query:
                    k=k[k.index!=idx]
                if len(k)==0:
                    vals.append(global_p); continue
                dist=np.abs((k.sleep_date.values.astype('datetime64[D]').astype(int) - np.datetime64(r.sleep_date,'D').astype(int))).astype(float)
                # public-like split has both neighbors; allow future known labels as interpolation evidence
                w=np.exp(-dist/tau)
                p=(w @ k[y].astype(float).to_numpy() + alpha*global_p)/(w.sum()+alpha)
                vals.append(float(np.clip(p,.02,.98)))
            out[f'ts_{y}']=vals
        # cross-family grammar features from advanced76 temporal network
        out['ts_Q_mean']=out[[f'ts_{x}' for x in ['Q1','Q2','Q3']]].mean(axis=1)
        out['ts_S_mean']=out[[f'ts_{x}' for x in ['S1','S2','S3','S4']]].mean(axis=1)
        out['ts_Q_minus_S']=out['ts_Q_mean']-out['ts_S_mean']
        return out
    return compute(train, True), compute(sample, False)

def merge_tokens(df):
    p=FEAT/'observation_identity_token_features.parquet'
    if not p.exists(): return df
    tok=pd.read_parquet(p)
    return df.merge(tok, on=['subject_id','date'], how='left').fillna(0)

def merge_coverage(df):
    p=FEAT/'observation_coverage_features.parquet'
    if not p.exists(): return df
    cov=pd.read_parquet(p).drop(columns=['split'], errors='ignore')
    return df.merge(cov, on=['subject_id','date'], how='left').fillna(0)

def selected_token_features(target):
    p=EXP/'advanced76_subject_debiased_token_association.csv'
    if not p.exists(): return []
    deb=pd.read_csv(p)
    if len(deb)==0: return []
    # use target-specific tokens; also for S4 include strong context tokens up to p<=0.08
    d=deb[(deb.target==target) & (deb.perm_p<=0.08)].copy()
    d=d.sort_values(['perm_p','within_subject_cov'], ascending=[True,False])
    return d.token.drop_duplicates().head(30).tolist()

def train_context_temporal_models(train, sample):
    tr_ts, te_ts = temporal_features(train, sample)
    tr = train.merge(tr_ts.drop(columns=['subject_id','sleep_date','lifelog_date','date']), left_index=True, right_index=True)
    te = sample.merge(te_ts.drop(columns=['subject_id','sleep_date','lifelog_date','date']), left_index=True, right_index=True)
    tr = merge_coverage(merge_tokens(tr)); te = merge_coverage(merge_tokens(te))
    preds = {}
    cv_rows=[]
    coverage_core=[c for c in ['w_light_longest_missing_hours','hr_night_hours','usage_longest_missing_hours','pedo_record_n','pedo_active_hours'] if c in tr.columns]
    for y in LABELS:
        tok_cols=[c for c in selected_token_features(y) if c in tr.columns]
        # Target-specific DS-informed feature scope.
        if y in ['Q2','Q3']:
            cols=[f'ts_{l}' for l in LABELS]+['ts_Q_mean','ts_S_mean','ts_Q_minus_S']+tok_cols[:20]+coverage_core
            C=.18
        elif y=='Q1':
            cols=[f'ts_{l}' for l in ['Q1','Q2','Q3','S3','S4']]+['ts_Q_minus_S']+tok_cols[:15]+coverage_core
            C=.10
        elif y=='S4':
            cols=[f'ts_{l}' for l in ['S1','S2','S3','S4','Q3']]+tok_cols[:30]+coverage_core
            C=.16
        else:
            cols=[f'ts_{y}','ts_S_mean']+tok_cols[:10]+coverage_core[:2]
            C=.06
        cols=[c for c in cols if c in tr.columns]
        num_cols=cols
        X=tr[num_cols+['subject_id']]; Xte=te[num_cols+['subject_id']]; yy=train[y].astype(int).to_numpy()
        pre=ColumnTransformer([
            ('num', Pipeline([('imp',SimpleImputer(strategy='median')),('sc',StandardScaler())]), num_cols),
            ('sid', OneHotEncoder(handle_unknown='ignore'), ['subject_id']),
        ])
        pipe=Pipeline([('pre',pre),('clf',LogisticRegression(C=C,solver='liblinear',class_weight='balanced',max_iter=1000,random_state=77))])
        # OOF diagnostics only, not selection-heavy.
        oof=np.zeros(len(train)); cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=77)
        for a,b in cv.split(X, yy):
            pipe.fit(X.iloc[a], yy[a]); oof[b]=pipe.predict_proba(X.iloc[b])[:,1]
        basep=np.repeat(np.clip(yy.mean(),.02,.98), len(yy))
        cv_rows.append({'target':y,'n_features':len(num_cols),'token_features':len(tok_cols),'auc':float(roc_auc_score(yy,oof)),'logloss':float(log_loss(yy,clip(oof),labels=[0,1])),'base_logloss':float(log_loss(yy,basep,labels=[0,1])),'ll_improve_vs_prev':float(log_loss(yy,basep,labels=[0,1])-log_loss(yy,clip(oof),labels=[0,1]))})
        pipe.fit(X,yy); preds[y]=clip(pipe.predict_proba(Xte)[:,1])
    pd.DataFrame(cv_rows).to_csv(EXP/'submission_advanced76_context_temporal_model_cv.csv', index=False)
    model_df=sample[IDS].copy()
    for y in LABELS: model_df[y]=preds[y]
    model_df.to_csv(EXP/'submission_advanced76_context_temporal_model_rawpred.csv', index=False)
    return model_df

def save(name, df, refs, notes):
    for y in LABELS: df[y]=clip(df[y])
    df.to_csv(OUT/name, index=False)
    rows=[]
    for refname,ref in refs.items():
        if not df[IDS].astype(str).equals(ref[IDS].astype(str)): raise ValueError(f'id mismatch vs {refname}')
        for y in LABELS:
            delta=np.abs(df[y].to_numpy(float)-ref[y].to_numpy(float))
            rows.append({'file':name,'ref':refname,'target':y,'changed_rows':int((delta>1e-12).sum()),'mean_abs_delta':float(delta.mean()),'p95_abs_delta':float(np.quantile(delta,.95)),'max_abs_delta':float(delta.max()),'mean_prob_shift':float(df[y].mean()-ref[y].mean()),'corr':float(np.corrcoef(df[y],ref[y])[0,1]) if delta.max()>0 else 1.0})
    pd.DataFrame(rows).to_csv(EXP/f'{name[:-4]}_shift.csv', index=False)
    (EXP/f'{name[:-4]}_notes.json').write_text(json.dumps(notes|{'file':str(OUT/name)}, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    train,sample=load()
    base=pd.read_csv(OUT/'submission_rebuild_publiclike_router_prob.csv')
    antifix=pd.read_csv(OUT/'submission_rebuild_moonshot_antifix_q3w02_prob.csv')
    validated=pd.read_csv(OUT/'submission_moonshot_validated_block_sharp_prob.csv')
    model=train_context_temporal_models(train,sample)
    refs={'publiclike_router':base,'moonshot_antifix_q3w02':antifix,'validated_block_sharp':validated,'advanced76_raw_model':model}
    c=base.copy()
    # DS-informed target weights. Q3/Q2 temporal grammar real; S4 context real; S2/S3 barely touched.
    weights={'Q1':0.10,'Q2':0.18,'Q3':0.30,'S1':0.05,'S2':0.04,'S3':0.04,'S4':0.24}
    for y,w in weights.items():
        c[y]=blend_logit(base[y], model[y], w)
    # Extra: keep Q3 closer to temporal version already in antifix/publiclike, but allow model direction.
    # S4 context can be high-variance, cap per-row move for safer submit.
    for y,cap in [('S4',0.12),('Q3',0.10),('Q2',0.08),('Q1',0.06),('S2',0.04),('S3',0.04),('S1',0.04)]:
        diff=c[y].to_numpy(float)-base[y].to_numpy(float)
        c[y]=clip(base[y].to_numpy(float)+np.clip(diff,-cap,cap))
    save('submission_advanced76_context_temporal_prob.csv', c, refs, {
        'family':'advanced76_context_temporal_ds',
        'description':'Publiclike router plus small subject-controlled temporal grammar/context-token calibration from advanced76 diagnostics.',
        'rationale':'Q2/Q3 get temporal-grammar blend; S4 gets subject-debiased WiFi/BLE/app context blend; S2/S3 are nearly frozen because diagnostics show subject/static artifact risk.',
        'weights':weights,
        'caps':{'S4':0.12,'Q3':0.10,'Q2':0.08,'Q1':0.06,'S2':0.04,'S3':0.04,'S1':0.04}
    })
    print(json.dumps({'output':str(OUT/'submission_advanced76_context_temporal_prob.csv'),'notes':str(EXP/'submission_advanced76_context_temporal_prob_notes.json')}, indent=2))

if __name__=='__main__': main()
