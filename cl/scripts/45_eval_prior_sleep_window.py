#!/usr/bin/env python3
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs
warnings.filterwarnings('ignore')

KEYS=['subject_id','lifelog_date']
DROP=set(['subject_id','sleep_date','lifelog_date']+LABELS)
BASE_CFG={
    'Q1':('semantic_only',50,0.03),
    'Q2':('day_flat',20,0.01),
    'Q3':('dino_k4_cluster',10,0.30),
    'S1':('no_flat_hourly',20,0.10),
    'S2':('no_flat_hourly',20,0.001),
    'S3':('semantic_only',20,0.01),
    'S4':('sleep_plus_s4x',200,0.003),
}
S_PROXY={'S1':'pswp_rest_duration','S2':'pswp_sleep_efficiency','S3':'pswp_sleep_latency_bad','S4':'pswp_waso_bad','Q1':'pswp_sleep_quality','Q2':'pswp_fatigue_stress','Q3':'pswp_fatigue_stress'}

def folds(): return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

def valid_cols(df, cols):
    out=[]
    for c in cols:
        if c not in df.columns: continue
        s=pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1:
            out.append(c)
    return out

def base_subset(all_cols, subset):
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    if subset=='psw_all': return [c for c in all_cols if c.startswith('psw_')]
    if subset=='psw_sleep': return [c for c in all_cols if c.startswith('psw_sw_overnight') or c.startswith('psw_sw_presleep') or c.startswith('psw_sw_fullctx')]
    if subset=='pswp_proxy': return [c for c in all_cols if c.startswith('pswp_')]
    if subset.endswith('+psw_all'):
        return base_subset(all_cols, subset[:-8]) + base_subset(all_cols, 'psw_all')
    if subset.endswith('+psw_sleep'):
        return base_subset(all_cols, subset[:-10]) + base_subset(all_cols, 'psw_sleep')
    if subset.endswith('+pswp_proxy'):
        return base_subset(all_cols, subset[:-11]) + base_subset(all_cols, 'pswp_proxy')
    raise ValueError(subset)

def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def load_df():
    con=duckdb.connect(); train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv'); df=train.copy()
    paths=[FEATURE_DIR/'model_features_v0.parquet', FEATURE_DIR/'ssl_semantic_cluster_features.parquet', FEATURE_DIR/'prior_sleep_window_features_v1.parquet', FEATURE_DIR/'prior_sleep_proxy_features_v1.parquet']
    for p in paths:
        if p.exists():
            feat=con.execute(f"select * from read_parquet('{p}')").df()
            dup=[c for c in feat.columns if c in df.columns and c not in KEYS]
            if dup: feat=feat.rename(columns={c:f'{c}__{p.stem}' for c in dup})
            df=df.merge(feat,on=KEYS,how='left')
    return df

def fold_mask(df, fold):
    valid={(x['subject_id'],str(x['lifelog_date'])) for x in fold['valid_keys']}
    return df.apply(lambda r:(r['subject_id'],str(r['lifelog_date'])) in valid,axis=1).to_numpy()

def predict_oof(df, cfg, model_name):
    all_cols=[c for c in df.columns if c not in DROP]
    needed=sorted(set(v[0] for v in cfg.values()))
    col_cache={s:valid_cols(df,base_subset(all_cols,s)) for s in needed}
    pred=pd.DataFrame({k:df[k] for k in ['subject_id','lifelog_date']+LABELS})
    for y in LABELS: pred['pred_'+y]=np.nan
    rows=[]
    for fold in folds():
        mask=fold_mask(df,fold); scores={}
        for y,(subset,k,C) in cfg.items():
            cols=col_cache[subset]
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            pipe=make_pipe(k,C,len(cols)); pipe.fit(df.loc[~mask,cols],ytr)
            p=np.clip(pipe.predict_proba(df.loc[mask,cols])[:,1],0.05,0.95)
            pred.loc[mask,'pred_'+y]=p
            scores[y]=log_loss(yva,p,labels=[0,1])
        rows.append({'model':model_name,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS}})
    return pd.DataFrame(rows), pred

def calibrate_prior(train_score, train_y, score_all, bins=6, smooth=18.0):
    y=pd.Series(train_y).astype(float).reset_index(drop=True)
    s_train=pd.Series(train_score).astype(float).reset_index(drop=True)
    s_all=pd.Series(score_all).astype(float)
    gm=float(y.mean())
    corr=s_train.corr(y)
    if not np.isfinite(corr): corr=0.0
    if corr<0:
        s_train=-s_train; s_all=-s_all
    all_rank=s_all.rank(pct=True,method='average')
    train_rank=all_rank.iloc[:len(s_train)] if False else pd.Series(s_train).rank(pct=True,method='average')
    try:
        qbin=pd.qcut(train_rank,q=bins,labels=False,duplicates='drop')
    except ValueError:
        return np.full(len(s_all),gm), corr
    stats=pd.DataFrame({'bin':qbin,'y':y}).groupby('bin')['y'].agg(['mean','count'])
    stats['smooth']=(stats['mean']*stats['count']+gm*smooth)/(stats['count']+smooth)
    if len(stats)<=1: return np.full(len(s_all),gm), corr
    edges=np.quantile(train_rank, np.linspace(0,1,len(stats)+1)); edges[0]=-np.inf; edges[-1]=np.inf
    bins_all=np.digitize(all_rank.to_numpy(float), edges[1:-1], right=True)
    mp={int(k):float(v) for k,v in stats['smooth'].items()}
    prior=np.array([mp.get(int(b),gm) for b in bins_all])
    prior=0.72*prior+0.28*gm
    return np.clip(prior,0.05,0.95), corr

def eval_proxy_prior_and_blend(df, base_pred):
    rows=[]; prior_pred=base_pred[['subject_id','lifelog_date']+LABELS].copy()
    for y in LABELS: prior_pred['pred_'+y]=np.nan
    for fold in folds():
        mask=fold_mask(df,fold); scores_prior={}; scores_blend_grid={w:{} for w in [0.02,0.04,0.06,0.08,0.10,0.12,0.16,0.20]}
        for y in LABELS:
            col=S_PROXY[y]
            # Build all score vector with train rows first for calibration helper simplicity.
            train_score=pd.to_numeric(df.loc[~mask,col],errors='coerce').fillna(0).to_numpy()
            valid_score=pd.to_numeric(df.loc[mask,col],errors='coerce').fillna(0).to_numpy()
            prior_all,corr=calibrate_prior(train_score, df.loc[~mask,y].astype(int).to_numpy(), np.r_[train_score, valid_score])
            p=prior_all[len(train_score):]
            prior_pred.loc[mask,'pred_'+y]=p
            yva=df.loc[mask,y].astype(int).to_numpy()
            scores_prior[y]=log_loss(yva,p,labels=[0,1])
            b=base_pred.loc[mask,'pred_'+y].astype(float).to_numpy()
            for w in scores_blend_grid:
                if y.startswith('S') or y=='Q1':
                    pb=np.clip((1-w)*b + w*p,0.05,0.95)
                else:
                    pb=b
                scores_blend_grid[w][y]=log_loss(yva,pb,labels=[0,1])
        rows.append({'model':'rankbin_proxy_prior_only','fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores_prior.values()))),**{f'logloss_{y}':scores_prior[y] for y in LABELS}})
        for w,sc in scores_blend_grid.items():
            rows.append({'model':f'base_blend_rankbin_proxy_w{w:g}','fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(sc.values()))),**{f'logloss_{y}':sc[y] for y in LABELS}})
    return pd.DataFrame(rows), prior_pred

def main():
    ensure_dirs(); df=load_df(); rows=[]; preds={}
    candidates=[('base_v4_replicate',BASE_CFG)]
    for mode in ['psw_all','psw_sleep','pswp_proxy']:
        for k in [5,10,20,50,100,200]:
            for C in [0.001,0.003,0.01,0.03,0.1,0.3]:
                candidates.append((f'{mode}_only_k{k}_C{C}',{y:(mode,k,C) for y in LABELS}))
    for add in ['psw_all','psw_sleep','pswp_proxy']:
        for k_scale in [1,2,4]:
            for Cmul in [0.3,1,3]:
                cfg={y:(subset+'+'+add, max(k,min(400,k*k_scale)), max(0.0003,min(1.0,C*Cmul))) for y,(subset,k,C) in BASE_CFG.items()}
                candidates.append((f'base_v4_plus_{add}_ks{k_scale}_cm{Cmul}',cfg))
    best_by_target={y:[] for y in LABELS}
    for name,cfg in candidates:
        res,pred=predict_oof(df,cfg,name); rows.append(res)
        avg=res.mean(numeric_only=True); print(name,'mean',float(avg['mean_logloss']))
        if name=='base_v4_replicate': preds['base']=pred
        for y in LABELS: best_by_target[y].append((float(avg[f'logloss_{y}']),name,cfg[y]))
    proxy_res,prior_pred=eval_proxy_prior_and_blend(df,preds['base']); rows.append(proxy_res)
    allres=pd.concat(rows,ignore_index=True)
    allres.to_csv(EXPERIMENT_DIR/'probe_prior_sleep_window_results.csv',index=False)
    preds['base'].to_csv(EXPERIMENT_DIR/'probe_prior_sleep_window_base_oof.csv',index=False)
    prior_pred.to_csv(EXPERIMENT_DIR/'probe_prior_sleep_proxy_rankbin_oof.csv',index=False)
    oracle_cfg={y:sorted(lst,key=lambda x:x[0])[0][2] for y,lst in best_by_target.items()}
    oracle,opred=predict_oof(df,oracle_cfg,'prior_sleep_targetwise_best_from_sweep')
    oracle.to_csv(EXPERIMENT_DIR/'probe_prior_sleep_targetwise_best_results.csv',index=False)
    opred.to_csv(EXPERIMENT_DIR/'probe_prior_sleep_targetwise_best_oof.csv',index=False)
    (EXPERIMENT_DIR/'probe_prior_sleep_targetwise_best_config.json').write_text(json.dumps(oracle_cfg,indent=2),encoding='utf-8')
    summary=allres.groupby('model').mean(numeric_only=True).sort_values('mean_logloss')
    print('\nTOP MODELS')
    print(summary.head(25).to_string())
    print('\nORACLE',oracle_cfg)
    print(oracle.to_string(index=False))
    print('oracle avg', float(oracle.mean(numeric_only=True)['mean_logloss']))

if __name__=='__main__': main()
