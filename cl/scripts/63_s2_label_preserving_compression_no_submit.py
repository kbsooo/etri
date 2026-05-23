#!/usr/bin/env python3
"""No-submit S2 follow-up: label-preserving compression and base blends.

The unsupervised PCA/SVD/NMF/KMeans compression in script 62 was too lossy.
This script tests whether S2 can be stabilized by:
  * fold-local SelectK -> PCA compression,
  * fold-local SelectK -> PLS supervised latent factors,
  * small blends between the official S2 base head and robust raw SelectK heads.

No submission files are written.
"""
from __future__ import annotations
import importlib.util, json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parents[1]
EXP=ROOT/'experiments'
spec=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
TARGET='S2'

class SelectPCAClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, k=64, n=16, C=0.003):
        self.k=k; self.n=n; self.C=C
    def fit(self, X, y):
        self.imp_=SimpleImputer(strategy='median')
        X0=self.imp_.fit_transform(X)
        self.sel_=SelectKBest(f_classif,k=min(self.k,X0.shape[1]))
        X1=self.sel_.fit_transform(X0,y)
        self.scale_=StandardScaler()
        X2=self.scale_.fit_transform(X1)
        self.pca_=PCA(n_components=min(self.n,X2.shape[1],max(1,len(X2)-2)),random_state=42,svd_solver='randomized')
        Z=self.pca_.fit_transform(X2)
        self.post_=RobustScaler(); Z=self.post_.fit_transform(Z)
        self.clf_=LogisticRegression(C=self.C,solver='liblinear',max_iter=1000,random_state=42)
        self.clf_.fit(Z,y)
        return self
    def predict_proba(self, X):
        X0=self.imp_.transform(X); X1=self.sel_.transform(X0); X2=self.scale_.transform(X1)
        Z=self.post_.transform(self.pca_.transform(X2))
        return self.clf_.predict_proba(Z)

class PLSLogitClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, k=64, n=8, C=0.003):
        self.k=k; self.n=n; self.C=C
    def fit(self, X, y):
        self.imp_=SimpleImputer(strategy='median')
        X0=self.imp_.fit_transform(X)
        self.sel_=SelectKBest(f_classif,k=min(self.k,X0.shape[1]))
        X1=self.sel_.fit_transform(X0,y)
        self.scale_=StandardScaler(); X2=self.scale_.fit_transform(X1)
        self.pls_=PLSRegression(n_components=min(self.n,X2.shape[1],max(1,len(X2)-2)), scale=False)
        Z=self.pls_.fit_transform(X2,y)[0]
        self.post_=RobustScaler(); Z=self.post_.fit_transform(Z)
        self.clf_=LogisticRegression(C=self.C,solver='liblinear',max_iter=1000,random_state=42)
        self.clf_.fit(Z,y)
        return self
    def predict_proba(self, X):
        X0=self.imp_.transform(X); X1=self.sel_.transform(X0); X2=self.scale_.transform(X1)
        Z=self.post_.transform(self.pls_.transform(X2))
        return self.clf_.predict_proba(Z)

def auc_safe(y,p): return roc_auc_score(y,p) if len(set(y))==2 else np.nan

def valid_cols(df,mask,cols):
    out=[]
    for c in cols:
        s=pd.to_numeric(df.loc[mask,c],errors='coerce') if c in df.columns else pd.Series(dtype=float)
        if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
    return out

def raw_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def random_gap(train, seed):
    rng=np.random.default_rng(seed+630); mask=np.zeros(len(train),bool)
    for _,g in train.groupby('subject_id'):
        idx=g.sort_values('sleep_date').index.to_numpy(); n=max(3,int(round(len(idx)*.28)))
        ranks=np.linspace(0,1,len(idx)); prob=.18+.65*ranks+np.exp(-.5*((ranks-.55)/.22)**2); prob/=prob.sum()
        chosen=rng.choice(idx,size=min(n,len(idx)-2),replace=False,p=prob)
        mask[train.index.get_indexer(chosen)]=True
    return mask

def masks(train,sample):
    out=[]; f=ROOT/'outputs/validation/folds_chrono.json'
    if f.exists():
        for fold in json.loads(f.read_text())['folds']:
            valid={(x['subject_id'],str(x['lifelog_date'])[:10]) for x in fold['valid_keys']}
            m=train.apply(lambda r:(r.subject_id,pd.Timestamp(r.lifelog_date).strftime('%Y-%m-%d')) in valid,axis=1).to_numpy()
            out.append(('chrono',fold['fold_id'],m))
    # Keep this follow-up focused/fast: enough seeds for coarse signal, not a grid-search marathon.
    for seed in range(4): out.append(('testpattern',seed,ts.make_testpattern_mask(train,sample,seed)))
    for seed in range(4): out.append(('random_gap',seed,random_gap(train,seed)))
    for frac in [.2,.3,.4,.5]: out.append((f'tail{frac:.2f}',int(frac*100),ts.make_tail_mask(train,frac=frac)))
    return out

def run():
    EXP.mkdir(exist_ok=True)
    df=ts.load_all()
    train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    all_cols=[c for c in train.columns if c not in ts.DROP]
    sources={
        'existing_no_flat': ts.base_subset(all_cols,'no_flat_hourly'),
        'combo_existing_dayflat': list(dict.fromkeys(ts.base_subset(all_cols,'no_flat_hourly')+ts.base_subset(all_cols,'day_flat'))),
    }
    model_grid=[]
    # Focus around the script-62 survivor: existing_no_flat raw k≈32, plus a small
    # set of label-preserving compression alternatives.
    for source in sources:
        for k in [20,32,48,64]:
            for C in [0.001,0.003,0.01]:
                model_grid.append((source,'raw',k,np.nan,C))
        for k in [48,64,96]:
            for n in [8,16,32]:
                if n < k:
                    for C in [0.001,0.003]:
                        model_grid.append((source,'select_pca',k,n,C))
            for n in [4,8,12]:
                if n < k:
                    for C in [0.001,0.003]:
                        model_grid.append((source,'pls_logit',k,n,C))
    rows=[]; pred_rows=[]
    for split,seed,val_mask in masks(train,sample):
        known=~val_mask; yva=train.loc[val_mask,TARGET].astype(int).to_numpy(); ytr=train.loc[known,TARGET].astype(int).to_numpy()
        pbase=ts.base_predict_for(train,known,val_mask,TARGET,None); base_loss=log_loss(yva,pbase,labels=[0,1])
        rows.append({'split':split,'seed':seed,'source':'existing_base_cfg','model':'basecfg','k':np.nan,'n':np.nan,'C':np.nan,'blend_w':0,'logloss':base_loss,'auc':auc_safe(yva,pbase),'base_loss':base_loss})
        # A small subset of stable candidates for blend diagnostics.
        blend_preds=[]
        for source,kind,k,n,C in model_grid:
            cols=valid_cols(train,known,sources[source])
            Xtr=train.loc[known,cols]; Xva=train.loc[val_mask,cols]
            try:
                if kind=='raw': model=raw_pipe(k,C,len(cols))
                elif kind=='select_pca': model=SelectPCAClassifier(k=k,n=int(n),C=C)
                else: model=PLSLogitClassifier(k=k,n=int(n),C=C)
                model.fit(Xtr,ytr); p=np.clip(model.predict_proba(Xva)[:,1],.02,.98)
            except Exception as e:
                rows.append({'split':split,'seed':seed,'source':source,'model':kind,'k':k,'n':n,'C':C,'blend_w':np.nan,'logloss':np.nan,'auc':np.nan,'base_loss':base_loss,'error':str(e)[:120]})
                continue
            loss=log_loss(yva,p,labels=[0,1]); auc=auc_safe(yva,p)
            rows.append({'split':split,'seed':seed,'source':source,'model':kind,'k':k,'n':n,'C':C,'blend_w':1.0,'logloss':loss,'auc':auc,'base_loss':base_loss})
            if (source,kind,k,n,C) in [
                ('existing_no_flat','raw',32,np.nan,0.003),('existing_no_flat','raw',32,np.nan,0.001),
                ('combo_existing_dayflat','raw',32,np.nan,0.001),('existing_no_flat','select_pca',64,16,0.003),
                ('existing_no_flat','pls_logit',64,8,0.003)]:
                blend_preds.append((source,kind,k,n,C,p))
        for source,kind,k,n,C,p in blend_preds:
            for w in [.1,.2,.3,.4,.5,.7]:
                pb=np.clip((1-w)*pbase+w*p,.02,.98)
                rows.append({'split':split,'seed':seed,'source':source,'model':kind+'_blend_base','k':k,'n':n,'C':C,'blend_w':w,'logloss':log_loss(yva,pb,labels=[0,1]),'auc':auc_safe(yva,pb),'base_loss':base_loss})
    res=pd.DataFrame(rows); res.to_csv(EXP/'s2_label_preserving_compression_results.csv',index=False)
    summarize(res)

def summarize(res):
    clean=res.dropna(subset=['logloss']).copy()
    clean['delta_vs_base']=clean.logloss-clean.base_loss
    clean['group']=clean.split.map(lambda x:'tail' if str(x).startswith('tail') else x)
    summ=clean.groupby(['group','source','model','k','n','C','blend_w'],dropna=False).agg(logloss=('logloss','mean'),delta=('delta_vs_base','mean'),auc=('auc','mean'),runs=('logloss','size')).reset_index()
    summ.to_csv(EXP/'s2_label_preserving_compression_summary.csv',index=False)
    robust=summ.groupby(['source','model','k','n','C','blend_w'],dropna=False).agg(mean_delta=('delta','mean'),worst_delta=('delta','max'),best_group_delta=('delta','min'),groups=('group','nunique'),mean_auc=('auc','mean')).reset_index().sort_values(['mean_delta','worst_delta'])
    robust.to_csv(EXP/'s2_label_preserving_compression_robust.csv',index=False)
    lines=['# S2 label-preserving compression / blend no-submit follow-up','','No submission files were created.','']
    for group in ['chrono','testpattern','random_gap','tail']:
        sub=summ[summ.group.eq(group)].sort_values(['logloss','delta']).head(15)
        if len(sub): lines += [f'## {group} best', sub.to_string(index=False,float_format=lambda x:f'{x:.4f}'),'']
    lines += ['## Robust ranking', robust.head(35).to_string(index=False,float_format=lambda x:f'{x:.4f}'),'']
    lines += ['## Best compression-only', robust[robust.model.isin(['select_pca','pls_logit'])].head(20).to_string(index=False,float_format=lambda x:f'{x:.4f}'),'']
    lines += ['## Best base blends', robust[robust.model.str.contains('blend',na=False)].head(20).to_string(index=False,float_format=lambda x:f'{x:.4f}'),'']
    out=EXP/'s2_label_preserving_compression_report.md'; out.write_text('\n'.join(lines),encoding='utf-8')
    print('wrote',EXP/'s2_label_preserving_compression_results.csv')
    print('wrote',EXP/'s2_label_preserving_compression_summary.csv')
    print('wrote',EXP/'s2_label_preserving_compression_robust.csv')
    print('wrote',out)
    print('\n'.join(lines[:140]))

if __name__=='__main__': run()
