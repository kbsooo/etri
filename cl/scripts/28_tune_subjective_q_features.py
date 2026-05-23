#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs


def folds():
    return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']


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
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_only':
        return [c for c in all_cols if any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_')) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_'))]
    if subset=='q2x_only': return [c for c in all_cols if c.startswith('q2x_')]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='q3x_only': return [c for c in all_cols if c.startswith(('q3x_','qpatch_','qcarry_prev_q3x_','qcarry_prev_qpatch_'))]
    if subset=='q1x_only': return [c for c in all_cols if c.startswith(('q1x_','qpatch_','qcarry_prev_q1x_','qcarry_prev_qpatch_'))]
    if subset=='qstate_all': return [c for c in all_cols if c.startswith(('q3x_','q1x_','qpatch_','qcarry_'))]
    if subset=='q3x_plus_semantic':
        return sorted(set(base_subset(all_cols,'semantic_only') + base_subset(all_cols,'q3x_only')))
    if subset=='q1x_plus_sleep':
        return sorted(set(base_subset(all_cols,'q1x_only') + base_subset(all_cols,'sleep_plus_s4x') + base_subset(all_cols,'sleep_only')))
    if subset=='qstate_plus_semantic':
        return sorted(set(base_subset(all_cols,'semantic_only') + base_subset(all_cols,'qstate_all')))
    if subset=='qstate_plus_sleep_semantic':
        return sorted(set(base_subset(all_cols,'semantic_only') + base_subset(all_cols,'qstate_all') + base_subset(all_cols,'sleep_plus_s4x')))
    raise ValueError(subset)


def make_pipe(k, C, ncols):
    return Pipeline([
        ('imp',SimpleImputer(strategy='median')),
        ('sel',SelectKBest(f_classif,k=min(k,ncols))),
        ('scale',RobustScaler()),
        ('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000))
    ])


def eval_target(df, fold_defs, target, cols, k, C):
    losses=[]
    for fold in fold_defs:
        valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1).to_numpy()
        Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
        ytr=df.loc[~mask,target].astype(int).to_numpy(); yva=df.loc[mask,target].astype(int).to_numpy()
        pipe=make_pipe(k,C,len(cols))
        pipe.fit(Xtr,ytr)
        p=np.clip(pipe.predict_proba(Xva)[:,1],0.05,0.95)
        losses.append(log_loss(yva,p,labels=[0,1]))
    return float(np.mean(losses)), losses


def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    feat=con.execute(f"select * from read_parquet('{FEATURE_DIR/'model_features_v0.parquet'}')").df()
    df=train.merge(feat,on=['subject_id','lifelog_date'],how='left')
    all_cols=[c for c in feat.columns if c not in {'subject_id','lifelog_date'}]
    fold_defs=folds()

    subset_names=['semantic_only','sleep_only','no_flat_hourly','q3x_only','q1x_only','qstate_all','q3x_plus_semantic','q1x_plus_sleep','qstate_plus_semantic','qstate_plus_sleep_semantic']
    col_cache={s:valid_cols(df,base_subset(all_cols,s)) for s in subset_names + ['sleep_plus_s4x','day_flat']}
    for s, cols in col_cache.items():
        print(s, len(cols))

    tune_rows=[]; best={}
    target_grid={
        'Q1':['semantic_only','sleep_only','no_flat_hourly','q1x_only','qstate_all','q1x_plus_sleep','qstate_plus_semantic','qstate_plus_sleep_semantic'],
        'Q3':['semantic_only','sleep_only','no_flat_hourly','q3x_only','qstate_all','q3x_plus_semantic','qstate_plus_semantic','qstate_plus_sleep_semantic'],
    }
    for target, subsets in target_grid.items():
        for subset in subsets:
            cols=col_cache[subset]
            if not cols: continue
            for k in [10,20,30,50,80,120,200]:
                if k > len(cols)*2: continue
                for C in [0.0005,0.001,0.003,0.01,0.03,0.1]:
                    avg, per=eval_target(df,fold_defs,target,cols,k,C)
                    row={'target':target,'subset':subset,'k':k,'C':C,'avg_logloss':avg,
                         **{fold_defs[i]['fold_id']:per[i] for i in range(len(per))},'n_cols':len(cols)}
                    tune_rows.append(row)
        tdf=pd.DataFrame([r for r in tune_rows if r['target']==target]).sort_values('avg_logloss')
        best[target]=tdf.iloc[0].to_dict()
        print('BEST',target,best[target])

    tune=pd.DataFrame(tune_rows).sort_values(['target','avg_logloss'])
    tune.to_csv(EXPERIMENT_DIR/'probe_subjective_q_feature_tuning.csv',index=False)

    cfg={
        'Q1':(best['Q1']['subset'],int(best['Q1']['k']),float(best['Q1']['C'])),
        'Q2':('day_flat',20,0.01),
        'Q3':(best['Q3']['subset'],int(best['Q3']['k']),float(best['Q3']['C'])),
        'S1':('no_flat_hourly',20,0.10),
        'S2':('no_flat_hourly',20,0.001),
        'S3':('semantic_only',20,0.01),
        'S4':('sleep_plus_s4x',200,0.003),
    }
    rows=[]; pred_rows=[]
    for fold in fold_defs:
        valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1).to_numpy()
        scores={}; aucs={}; accs={}
        tmp=df.loc[mask,['subject_id','lifelog_date']+LABELS].copy()
        for y,(subset,k,C) in cfg.items():
            cols=col_cache[subset]
            Xtr=df.loc[~mask,cols]; Xva=df.loc[mask,cols]
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            pipe=make_pipe(k,C,len(cols))
            pipe.fit(Xtr,ytr)
            p=np.clip(pipe.predict_proba(Xva)[:,1],0.05,0.95)
            scores[y]=log_loss(yva,p,labels=[0,1])
            try: aucs[y]=roc_auc_score(yva,p)
            except Exception: aucs[y]=np.nan
            accs[y]=accuracy_score(yva,p>=0.5)
            tmp[f'pred_{y}']=p
        rows.append({'model':'target_specific_subjective_q_v3','fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS},**{f'auc_{y}':aucs[y] for y in LABELS},**{f'acc_{y}':accs[y] for y in LABELS}})
        pred_rows.append(tmp)
    res=pd.DataFrame(rows)
    res.to_csv(EXPERIMENT_DIR/'probe_target_specific_subjective_q_v3_results.csv',index=False)
    pd.concat(pred_rows).to_csv(EXPERIMENT_DIR/'probe_target_specific_subjective_q_v3_oof.csv',index=False)
    Path(EXPERIMENT_DIR/'probe_target_specific_subjective_q_v3_config.json').write_text(json.dumps(cfg,indent=2),encoding='utf-8')
    print(res.to_string(index=False))
    print('avg mean',res.mean(numeric_only=True)['mean_logloss'])
    print('target avg')
    print(res[[f'logloss_{y}' for y in LABELS]].mean().to_string())
    print('cfg',cfg)

if __name__=='__main__': main()
